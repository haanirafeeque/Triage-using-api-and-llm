from src.llm.parser import parse_json
from src.llm.validator import validate_output
from src.llm.repair import repair_output
from src.llm.quarantine import quarantine_output


def process_model_output(model_output: str):
    # First attempt
    try:
        data = parse_json(model_output)
        return validate_output(data), 0

    except Exception as first_error:
        # Repair exactly once
        repaired_output = repair_output(
            original_output=model_output,
            validation_error=str(first_error),
        )

        # Second attempt
        try:
            data = parse_json(repaired_output)
            return validate_output(data), 1

        except Exception as second_error:
            quarantine_output(
                original_output=model_output,
                repaired_output=repaired_output,
                error=str(second_error),
            )

            raise ValueError(
                "Model output failed validation after one repair attempt."
            )