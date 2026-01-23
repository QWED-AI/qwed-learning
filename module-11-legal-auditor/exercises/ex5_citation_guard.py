"""
Exercise 5: CitationGuard (The Fact Shield)

Goal: Verify legal citations against a trusted allow-list or regex pattern
to prevent "Mata v. Avianca" style hallucinations.
"""

import re

# A simplified database of real cases
REAL_CASES_DB = [
    "Roe v. Wade",
    "Brown v. Board of Education",
    "Miranda v. Arizona",
    "Marbury v. Madison"
]

def verify_citation(citation_text):
    print(f"🔎 Verifying Citation: '{citation_text}'")
    
    # 1. Format Check (Regex)
    # Looking for "v." pattern
    if not re.search(r".+ v\. .+", citation_text):
        return False, "❌ Invalid Format: Not a proper legal citation format."
        
    # 2. Fact Check (Database Lookup)
    if citation_text not in REAL_CASES_DB:
        return False, "❌ HALLUCINATION WARNING: Case not found in trusted database."
        
    return True, "✅ Citation Verified."

def main():
    print("--- 📚 CitationGuard (Fact Shield) ---\n")
    
    # Case 1: Real Case
    valid, msg = verify_citation("Miranda v. Arizona")
    print(msg)
    
    # Case 2: Fake Case (Hallucinated by LLM)
    print("\nChecking generated content...")
    valid, msg = verify_citation("Mata v. Avianca") # The famous fake case
    print(msg)
    
    # Case 3: Bad Format
    print("\nChecking malformed content...")
    valid, msg = verify_citation("The case about the airline")
    print(msg)

if __name__ == "__main__":
    main()
