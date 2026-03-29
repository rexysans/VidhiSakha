import requests
import time

BASE = "http://127.0.0.1:8000/v1/ask"

# V2: ADVERSARIAL & NUANCED TEST CASES
test_cases_v2 = {
    # 1. Semantic Nuance (Avoids title words)
    "can i be forced to join a union?": "19",
    "right against self-incrimination": "20",
    "protection from arbitrary arrest": "22",
    "who pays for minority run schools?": "30",
    "procedure for the death penalty": "21",
    
    # 2. Sibling Article Stress (Overlapping topics)
    "what happens to states when center takes over?": "356",
    "can the president stop giving tax money to states during war?": "354",
    "declaring a war-time emergency": "352",
    "person who went to pakistan and came back in 1948": "7",
    "rights of indian people living in london": "8",
    
    # 3. Procedural vs Substantive
    "can parliament change citizenship rules?": "11",
    "how to move the supreme court for rights?": "32",
    "can high courts issue writs?": "226",
    "steps to separate judges from bureaucrats": "50",
    
    # 4. Directive Principles (Abstract Phrasing)
    "steps to stop cow slaughter": "48",
    "guaranteeing a living wage": "43",
    "protection of the Taj Mahal and other sites": "49",
    "improving public health": "47",
    
    # 5. Advanced Junk (Adversarial - Sounds Legal but isn't in Constitution)
    "right to bear arms": None, # US Constitution
    "freedom from unreasonable searches": None, # US 4th Amendment
    "IPC section 302 punishment": None, # Criminal Law, not Constitution
    "how to file a divorce": None, # Family Law
    "punishment for cheque bounce": None, # NI Act
    "who is the Chief Justice of the US?": None,
    "salary of a software engineer in India": None
}

def run_stress_test():
    total = len(test_cases_v2)
    correct = 0
    junk_correct = 0
    
    print(f"🚀 Starting VidhiSakhā v1.7 Stress Test on {total} nuanced queries...")
    
    for q, expected in test_cases_v2.items():
        try:
            # Increased timeout to 60s for CPU processing
            r = requests.get(BASE, params={"q": q}, timeout=60)
            if r.status_code != 200:
                print(f"Error: HTTP {r.status_code} for '{q}'")
                continue
            data = r.json().get("answer", {})
            citations = data.get("citations", [])
            
            predicted = str(citations[0].get("article_id")) if citations else None
            
            print("-" * 40)
            print(f"Query: {q}")
            
            if expected is None:
                if not predicted:
                    print("Result: ✅ ADVERSARIAL JUNK REJECTED")
                    junk_correct += 1
                else:
                    print(f"Result: ❌ HALLUCINATION FAIL (Predicted Art {predicted})")
            else:
                if predicted == str(expected):
                    print(f"Result: ✅ NUANCE PASS (Art {predicted})")
                    correct += 1
                else:
                    print(f"Result: ❌ PRECISION FAIL (Expected {expected}, Got {predicted})")

        except Exception as e:
            print(f"Error processing '{q}': {e}")

    # Final Stats
    print("=" * 60)
    legal_total = sum(1 for v in test_cases_v2.values() if v is not None)
    junk_total = total - legal_total
    
    print(f"Adversarial Legal Accuracy: {correct}/{legal_total}")
    print(f"Adversarial Junk Accuracy: {junk_correct}/{junk_total}")
    print(f"Total Stress Test Score: {(correct + junk_correct) / total:.2%}")

if __name__ == "__main__":
    run_stress_test()