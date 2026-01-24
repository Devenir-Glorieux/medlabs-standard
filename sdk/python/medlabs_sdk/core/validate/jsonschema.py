from typing import Any

from medlabs_sdk.core.models import ValidationResult

def validate_jsonschema(payload: dict[str, Any], schema_path: str) -> ValidationResult:
    raise NotImplementedError("JSON Schema validation is not implemented")
