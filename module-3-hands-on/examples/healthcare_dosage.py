"""
Healthcare dosage example with fail-closed verification and audit logging.

This demo is intentionally strict:
- all patient math must be verified before a dosage is returned
- unit mistakes are treated as safety failures
- unverifiable outputs escalate to human review instead of downgraded confidence
"""

from datetime import datetime
import logging
from typing import Dict, Optional

from qwed_sdk import QWEDLocal


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class SafetyError(Exception):
    """Raised when a dosage cannot be verified safely."""


def unsafe_dosage_calculator(weight_kg: float, drug: str) -> float:
    """
    Dangerous path shown for contrast only.

    This function represents what happens when a probabilistic answer is trusted
    without a deterministic unit-aware verification step.
    """
    logger.warning("UNSAFE MODE: No verification for %s", drug)
    hallucinated_grams = weight_kg * 20
    logger.error("Unsafe output: %sg interpreted as a prescribed dose", hallucinated_grams)
    return hallucinated_grams


class HIPAACompliantDosageCalculator:
    """Pediatric dosage calculator with masking and fail-closed verification."""

    def __init__(self):
        self.client = QWEDLocal(
            provider="openai",
            model="gpt-4o-mini",
            mask_pii=True,
            pii_entities=[
                "PERSON",
                "DATE_TIME",
                "US_SSN",
                "MEDICAL_LICENSE",
            ],
        )
        self.safety_log = []

    def calculate_pediatric_dose(
        self,
        patient_name: str,
        weight_kg: float,
        drug_name: str,
        dosage_per_kg_mg: float,
        max_dosage_mg: Optional[float] = None,
    ) -> Dict:
        """
        Calculate and verify a pediatric dosage in milligrams.

        Raises `SafetyError` if the dosage cannot be deterministically verified.
        """
        logger.info(
            "Processing dosage for %s: %s, %skg, %smg/kg",
            patient_name,
            drug_name,
            weight_kg,
            dosage_per_kg_mg,
        )

        query = f"""
        Calculate pediatric dosage:
        - Drug: {drug_name}
        - Patient weight: {weight_kg} kilograms
        - Dosage rate: {dosage_per_kg_mg} milligrams per kilogram

        Formula: total_mg = weight_kg * dosage_mg_per_kg

        Return the final answer in milligrams only.
        """

        try:
            result = self.client.verify_math(query)
            if not result.verified:
                self._log_safety_event(
                    patient=patient_name,
                    drug=drug_name,
                    weight=weight_kg,
                    dosage=None,
                    verified=False,
                    error=result.error,
                )
                raise SafetyError(
                    f"Dosage for {drug_name} is unverifiable: {result.error}. "
                    "Escalate to pharmacist or clinician review."
                )

            calculated_dosage_mg = result.value
            capped = False
            if max_dosage_mg is not None and calculated_dosage_mg > max_dosage_mg:
                logger.warning(
                    "Calculated dose %smg exceeds max %smg; capping to safe maximum",
                    calculated_dosage_mg,
                    max_dosage_mg,
                )
                calculated_dosage_mg = max_dosage_mg
                capped = True

            logger.info(
                "Verified dosage: %smg via %s",
                calculated_dosage_mg,
                result.evidence.get("method", "symbolic engine"),
            )

            audit_info = self._log_safety_event(
                patient=patient_name,
                drug=drug_name,
                weight=weight_kg,
                dosage=calculated_dosage_mg,
                verified=True,
                pii_masked=result.evidence.get("pii_masked", {}),
            )

            return {
                "dosage_mg": calculated_dosage_mg,
                "verified": True,
                "verification_status": "VERIFIED",
                "capped": capped,
                "max_dosage_mg": max_dosage_mg,
                "pii_detected": result.evidence.get("pii_masked", {}).get("pii_detected", 0),
                "audit_id": audit_info["audit_id"],
                "timestamp": audit_info["timestamp"],
                "safety_status": "APPROVED",
            }
        except SafetyError:
            raise
        except Exception as exc:
            self._log_safety_event(
                patient=patient_name,
                drug=drug_name,
                weight=weight_kg,
                dosage=None,
                verified=False,
                error=str(exc),
            )
            raise SafetyError(f"Critical error in dosage calculation: {exc}") from exc

    def _log_safety_event(
        self,
        patient: str,
        drug: str,
        weight: float,
        dosage: Optional[float],
        verified: bool,
        pii_masked: Optional[Dict] = None,
        error: Optional[str] = None,
    ) -> Dict:
        """Create a local audit trail entry."""
        audit_event = {
            "audit_id": f"MED-{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
            "timestamp": datetime.now().isoformat(),
            "patient": patient,
            "drug": drug,
            "weight_kg": weight,
            "calculated_dosage_mg": dosage,
            "verified": verified,
            "pii_masked": pii_masked,
            "error": error,
        }
        self.safety_log.append(audit_event)
        return audit_event


if __name__ == "__main__":
    patient_name = "Emma Rodriguez"
    weight_kg = 18.0
    drug = "Amoxicillin"
    dosage_rate = 20
    max_dose = 500

    print("=" * 70)
    print("MEDICAL AI SAFETY DEMONSTRATION")
    print("=" * 70)

    print("\nPATH 1: WITHOUT VERIFICATION (UNSAFE)")
    unsafe = unsafe_dosage_calculator(weight_kg, drug)
    print(f"Unsafe result: {unsafe}g")
    print("Expected deterministic result: 360mg (0.36g)")

    print("\nPATH 2: WITH QWED VERIFICATION (SAFE)")
    calculator = HIPAACompliantDosageCalculator()
    try:
        safe_result = calculator.calculate_pediatric_dose(
            patient_name=patient_name,
            weight_kg=weight_kg,
            drug_name=drug,
            dosage_per_kg_mg=dosage_rate,
            max_dosage_mg=max_dose,
        )
        print(f"Dosage: {safe_result['dosage_mg']}mg")
        print(f"Verified: {safe_result['verified']}")
        print(f"Verification Status: {safe_result['verification_status']}")
        print(f"Capped: {safe_result['capped']}")
        print(f"Audit ID: {safe_result['audit_id']}")
        print(f"Safety Status: {safe_result['safety_status']}")
    except SafetyError as exc:
        print(f"Blocked for human review: {exc}")

    print("\nLesson:")
    print("- Unit confusion is a safety failure, not a lower-confidence result.")
    print("- Unsupported or unverifiable outputs must block and escalate.")
    print("- In medical AI, verification is a safety boundary, not a UX improvement.")
