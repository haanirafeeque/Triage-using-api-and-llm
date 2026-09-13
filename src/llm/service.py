from src.llm.client import create_client
from src.llm.prompt import load_prompt
import os

def classify_message(text: str) -> str:
    client = create_client()
    system_prompt = load_prompt()

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

    return response.choices[0].message.content