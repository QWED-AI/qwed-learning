"""
HIPAA-Compliant Healthcare Dosage Calculator

Demonstrates:
- PII masking for patient data
- Critical medication dosage calculation with verification
- Audit trail requirements
- Error handling for safety

Use Case: Hospital EHR systems, pharmacy apps, telehealth platforms
"""

from qwed_sdk import QWEDLocal
import logging
from datetime import datetime
from typing import Dict, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SafetyError(Exception):
    """Raised when dosage calculation cannot be verified - safety critical!"""
    pass


class HIPAACompliantDosageCalculator:
    """
    Healthcare dosage calculator with HIPAA-compliant PII masking.
    
    All patient data is masked before being sent to LLM.
    All dosages are verified using symbolic math.
    """
    
    def __init__(self):
        """Initialize with PII masking enabled."""
        self.client = QWEDLocal(
            provider="openai",
            model="gpt-4o-mini",
            mask_pii=True,  # HIPAA compliance
            pii_entities=[
                "PERSON",           # Patient names
                "DATE_TIME",        # Birth dates, appointment times
                "LOCATION",         # Addresses
                "US_SSN",          # Social security numbers
                "PHONE_NUMBER",     # Contact info
                "EMAIL_ADDRESS",
                "MEDICAL_LICENSE",  # Provider IDs
                "NRP"              # National provider numbers
            ]
        )
        self.audit_log = []
    
    def calculate_weight_based_dosage(
        self,
        patient_name: str,
        weight_kg: float,
        drug_name: str,
        dosage_per_kg: float,
        max_dosage: Optional[float] = None
    ) -> Dict:
        """
        Calculate medication dosage based on patient weight.
        
        Args:
            patient_name: Patient full name (will be masked)
            weight_kg: Patient weight in kilograms
            drug_name: Medication name
            dosage_per_kg: Dosage in mg per kg
            max_dosage: Optional maximum dosage cap (mg)
            
        Returns:
            Dict with dosage, verification status, and audit info
            
        Raises:
            SafetyError: If dosage cannot be verified
        """
        # Build query (PII will be automatically masked)
        query = f"""
        Calculate medication dosage for patient: {patient_name}
        
        Weight: {weight_kg} kg
        Drug: {drug_name}
        Dosage rate: {dosage_per_kg} mg/kg
        
        Calculate: total dosage in mg
        """
        
        try:
            # Verify calculation
            result = self.client.verify_math(query)
            
            if not result.verified:
                # CRITICAL: Cannot proceed without verification
                logger.error(f"❌ SAFETY ERROR: Cannot verify dosage for {drug_name}")
                self._log_audit_event(
                    patient_name=patient_name,
                    drug=drug_name,
                    weight=weight_kg,
                    dosage=None,
                    verified=False,
                    error=result.error
                )
                raise SafetyError(
                    f"Cannot verify {drug_name} dosage calculation. "
                    f"Error: {result.error}. "
                    "Manual calculation required."
                )
            
            calculated_dosage = result.value
            
            # Check against maximum dosage if specified
            if max_dosage and calculated_dosage > max_dosage:
                logger.warning(f"⚠ Calculated dosage ({calculated_dosage}mg) exceeds max ({max_dosage}mg)")
                calculated_dosage = max_dosage
                capped = True
            else:
                capped = False
            
            # Log successful calculation
            logger.info(f"✅ Verified {drug_name} dosage: {calculated_dosage}mg")
            
            # Audit trail
            audit_info = self._log_audit_event(
                patient_name=patient_name,
                drug=drug_name,
                weight=weight_kg,
                dosage=calculated_dosage,
                verified=True,
                pii_masked=result.evidence.get('pii_masked', {})
            )
            
            return {
                "dosage_mg": calculated_dosage,
                "verified": True,
                "confidence": 100.0,
                "capped": capped,
                "max_dosage": max_dosage,
                "pii_detected": result.evidence.get('pii_masked', {}).get('pii_detected', 0),
                "audit_id": audit_info['audit_id'],
                "timestamp": audit_info['timestamp']
            }
            
        except SafetyError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error in dosage calculation: {e}")
            self._log_audit_event(
                patient_name=patient_name,
                drug=drug_name,
                weight=weight_kg,
                dosage=None,
                verified=False,
                error=str(e)
            )
            raise SafetyError(f"Dosage calculation failed: {e}")
    
    def _log_audit_event(
        self,
        patient_name: str,
        drug: str,
        weight: float,
        dosage: Optional[float],
        verified: bool,
        pii_masked: Optional[Dict] = None,
        error: Optional[str] = None
    ) -> Dict:
        """
        Log audit event (compliant with HIPAA audit requirements).
        
        Note: Patient name is logged but NOT sent to LLM (masked before that).
        """
        audit_event = {
            "audit_id": f"AUD-{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
            "timestamp": datetime.now().isoformat(),
            "patient": patient_name,  # OK to log locally (not sent to LLM)
            "drug": drug,
            "weight_kg": weight,
            "calculated_dosage_mg": dosage,
            "verified": verified,
            "pii_masked": pii_masked,
            "error": error
        }
        
        self.audit_log.append(audit_event)
        
        # In production: Write to secure database
        logger.info(f"Audit event logged: {audit_event['audit_id']}")
        
        return audit_event
    
    def get_audit_trail(self, patient_name: Optional[str] = None) -> list:
        """Retrieve audit trail (filtered by patient if specified)."""
        if patient_name:
            return [e for e in self.audit_log if e['patient'] == patient_name]
        return self.audit_log


# Example Usage
if __name__ == "__main__":
    calc = HIPAACompliantDosageCalculator()
    
    print("=" * 60)
    print("HIPAA-Compliant Dosage Calculator Demo")
    print("=" * 60)
    
    # Example 1: Pediatric dosage
    print("\n💊 Example 1: Pediatric Antibiotic")
    try:
        result = calc.calculate_weight_based_dosage(
            patient_name="John Doe",  # Will be masked as <PERSON>
            weight_kg=25.0,
            drug_name="Amoxicillin",
            dosage_per_kg=20,  # 20mg/kg
            max_dosage=500  # Cap at 500mg
        )
        
        print(f"Patient: [MASKED - PII detected: {result['pii_detected']}]")
        print(f"Dosage: {result['dosage_mg']}mg")
        print(f"Verified: {'✅' if result['verified'] else '❌'}")
        print(f"Capped: {'Yes' if result['capped'] else 'No'}")
        print(f"Audit ID: {result['audit_id']}")
        
    except SafetyError as e:
        print(f"❌ SAFETY ERROR: {e}")
    
    # Example 2: Adult dosage
    print("\n💊 Example 2: Adult Pain Medication")
    try:
        result = calc.calculate_weight_based_dosage(
            patient_name="Jane Smith",
            weight_kg=70.0,
            drug_name="Ibuprofen",
            dosage_per_kg=10,  # 10mg/kg
            max_dosage=800  # Cap at 800mg
        )
        
        print(f"Patient: [MASKED]")
        print(f"Dosage: {result['dosage_mg']}mg")
        print(f"Verified: ✅")
        print(f"Audit ID: {result['audit_id']}")
        
    except SafetyError as e:
        print(f"❌ SAFETY ERROR: {e}")
    
    # Show audit trail
    print("\n📋 Audit Trail (last 5 events)")
    for event in calc.get_audit_trail()[-5:]:
        print(f"  {event['timestamp']}: {event['drug']} - {'✅' if event['verified'] else '❌'}")
