import requests

BASE = "http://127.0.0.1:8000/v1/ask"

test_cases = {
    # Core
    "equality before law": "14",
    "abolition of untouchability": "17",
    "freedom of religion": "25",
    "minority educational institutions": "30",
    "right to constitutional remedies": "32",
    "protection against double jeopardy": "20",
    "forced labour prohibition": "23",
    "child labour prohibition": "24",
    "freedom to form associations": "19",
    # Citizenship
    "citizenship by birth": "5",
    "migrants from pakistan citizenship": "6",
    "foreign citizenship disqualification": "9",
    "parliament power over citizenship": "11",
    # Emergency
    "national emergency proclamation": "352",
    "suspension of article 19 during emergency": "358",
    "financial emergency": "360",
    "parliament power during emergency": "353",
    "president rule in state": "356",
    # Reservation
    "reservation in public employment": "16",
    "reservation for scheduled castes services": "335",
    "reservation of seats in panchayats": "243D",
    "reservation in municipalities": "243T",
    # Directive Principles
    "uniform civil code": "44",
    "equal pay for equal work": "39",
    "free legal aid": "39A",
    "protection of environment": "48A",
    "separation of judiciary from executive": "50",
    # Ambiguous
    "freedom restrictions": "19",
    "state cannot discriminate": "15",
    "right to life": "21",
    "public order restriction speech": "19",
    "preventive detention": "22",
    "can government stop free speech": "19",
    "can state deny job based on caste": "16",
    "detained without lawyer": "22",
    "court writ powers": "32",
    # Direct mentions (should later bypass semantic)
    "Article 21": "21",
    "Article 19 restrictions": "19",
    "Article 356 explanation": "356",
    "Explain Article 14": "14",
    # Junk (expected None)
    "how to cook pasta": None,
    "best programming language 2025": None,
    "weather in delhi": None,
    "who is prime minister of japan": None,
    "how to build a startup": None,
    "quantum computing basics": None,
    "football world cup winner": None,
    # Confusion traps
    "reservation": "16",
    "jobs equality": "16",
    "religious institution management": "26",
    "religious tax payment": "27",
    "religious instruction in schools": "28",
}


def run_evaluation():
    correct = 0
    junk_correct = 0
    total = len(test_cases)

    print(f"Starting Evaluation on {total} queries...\n")

    for q, expected in test_cases.items():
        predicted = None
        citations = []

        try:
            # 1. API Call
            r = requests.get(BASE, params={"q": q}, timeout=300)
            r.raise_for_status()  # Raise error for 4xx/5xx responses
            data = r.json().get("answer", {})
            citations = data.get("citations", [])

            # 2. Extract Prediction (Indented INSIDE the loop)
            if citations:
                predicted = str(citations[0].get("article_id"))

            # 3. Logic Check (Indented INSIDE the loop)
            print("-" * 40)
            print(f"Query: {q}")
            print(f"Expected: {expected} | Predicted: {predicted}")

            if expected is None:
                if not citations:
                    print("Result: ✅ JUNK PASS")
                    junk_correct += 1
                else:
                    print("Result: ❌ JUNK FAIL (Returned results for junk query)")
            else:
                if predicted == str(expected):
                    print("Result: ✅ PASS")
                    correct += 1
                else:
                    print(f"Result: ❌ FAIL")

        except requests.exceptions.ConnectionError:
            print(
                f"Error: Could not connect to server for query '{q}'. Is uvicorn running?"
            )
            continue
        except Exception as e:
            print(f"Error processing '{q}': {e}")
            continue

    # 4. Final Stats (Outside the loop)
    print("=" * 60)
    print(
        f"Core Accuracy (Legal): {correct}/{total - 7}"
    )  # Subtracting your 7 junk queries
    print(f"Junk Accuracy: {junk_correct}/7")
    print(f"Overall Accuracy: {(correct + junk_correct) / total:.2%}")


if __name__ == "__main__":
    run_evaluation()
