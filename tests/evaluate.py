import requests

BASE = "http://127.0.0.1:8000/v1/ask?q="

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

correct = 0
junk_correct = 0
total = len(test_cases)

for q, expected in test_cases.items():
    r = requests.get(BASE + q.replace(" ", "%20"))
    data = r.json().get("answer", {})

    citations = data.get("citations", [])

    predicted = None
    if citations:
        predicted = citations[0]["article_id"]

    print("="*60)
    print("Query:", q)
    print("Expected:", expected)
    print("Predicted:", predicted)

    if expected is None:
        if not citations:
            print("JUNK PASS")
            junk_correct += 1
        else:
            print("JUNK FAIL")
    else:
        if predicted == expected:
            print("PASS")
            correct += 1
        else:
            print("FAIL")

print("\nCore Accuracy:", correct)
print("Junk Accuracy:", junk_correct)
print("Total Queries:", total)
print("Overall Accuracy:", (correct + junk_correct) / total)
