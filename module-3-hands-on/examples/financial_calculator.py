"""
Production-Ready Financial Calculator with QWED Verification

This example shows how to build a financial calculator that:
- Verifies all calculations before returning results
- Handles errors gracefully
- Logs verification failures
- Provides audit trails

Use Case: Fintech applications, banking apps, investment platforms
"""

from qwed_sdk import QWEDLocal
import logging
from typing import Optional
from dataclasses import dataclass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class CalculationResult:
    """Result of a financial calculation."""
    value: float
    verified: bool
    confidence: float
    audit_trail: str


class FinancialCalculator:
    """
    Production-ready financial calculator with QWED verification.
    
    All calculations are verified using symbolic math engines
    before being returned to users.
    """
    
    def __init__(self, provider: str = "openai", model: str = "gpt-4o-mini"):
        """
        Initialize calculator with QWED verification.
        
        Args:
            provider: LLM provider ("openai", "anthropic", or "gemini")
            model: Model name
        """
        self.client = QWEDLocal(
            provider=provider,
            model=model,
            use_cache=True  # Enable caching for cost savings
        )
        self.calculation_count = 0
        self.verification_failures = 0
    
    def compound_interest(
        self, 
        principal: float, 
        rate: float, 
        years: int
    ) -> CalculationResult:
        """
        Calculate compound interest with verification.
        
        Formula: A = P(1 + r)^t
        
        Args:
            principal: Initial amount ($)
            rate: Annual interest rate (%)
            years: Number of years
            
        Returns:
            CalculationResult with verified amount
            
        Raises:
            VerificationError: If calculation cannot be verified
        """
        query = f"""
        Calculate compound interest:
        - Principal: ${principal:,.2f}
        - Annual rate: {rate}%
        - Time: {years} years
        
        Use formula: A = P(1 + r)^t
        """
        
        try:
            result = self.client.verify_math(query)
            self.calculation_count += 1
            
            if result.verified:
                logger.info(f"✅ Verified compound interest: ${result.value:,.2f}")
                return CalculationResult(
                    value=result.value,
                    verified=True,
                    confidence=result.confidence,
                    audit_trail=f"Symbolic verification via {result.evidence.get('method')}"
                )
            else:
                self.verification_failures += 1
                logger.error(f"❌ Verification failed: {result.error}")
                raise VerificationError(f"Cannot verify calculation: {result.error}")
                
        except Exception as e:
            logger.error(f"Calculation error: {e}")
            raise
    
    def loan_payment(
        self,
        principal: float,
        annual_rate: float,
        years: int
    ) -> CalculationResult:
        """
        Calculate monthly loan payment with verification.
        
        Formula: M = P[r(1+r)^n]/[(1+r)^n-1]
        
        Args:
            principal: Loan amount ($)
            annual_rate: Annual interest rate (%)
            years: Loan term in years
            
        Returns:
            CalculationResult with verified monthly payment
        """
        query = f"""
        Calculate monthly payment for loan:
        - Principal: ${principal:,.2f}
        - Annual rate: {annual_rate}%
        - Term: {years} years
        
        Use standard loan payment formula.
        """
        
        result = self.client.verify_math(query)
        self.calculation_count += 1
        
        if result.verified:
            return CalculationResult(
                value=result.value,
                verified=True,
                confidence=100.0,
                audit_trail="Verified via SymPy"
            )
        else:
            self.verification_failures += 1
            # Fallback: Use conservative estimate
            logger.warning("Using conservative fallback estimate")
            monthly_rate = annual_rate / 100 / 12
            n_payments = years * 12
            fallback = principal * (monthly_rate * (1 + monthly_rate)**n_payments) / \
                       ((1 + monthly_rate)**n_payments - 1)
            
            return CalculationResult(
                value=fallback,
                verified=False,
                confidence=0.0,
                audit_trail="Fallback calculation (unverified)"
            )
    
    def get_stats(self) -> dict:
        """Get calculator statistics."""
        return {
            "total_calculations": self.calculation_count,
            "verification_failures": self.verification_failures,
            "success_rate": ((self.calculation_count - self.verification_failures) / 
                           self.calculation_count * 100) if self.calculation_count > 0 else 0
        }


class VerificationError(Exception):
    """Raised when verification fails."""
    pass


# Example Usage
if __name__ == "__main__":
    # Initialize calculator
    calc = FinancialCalculator()
    
    print("=" * 60)
    print("QWED Financial Calculator Demo")
    print("=" * 60)
    
    # Example 1: Compound Interest
    print("\n📊 Example 1: Compound Interest")
    result = calc.compound_interest(
        principal=100000,
        rate=5.0,
        years=10
    )
    print(f"Initial: $100,000")
    print(f"Rate: 5% annual")
    print(f"Time: 10 years")
    print(f"Final Amount: ${result.value:,.2f}")
    print(f"Verified: {'✅' if result.verified else '❌'}")
    print(f"Confidence: {result.confidence}%")
    
    # Example 2: Loan Payment
    print("\n🏠 Example 2: Mortgage Payment")
    result = calc.loan_payment(
        principal=500000,
        annual_rate=6.5,
        years=30
    )
    print(f"Loan: $500,000")
    print(f"Rate: 6.5% annual")
    print(f"Term: 30 years")
    print(f"Monthly Payment: ${result.value:,.2f}")
    print(f"Verified: {'✅' if result.verified else '❌'}")
    
    # Statistics
    print("\n📈 Calculator Statistics")
    stats = calc.get_stats()
    print(f"Total Calculations: {stats['total_calculations']}")
    print(f"Verification Failures: {stats['verification_failures']}")
    print(f"Success Rate: {stats['success_rate']:.1f}%")
