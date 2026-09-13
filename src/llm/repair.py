import os

from src.llm.client import create_client
from src.llm.prompt import load_prompt


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

    return response.choices[0].message.content