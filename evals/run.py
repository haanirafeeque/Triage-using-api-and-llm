import json
from pathlib import Path
from datetime import datetime, timezone
import requests


CASES_PATH = Path(__file__).with_name("cases.json")
API_URL = "http://127.0.0.1:8000/triage"


def load_cases():
    with CASES_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


def main():
    cases = load_cases()

    matches = 0
    category_matches = 0
    urgency_matches = 0
    total_fields = len(cases) * 2
    failures = []

    for case in cases:
        response = requests.post(
            API_URL,
            json={"text": case["text"]},
            timeout=35,
        )

        if response.status_code != 200:
            failures.append(
                {
                    "id": case["id"],
                    "error": f"HTTP {response.status_code}",
                    "response": response.text,
                }
            )
            continue

        result = response.json()

        category_match = (
            result.get("category")
            == case["expected"]["category"]
        )

        urgency_match = (
            result.get("urgency")
            == case["expected"]["urgency"]
        )

        if category_match:
            category_matches += 1

        if urgency_match:
            urgency_matches += 1

        if category_match and urgency_match:
            matches += 1
        else:
            failures.append(
                {
                    "id": case["id"],
                    "expected": case["expected"],
                    "actual": {
                        "category": result.get("category"),
                        "urgency": result.get("urgency"),
                    },
                }
            )

    total = len(cases)

    case_score = (
        (matches / total) * 100
        if total
        else 0
    )

    key_field_matches = (
        category_matches + urgency_matches
    )

    key_field_score = (
        (key_field_matches / total_fields) * 100
        if total_fields
        else 0
    )

    results = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "prompt_version": "triage-v1",
        "model": "gemma3:1b",
        "cases": total,
        "matches": matches,
        "case_score": case_score,
        "category_matches": category_matches,
        "urgency_matches": urgency_matches,
        "key_field_score": key_field_score,
        "failures": failures,
    }

    results_path = Path(__file__).with_name("results.json")

    with results_path.open("w", encoding="utf-8") as file:
        json.dump(results, file, indent=2)

    print(f"Cases: {total}")
    print(f"Matches: {matches}")
    print(f"Case score: {case_score:.1f}%")
    print(f"Category matches: {category_matches}/{total}")
    print(f"Urgency matches: {urgency_matches}/{total}")
    print(f"Key-field score: {key_field_score:.1f}%")

    if failures:
        print("\nFailures:")

        for failure in failures:
            print(json.dumps(failure, indent=2))

if __name__ == "__main__":
    main()