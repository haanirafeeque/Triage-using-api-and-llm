import json


def parse_json(text: str) -> dict:
    text = text.strip()

    # Remove Markdown code fences if the model adds them
    if text.startswith("```"):
        lines = text.splitlines()

        if lines[0].startswith("```"):
            lines = lines[1:]

        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        text = "\n".join(lines).strip()

    # Find the JSON object if there is extra text around it
    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end == -1 or end <= start:
        raise ValueError("No JSON object found in model output")

    text = text[start:end + 1]

    return json.loads(text)