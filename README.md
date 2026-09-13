# FlyRank Week 7 — LLM Support Ticket Triage API

A FastAPI API that uses a locally hosted **Ollama + Gemma 3 1B** model to classify customer support messages into validated categories and urgency levels.

## Pipeline

```text
Input → Validation → Versioned Prompt → LLM
      → Parse JSON → Pydantic Validation
      → Valid → Response
      → Invalid → One Repair → Validate
      → Failed → Quarantine + 422
```

## Tech Stack

- Python
- FastAPI
- Pydantic
- Uvicorn
- Ollama
- Gemma 3 1B

## API

### `POST /triage`

Request:

```json
{
  "text": "I was charged twice for my subscription."
}
```

Example response:

```json
{
  "category": "billing",
  "urgency": "normal",
  "confidence": 0.95,
  "reason": "The customer reports being charged twice for a subscription."
}
```

Allowed categories:

```text
billing | bug | feature | other
```

Allowed urgency:

```text
low | normal | high
```

Input is validated before any LLM call. Invalid requests return `400`.

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install fastapi uvicorn pydantic openai python-dotenv requests
```

Pull the Ollama model:

```bash
ollama pull gemma3:1b
```

Create `.env`:

```env
LLM_BASE_URL=http://localhost:11434/v1/
LLM_API_KEY=ollama
LLM_MODEL=gemma3:1b
LLM_STUB=0
LLM_ENABLED=true
```

Run:

```bash
uvicorn src.main:app --reload
```

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

## Stub Mode

Set:

```env
LLM_STUB=1
```

This skips the LLM and returns a deterministic, schema-valid response.

## Reliability

- 30-second LLM timeout
- Automatic SDK retries disabled
- Retries for timeouts, `429`, and `5xx`
- Exponential backoff with jitter
- No retries for `400`, `401`, or `403`
- `LLM_ENABLED=false` acts as a kill switch

## Output Safety

LLM output is:

1. Parsed as JSON
2. Validated using Pydantic
3. Repaired once if invalid
4. Returned as `422` and written to `logs/quarantine.jsonl` if repair fails

LLM usage is logged in:

```text
logs/llm_calls.jsonl
```

## Prompt

The system prompt is versioned separately:

```text
prompts/triage-v1.md
```

Customer input is sent separately as the user message and is treated as untrusted data.

## Evaluation

Eight hand-labelled cases are stored in:

```text
evals/cases.json
```

Run:

```bash
python evals/run.py
```

### Actual Result

```text
Model: gemma3:1b
Prompt: triage-v1
Cases: 8
Matches: 6/8
Case score: 75.0%
Category matches: 6/8
Urgency matches: 6/8
Key-field score: 75.0%
```

The results are saved in:

```text
evals/results.json
```

## Cost

Because Ollama runs locally, direct hosted LLM API cost is **$0**.

One observed call:

```text
Input tokens: 1047
Output tokens: 53
Duration: 2758 ms
Repair count: 1
```

Actual infrastructure cost depends on the hardware and electricity used to run Ollama.

## Job Card

**Input:** customer support message, 1–2000 characters.

**Output:**

```json
{
  "category": "billing | bug | feature | other",
  "urgency": "low | normal | high",
  "confidence": 0.0,
  "reason": "one short sentence"
}
```

When unsure, use `other` with low confidence.



## Security

- `.env` is excluded from Git.
- Customer messages are treated as untrusted input.
- Raw invalid LLM output is never returned to the client.
- Output is constrained by the Pydantic schema.
