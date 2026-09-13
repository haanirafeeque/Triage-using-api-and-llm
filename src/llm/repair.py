import os
import time

from src.llm.client import create_client
from src.llm.logging import log_llm_call
from src.llm.prompt import load_prompt, PROMPT_VERSION


def repair_output(
    original_output: str,
    validation_error: str,
) -> str:
    client = create_client()

    system_prompt = load_prompt()

    repair_message = f"""
The previous model output failed validation.

Previous output:
{original_output}

Validation error:
{validation_error}

Return ONLY a corrected JSON object that follows the required output
format and rules from the system prompt.

Do not use Markdown.
Do not use code fences.
Do not add explanations.
"""

    start_time = time.perf_counter()

    response = client.chat.completions.create(
        model=os.environ["LLM_MODEL"],
        temperature=0.0,
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": repair_message,
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
        repair_count=1,
    )

    return response.choices[0].message.content