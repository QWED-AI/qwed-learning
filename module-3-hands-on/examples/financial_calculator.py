"""
Production-ready financial calculator with fail-closed verification.

This example demonstrates the QWED mindset for trust-critical math:
- deterministic verification happens before a value is returned
- unsupported or unverifiable calculations are blocked
- simplified or heuristic outputs are never normalized into "verified"
"""

from dataclasses import dataclass
import logging

from qwed_sdk import QWEDLocal


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VerificationError(Exception):
    """Raised when a financial calculation cannot be verified."""


@dataclass
class CalculationResult:
    """Deterministic result for a financial calculation."""

    value: float
    verified: bool
    status: str
    audit_trail: str


class FinancialCalculator:
    """
    Financial calculator that fails closed on unverifiable results.

    The calculator never returns a fallback estimate in place of proof.
    """

    def __init__(self, provider: str = "openai", model: str = "gpt-4o-mini"):
        self.client = QWEDLocal(
            provider=provider,
            model=model,
            use_cache=True,
        )
        self.calculation_count = 0
        self.blocked_calculations = 0

    def compound_interest(self, principal: float, rate: float, years: int) -> CalculationResult:
        """
        Calculate compound interest with deterministic verification.

        Formula: A = P(1 + r)^t
        """
        query = f"""
        Calculate compound interest:
        - Principal: ${principal:,.2f}
        - Annual rate: {rate}%
        - Time: {years} years

        Use formula: A = P(1 + r)^t
        """

        result = self.client.verify_math(query)
        self.calculation_count += 1

        if not result.verified:
            self.blocked_calculations += 1
            logger.error("Compound-interest verification failed: %s", result.error)
            raise VerificationError(
                f"Compound-interest calculation is unverifiable: {result.error}. "
                "Block the response and escalate for manual review."
            )

        logger.info("Verified compound interest: $%.2f", result.value)
        return CalculationResult(
            value=result.value,
            verified=True,
            status="VERIFIED",
            audit_trail=f"Deterministic math verification via {result.evidence.get('method', 'symbolic engine')}",
        )

    def loan_payment(self, principal: float, annual_rate: float, years: int) -> CalculationResult:
        """
        Calculate a monthly loan payment with deterministic verification.

        Formula: M = P[r(1+r)^n]/[(1+r)^n-1]
        """
        query = f"""
        Calculate monthly payment for a loan:
        - Principal: ${principal:,.2f}
        - Annual rate: {annual_rate}%
        - Term: {years} years

        Use the standard amortizing loan payment formula.
        """

        result = self.client.verify_math(query)
        self.calculation_count += 1

        if not result.verified:
            self.blocked_calculations += 1
            logger.error("Loan-payment verification failed: %s", result.error)
            raise VerificationError(
                f"Loan-payment calculation is unverifiable: {result.error}. "
                "Do not substitute a fallback value."
            )

        logger.info("Verified loan payment: $%.2f", result.value)
        return CalculationResult(
            value=result.value,
            verified=True,
            status="VERIFIED",
            audit_trail=f"Deterministic math verification via {result.evidence.get('method', 'symbolic engine')}",
        )

    def get_stats(self) -> dict:
        """Return operational statistics for this calculator."""
        verified_calculations = self.calculation_count - self.blocked_calculations
        return {
            "total_calculations": self.calculation_count,
            "verified_calculations": verified_calculations,
            "blocked_calculations": self.blocked_calculations,
            "verification_success_rate": (
                verified_calculations / self.calculation_count * 100
            )
            if self.calculation_count
            else 0.0,
        }


if __name__ == "__main__":
    calc = FinancialCalculator()

    print("=" * 60)
    print("QWED Financial Calculator Demo")
    print("=" * 60)

    print("\nExample 1: Compound Interest")
    compound = calc.compound_interest(principal=100000, rate=5.0, years=10)
    print(f"Final Amount: ${compound.value:,.2f}")
    print(f"Verified: {compound.verified}")
    print(f"Status: {compound.status}")
    print(f"Audit Trail: {compound.audit_trail}")

    print("\nExample 2: Mortgage Payment")
    mortgage = calc.loan_payment(principal=500000, annual_rate=6.5, years=30)
    print(f"Monthly Payment: ${mortgage.value:,.2f}")
    print(f"Verified: {mortgage.verified}")
    print(f"Status: {mortgage.status}")
    print(f"Audit Trail: {mortgage.audit_trail}")

    print("\nCalculator Statistics")
    stats = calc.get_stats()
    print(f"Total Calculations: {stats['total_calculations']}")
    print(f"Blocked Calculations: {stats['blocked_calculations']}")
    print(f"Verification Success Rate: {stats['verification_success_rate']:.1f}%")
