import os
import random
import time

from src.llm.client import create_client
from src.llm.logging import log_llm_call
from src.llm.prompt import load_prompt, PROMPT_VERSION


def classify_message(text: str) -> str:
    client = create_client()
    system_prompt = load_prompt()

    max_attempts = 3

    for attempt in range(max_attempts):
        start_time = time.perf_counter()

        try:
            response = client.chat.completions.create(
                model=os.environ["LLM_MODEL"],
                temperature=0.2,
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt,
                    },
                    {
                        "role": "user",
                        "content": text,
                    },
                ],
            )

            duration_ms = int(
                (time.perf_counter() - start_time) * 1000
            )

            usage = response.usage

            input_tokens = usage.prompt_tokens if usage else 0
            output_tokens = usage.completion_tokens if usage else 0

            log_llm_call(
                prompt_version=PROMPT_VERSION,
                model=os.environ["LLM_MODEL"],
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                duration_ms=duration_ms,
                repair_count=0,
            )

            return response.choices[0].message.content

        except Exception as error:
            if not should_retry(error) or attempt == max_attempts - 1:
                raise

            delay = (2 ** attempt) + random.uniform(0, 0.5)

            print(
                f"LLM call failed: {type(error).__name__}. "
                f"Retrying in {delay:.2f}s..."
            )

            time.sleep(delay)


def should_retry(error: Exception) -> bool:
    status_code = getattr(error, "status_code", None)

    if status_code == 429:
        return True

    if status_code is not None and 500 <= status_code <= 599:
        return True

    error_name = type(error).__name__.lower()

    if "timeout" in error_name:
        return True

    return False