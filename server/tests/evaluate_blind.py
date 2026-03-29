import json
import requests
from pathlib import Path

BASE = "http://127.0.0.1:8000/v1/ask"
DATASET_PATH = Path("dataset/blind_eval_120.json")


def load_dataset():
    if not DATASET_PATH.exists():
        raise FileNotFoundError(f"Blind eval dataset not found: {DATASET_PATH}")
    with DATASET_PATH.open("r", encoding="utf-8") as f:
        items = json.load(f)
    if not isinstance(items, list):
        raise ValueError("Dataset must be a JSON array")
    return items


def run_blind_eval(timeout_sec: int = 120):
    data = load_dataset()
    legal_total = sum(1 for x in data if x.get("expected") is not None)
    junk_total = len(data) - legal_total

    legal_correct = 0
    junk_correct = 0

    print(f"Running blind evaluation on {len(data)} queries...")

    for i, item in enumerate(data, start=1):
        query = item["query"]
        expected = item.get("expected")

        predicted = None
        citations = []

        try:
            r = requests.get(BASE, params={"q": query}, timeout=timeout_sec)
            r.raise_for_status()
            payload = r.json().get("answer", {})
            citations = payload.get("citations", [])
            if citations:
                predicted = str(citations[0].get("article_id"))
        except Exception as e:
            print(f"[{i}] ERROR | query={query!r} | {e}")
            continue

        if expected is None:
            ok = len(citations) == 0
            junk_correct += 1 if ok else 0
            result = "JUNK_PASS" if ok else f"JUNK_FAIL(pred={predicted})"
        else:
            ok = predicted == str(expected)
            legal_correct += 1 if ok else 0
            result = "PASS" if ok else f"FAIL(exp={expected}, pred={predicted})"

        print(f"[{i}] {result} | {query}")

    print("=" * 64)
    print(f"Legal Accuracy: {legal_correct}/{legal_total} = {legal_correct / max(legal_total, 1):.2%}")
    print(f"Junk Accuracy:  {junk_correct}/{junk_total} = {junk_correct / max(junk_total, 1):.2%}")
    total_correct = legal_correct + junk_correct
    total = len(data)
    print(f"Overall:        {total_correct}/{total} = {total_correct / max(total, 1):.2%}")


if __name__ == "__main__":
    run_blind_eval()
