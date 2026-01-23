"""
Exercise 3: LiabilityGuard (Financial Risk Auditing)

Goal: build a guard that checks extracted liability caps against
corporate policy.

Policy: "We do not accept liability greater than $1,000,000."
"""

class LiabilityGuard:
    def __init__(self, max_cap_usd):
        self.max_cap = max_cap_usd
        
    def check_clause(self, extracted_amount_usd):
        if extracted_amount_usd > self.max_cap:
            return False, f"Risk Alert: Cap ${extracted_amount_usd:,} exceeds policy ${self.max_cap:,}"
        return True, "✅ Liability within limits."

def main():
    print("--- 💰 LiabilityGuard Audit ---")
    
    # Company Policy: Max $1M
    auditor = LiabilityGuard(max_cap_usd=1_000_000)
    
    literals = [
        {"desc": "Standard Cap", "amount": 500_000},
        {"desc": "High Risk Cap", "amount": 5_000_000},
        {"desc": "Edge Case", "amount": 1_000_000}
    ]
    
    for case in literals:
        print(f"\nChecking: {case['desc']} (${case['amount']:,})")
        allowed, msg = auditor.check_clause(case['amount'])
        print(msg)
        
    print("\n💡 Key Insight: This guard runs *deterministically*. An LLM might say '5 million is reasonable', but the code says NO.")

if __name__ == "__main__":
    main()
