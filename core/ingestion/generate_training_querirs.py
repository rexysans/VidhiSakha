import json
import os

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


def generate_training_json(output_path="dataset/training_queries.json"):
    # Ensure directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    training_data = []

    for query, article_id in test_cases.items():
        # EXCLUDE JUNK: Only include if article_id is not None
        if article_id is not None:
            training_data.append(
                {
                    "query": query,
                    "article_id": str(
                        article_id
                    ),  # Ensure ID is a string (e.g., "39A")
                }
            )

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(training_data, f, indent=2)

    print(
        f"Successfully generated {len(training_data)} training queries in {output_path}"
    )


if __name__ == "__main__":
    generate_training_json()
