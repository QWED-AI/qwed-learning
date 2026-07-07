"""
Production-ready financial calculator with fail-closed verification.

This example demonstrates the QWED mindset for trust-critical math:
- deterministic verification happens before a value is returned
- unsupported or unverifiable calculations are blocked
- only VERIFIED results with proof_ref are authoritative for control flow
"""

import logging

from qwed_sdk import QWEDLocal
from qwed_core import DiagnosticResult, DiagnosticStatus, compute_proof_ref


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VerificationError(Exception):
    """Raised when a financial calculation cannot be verified."""


class FinancialCalculator:
    """
    Financial calculator that fails closed on unverifiable results.

    The calculator never returns a fallback estimate in place of proof.
    Every VERIFIED result carries a proof_ref binding the verdict to evidence.
    """

    def __init__(self, provider: str = "openai", model: str = "gpt-4o-mini"):
        self.client = QWEDLocal(
            provider=provider,
            model=model,
            use_cache=True,
        )
        self.calculation_count = 0
        self.blocked_calculations = 0

    @staticmethod
    def _validate_financial_inputs(principal: float, rate: float, years: int) -> None:
        """Reject domain-invalid business inputs before verification."""
        if principal < 0:
            raise ValueError("principal must be >= 0")
        if rate < 0:
            raise ValueError("rate must be >= 0")
        if not isinstance(years, int) or years <= 0:
            raise ValueError("years must be a positive integer")

    def compound_interest(self, principal: float, rate: float, years: int) -> DiagnosticResult:
        """
        Calculate compound interest with deterministic verification.

        Formula: A = P(1 + r)^t
        Returns DiagnosticResult with proof_ref on VERIFIED.
        """
        self._validate_financial_inputs(principal, rate, years)
        query = f"""
        Calculate compound interest:
        - Principal: ${principal:,.2f}
        - Annual rate: {rate}%
        - Time: {years} years

        Use formula: A = P(1 + r)^t
        """

        result = self.client.verify_math(query)
        self.calculation_count += 1

        if result.status != DiagnosticStatus.VERIFIED:
            self.blocked_calculations += 1
            logger.error("Compound-interest verification failed: %s", result.agent_message)
            raise VerificationError(
                f"Compound-interest calculation is unverifiable: {result.agent_message}. "
                "Block the response and escalate for manual review."
            )

        value = result.developer_fields.get("value")
        logger.info("Verified compound interest: $%.2f", value)
        return DiagnosticResult.verified(
            agent_message=f"Compound interest calculated for ${principal:,.2f} at {rate}% over {years} years",
            developer_fields={
                "value": value,
                "method": result.developer_fields.get("method", "symbolic engine"),
                "constraint_id": "FIN-001",
            },
            evidence=result.developer_fields,
        )

    def loan_payment(self, principal: float, annual_rate: float, years: int) -> DiagnosticResult:
        """
        Calculate a monthly loan payment with deterministic verification.

        Formula: M = P[r(1+r)^n]/[(1+r)^n-1]
        Returns DiagnosticResult with proof_ref on VERIFIED.
        """
        self._validate_financial_inputs(principal, annual_rate, years)
        query = f"""
        Calculate monthly payment for a loan:
        - Principal: ${principal:,.2f}
        - Annual rate: {annual_rate}%
        - Term: {years} years

        Use the standard amortizing loan payment formula.
        """

        result = self.client.verify_math(query)
        self.calculation_count += 1

        if result.status != DiagnosticStatus.VERIFIED:
            self.blocked_calculations += 1
            logger.error("Loan-payment verification failed: %s", result.agent_message)
            raise VerificationError(
                f"Loan-payment calculation is unverifiable: {result.agent_message}. "
                "Do not substitute a fallback value."
            )

        value = result.developer_fields.get("value")
        logger.info("Verified loan payment: $%.2f", value)
        return DiagnosticResult.verified(
            agent_message=f"Monthly loan payment calculated for ${principal:,.2f} at {annual_rate}% over {years} years",
            developer_fields={
                "value": value,
                "method": result.developer_fields.get("method", "symbolic engine"),
                "constraint_id": "FIN-002",
            },
            evidence=result.developer_fields,
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
    print(f"Status: {compound.status.value}")
    print(f"Value: ${compound.developer_fields['value']:,.2f}")
    print(f"Proof Ref: {compound.proof_ref}")
    print(f"Is Authoritative: {compound.is_authoritative}")

    print("\nExample 2: Mortgage Payment")
    mortgage = calc.loan_payment(principal=500000, annual_rate=6.5, years=30)
    print(f"Status: {mortgage.status.value}")
    print(f"Monthly Payment: ${mortgage.developer_fields['value']:,.2f}")
    print(f"Proof Ref: {mortgage.proof_ref}")

    print("\nCalculator Statistics")
    stats = calc.get_stats()
    print(f"Total Calculations: {stats['total_calculations']}")
    print(f"Blocked Calculations: {stats['blocked_calculations']}")
    print(f"Verification Success Rate: {stats['verification_success_rate']:.1f}%")
