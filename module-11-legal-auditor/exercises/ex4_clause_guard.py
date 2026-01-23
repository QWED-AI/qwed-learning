"""
Exercise 4: ClauseGuard (Logic & Contradictions)

Goal: Use logical proofs to find unexpected contradictions in contract terms.
Real implementations use Z3 Solver. Here we simulate the logic.
"""

def verify_payment_terms(term_a_days, term_b_days):
    print(f"🔍 Checking consistency: Clause A ({term_a_days} days) vs Clause B ({term_b_days} days)")
    
    if term_a_days != term_b_days:
        return False, f"❌ CONTRADICTION FOUND: Section 1 says Net {term_a_days}, but Section 14 says Net {term_b_days}."
    
    return True, "✅ Terms are consistent."

def main():
    print("--- 🧠 ClauseGuard (Logic) ---")
    
    # Scenario: Long contract.
    # Page 1: "Payment due within 30 days."
    # Page 50: "Payment due within 90 days."
    
    print("Scanning Contract...")
    
    # Consistent
    valid, msg = verify_payment_terms(30, 30)
    print(msg)
    
    # Contradictory
    valid, msg = verify_payment_terms(30, 90)
    print(msg)
    
    print("\n💡 Impact: An LLM summarizing this might just pick one number randomly.")
    print("   QWED ClauseGuard highlights the CONFLICT so a human can fix it.")

if __name__ == "__main__":
    main()
