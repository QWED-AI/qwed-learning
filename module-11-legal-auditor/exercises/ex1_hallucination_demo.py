"""
Exercise 1: Hallucination Demo (The Crisis)

This script demonstrates why 'qwed-legal' is necessary.
We simulate an LLM generating a legal brief with a hallucinated case citation.

Goal: Understand that LLMs are probabilistic "Artists", not deterministic "Accountants".
"""

import time

# SIMULATED LLM RESPONSE (This is what an LLM might actually generate)
HALLUCINATED_RESPONSE = """
Based on the precedent set in Mata v. Avianca, 2023 WL 123456 (S.D.N.Y.), 
the airline is liable for the missed connection due to the implicit contract of carriage. 
This case clearly establishes the 'duty of swift rebooking'.
"""

def simulated_legal_brief_generator(prompt):
    print(f"🤖 AI connecting to Legal Database... (Simulating)")
    time.sleep(1)
    print("📝 Drafting brief...")
    time.sleep(1)
    return HALLUCINATED_RESPONSE

def main():
    print("--- 📉 The Problem: Unverified AI Lawyer ---")
    prompt = "Draft a brief arguing for passenger compensation."
    
    response = simulated_legal_brief_generator(prompt)
    
    print("\n[AI Output]:")
    print(response)
    
    print("\n🛑 STOP!")
    print("Did you check the citation 'Mata v. Avianca'?")
    print("REALITY CHECK: In the real world, ChatGPT famously hallucinated 'Mata v. Avianca' cases.")
    print("Lawyers were sanctioned for submitting this to court.")
    print("\nIn the next exercises, we will build Guards to prevent this.")

if __name__ == "__main__":
    main()
