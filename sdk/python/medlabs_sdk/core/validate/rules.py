from typing import Any

from medlabs_sdk.core.models import ValidationResult

def validate_rules(payload: dict[str, Any]) -> ValidationResult:
    errors: list[str] = []
    warnings: list[str] = []

    observations = payload.get("observations", [])
    if observations is None:
        observations = []

    if not isinstance(observations, list):
        errors.append("observations must be a list")
        return ValidationResult(is_valid=False, errors=errors, warnings=warnings)

    panel_code = payload.get("panel_code", {})
    panel_name = payload.get("panel_name")
    if isinstance(panel_code, dict):
        display = panel_code.get("display")
        if panel_name and display and panel_name != display:
            warnings.append("panel_name should match panel_code.display")

    for index, obs in enumerate(observations):
        if not isinstance(obs, dict):
            errors.append(f"observations[{index}] must be an object")
            continue

        value = obs.get("value")
        ref_range = obs.get("reference_range")
        path = f"observations[{index}]"

        if isinstance(value, dict):
            unit_code = value.get("unit_code")
            unit_system = value.get("unit_system")
            if not unit_code:
                errors.append(f"{path}.value.unit_code is required for numeric values")
            if unit_system and unit_system != "UCUM":
                warnings.append(f"{path}.value.unit_system is expected to be UCUM")

            if isinstance(ref_range, dict):
                for bound in ("low", "high"):
                    bound_value = ref_range.get(bound)
                    if isinstance(bound_value, dict):
                        bound_unit_code = bound_value.get("unit_code")
                        bound_unit_system = bound_value.get("unit_system")
                        if unit_code and bound_unit_code and bound_unit_code != unit_code:
                            errors.append(
                                f"{path}.reference_range.{bound}.unit_code must match value.unit_code"
                            )
                        if unit_system and bound_unit_system and bound_unit_system != unit_system:
                            errors.append(
                                f"{path}.reference_range.{bound}.unit_system must match value.unit_system"
                            )
        elif value is None:
            if isinstance(ref_range, dict) and any(key in ref_range for key in ("low", "high")):
                warnings.append(f"{path}.reference_range provided for null value")
        else:
            if isinstance(ref_range, dict) and any(key in ref_range for key in ("low", "high")):
                warnings.append(f"{path}.reference_range has numeric bounds for non-numeric value")

    return ValidationResult(is_valid=not errors, errors=errors, warnings=warnings)
