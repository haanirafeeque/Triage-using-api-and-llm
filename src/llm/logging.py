import json
from datetime import datetime, timezone
from pathlib import Path


LOG_PATH = Path("logs/llm_calls.jsonl")


def log_llm_call(
    *,
    prompt_version: str,
    model: str,
    input_tokens: int,
    output_tokens: int,
    duration_ms: int,
    repair_count: int,
):
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "prompt_version": prompt_version,
        "model": model,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "duration_ms": duration_ms,
        "repair_count": repair_count,
    }

    with LOG_PATH.open("a", encoding="utf-8") as file:
        file.write(json.dumps(record) + "\n")