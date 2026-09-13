from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import os
from src.llm.schema import TriageRequest, TriageResponse
from src.llm.service import classify_message
from fastapi import HTTPException
from src.llm.pipeline import process_model_output

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


@app.post("/triage", response_model=TriageResponse)
def triage(request: TriageRequest):
    if os.getenv("LLM_STUB") == "1":
        return TriageResponse(
            category="billing",
            urgency="normal",
            confidence=0.95,
            reason="The customer reports a billing issue.",
        )

    if os.getenv("LLM_ENABLED", "true").lower() != "true":
        return TriageResponse(
            category="other",
            urgency="normal",
            confidence=0.0,
            reason="LLM processing is currently disabled.",
        )

    model_output = classify_message(request.text)

    try:
        result, repair_count = process_model_output(model_output)
        return result

    except ValueError as error:
        raise HTTPException(
            status_code=422,
            detail=str(error),
        )