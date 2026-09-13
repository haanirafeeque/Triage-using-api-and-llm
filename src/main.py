from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import os
from src.llm.schema import TriageRequest, TriageResponse
from src.llm.service import classify_message

load_dotenv()

app = FastAPI(title="FlyRank Week 7 LLM API")


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
):
    errors = exc.errors()

    fields = []

    for error in errors:
        location = error.get("loc", [])

        if location:
            fields.append(str(location[-1]))

    return JSONResponse(
        status_code=400,
        content={
            "error": "Invalid request",
            "fields": fields,
        },
    )


@app.get("/")
def root():
    return {
        "message": "FlyRank Week 7 API is running"
    }


@app.post("/triage")
def triage(request: TriageRequest):
    if os.getenv("LLM_STUB") == "1":
        return TriageResponse(
            category="billing",
            urgency="normal",
            confidence=0.95,
            reason="The customer reports a billing issue.",
        )

    model_output = classify_message(request.text)
    return model_output