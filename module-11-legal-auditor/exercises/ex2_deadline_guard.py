"""
Exercise 2: DeadlineGuard (Precision Date Verification)

Goal: Verify contract deadlines using deterministic logic that handles
jurisdiction-specific holidays (e.g., UK Bank Holidays vs US Federal Holidays).
"""

from datetime import date
# In a real scenario, you'd import from qwed_legal
# from qwed_legal.guards.deadline_guard import DeadlineGuard

class MockDeadlineGuard:
    """Simulated DeadlineGuard for educational purpose"""
    def verify(self, start_date, days, jurisdiction, expected_end_date):
        print(f"🛡️  Verifying deadline: {days} business days after {start_date} in {jurisdiction}...")
        
        # Deterministic Logic (Simplified for demo)
        # In reality, this uses the 'holidays' library
        real_end_date = None
        if jurisdiction == "UK":
            # Simulation: UK has a Bank Holiday effectively pushing the date
            real_end_date = "2024-01-05" 
        elif jurisdiction == "US":
            real_end_date = "2024-01-04"
            
        if expected_end_date == real_end_date:
            return True, "✅ Deadline Correct"
        else:
            return False, f"❌ Deadline Missed. Expected {expected_end_date}, but {jurisdiction} calendar says {real_end_date}"

def main():
    guard = MockDeadlineGuard()
    
    print("--- 🗓️ DeadlineGuard In Action ---")
    
    # Scenario: Contract says "3 business days after Jan 1st, 2024"
    # LLM says: Jan 4th
    
    # Test 1: US Context (Safe)
    valid, msg = guard.verify(
        start_date="2024-01-01", 
        days=3, 
        jurisdiction="US", 
        expected_end_date="2024-01-04"
    )
    print(f"US Check: {msg}")
    
    # Test 2: UK Context (Fail - Bank Holiday?)
    # Imagine Jan 2nd was a UK Bank Holiday
    valid, msg = guard.verify(
        start_date="2024-01-01", 
        days=3, 
        jurisdiction="UK", 
        expected_end_date="2024-01-04" # LLM is unaware of UK holiday
    )
    print(f"UK Check: {msg}")

if __name__ == "__main__":
    main()
