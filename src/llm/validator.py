from src.llm.schema import TriageResponse


def validate_output(data: dict) -> TriageResponse:
    return TriageResponse.model_validate(data)