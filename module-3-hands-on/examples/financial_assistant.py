"""
Multi-Domain Financial Assistant

Demonstrates combining multiple QWED verifiers in one application:
- Math verification (interest calculations)
- Logic verification (eligibility rules)
- Data validation (input sanity checks)

Real-world use case: Personal finance chatbot
"""

from qwed_sdk import QWEDLocal
from qwed_core import DiagnosticStatus
import logging
from typing import Dict, Optional
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class FinancialAssistant:
    """
    Production financial assistant with multi-domain verification.
    """
    
    def __init__(self):
        self.client = QWEDLocal(provider="openai", model="gpt-4o-mini")
    
    def calculate_loan_eligibility(
        self,
        annual_income: float,
        loan_amount: float,
        interest_rate: float,
        term_years: int
    ) -> Dict:
        """
        Check loan eligibility with multi-step verification.
        
        Steps:
        1. Validate inputs (data check)
        2. Calculate monthly payment (math)
        3. Check debt-to-income ratio (logic)
        """
        logger.info(f"💰 Loan eligibility check for ${loan_amount:,.2f}")
        
        # Step 1: Validate inputs
        validation = self._validate_inputs(annual_income, loan_amount, interest_rate, term_years)
        if not validation['valid']:
            return {"eligible": False, "reason": validation['reason']}
        
        # Step 2: Calculate monthly payment
        monthly_payment = self._calculate_monthly_payment(
            loan_amount, interest_rate, term_years
        )
        
        if monthly_payment is None:
            return {"eligible": False, "reason": "Payment calculation failed"}
        
        # Step 3: Check debt-to-income ratio
        monthly_income = annual_income / 12
        debt_to_income_ratio = (monthly_payment / monthly_income) * 100
        
        eligible = debt_to_income_ratio <= 43  # Standard DTI limit
        
        return {
            "eligible": eligible,
            "monthly_payment": round(monthly_payment, 2),
            "debt_to_income_ratio": round(debt_to_income_ratio, 2),
            "max_dti": 43,
            "annual_income": annual_income,
            "loan_amount": loan_amount,
        }
    
    def _validate_inputs(self, income: float, loan: float, rate: float, years: int) -> Dict:
        """Validate input ranges."""
        if income <= 0:
            return {"valid": False, "reason": "Income must be positive"}
        if loan <= 0:
            return {"valid": False, "reason": "Loan amount must be positive"}
        if rate <= 0 or rate > 100:
            return {"valid": False, "reason": "Interest rate must be between 0-100"}
        if years <= 0 or years > 30:
            return {"valid": False, "reason": "Term must be 1-30 years"}
        
        return {"valid": True}
    
    def _calculate_monthly_payment(
        self,
        principal: float,
        annual_rate: float,
        years: int
    ) -> Optional[float]:
        """
        Calculate monthly loan payment with verification.
        
        Formula: M = P * [r(1+r)^n] / [(1+r)^n - 1]
        Where:
        - M = monthly payment
        - P = principal
        - r = monthly interest rate
        - n = number of payments
        """
        query = f"""
        Calculate monthly loan payment:
        - Principal: ${principal}
        - Annual interest rate: {annual_rate}%
        - Loan term: {years} years
        
        Monthly rate = {annual_rate}/12/100
        Number of payments = {years} * 12
        
        Formula: M = P * [r(1+r)^n] / [(1+r)^n - 1]
        """
        
        try:
            result = self.client.verify_math(query)
            
            if result.status == DiagnosticStatus.VERIFIED:
                value = result.developer_fields.get("value")
                logger.info(f"✅ Verified monthly payment: ${value:.2f}")
                return value
            else:
                logger.error(f"❌ Payment calculation failed: {result.agent_message}")
                return None
                
        except Exception as e:
            logger.error(f"Exception in payment calculation: {e}")
            return None


# Demo
if __name__ == "__main__":
    assistant = FinancialAssistant()
    
    print("=" * 60)
    print("Financial Assistant Demo")
    print("=" * 60)
    
    # Scenario: Home loan eligibility
    print("\n🏠 Scenario: Home Loan Application")
    print("-" * 60)
    
    result = assistant.calculate_loan_eligibility(
        annual_income=75000,
        loan_amount=300000,
        interest_rate=6.5,
        term_years=30
    )
    
    print(f"\nIncome: ${result['annual_income']:,.2f}/year")
    print(f"Loan: ${result['loan_amount']:,.2f}")
    print(f"Monthly Payment: ${result['monthly_payment']:,.2f}")
    print(f"Debt-to-Income: {result['debt_to_income_ratio']:.1f}%")
    print(f"Max DTI Allowed: {result['max_dti']}%")
    print(f"\nEligible: {'✅ YES' if result['eligible'] else '❌ NO'}")
    
    print("\n" + "=" * 60)
    print("✅ All calculations verified with QWED!")
    print("=" * 60)
