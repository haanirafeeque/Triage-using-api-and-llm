import json
from datetime import datetime, timezone
from pathlib import Path


LOG_PATH = Path("logs/quarantine.jsonl")


def quarantine_output(
    original_output: str,
    repaired_output: str,
    error: str,
):
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "original_output": original_output,
        "repaired_output": repaired_output,
        "error": error,
    }

    with LOG_PATH.open("a", encoding="utf-8") as file:
        file.write(json.dumps(record) + "\n")