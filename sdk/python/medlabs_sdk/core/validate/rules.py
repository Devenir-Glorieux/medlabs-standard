from __future__ import annotations

from typing import Any

from medlabs_sdk.core.models import ValidationIssue, ValidationResult


def _is_error(issue: ValidationIssue) -> bool:
    return issue.severity == "error"


def validate_rules(payload: dict[str, Any]) -> ValidationResult:
    issues: list[ValidationIssue] = []

    observations = payload.get("observations")
    if not isinstance(observations, list):
        issues.append(
            ValidationIssue(
                path="/observations",
                description="observations must be an array",
                severity="error",
            )
        )
        return ValidationResult(is_valid=False, issues=issues)

    for index, observation in enumerate(observations):
        path_prefix = f"/observations/{index}"
        if not isinstance(observation, dict):
            issues.append(
                ValidationIssue(
                    path=path_prefix,
                    description="observation must be an object",
                    severity="error",
                )
            )
            continue

        value = observation.get("value")
        reference_range = observation.get("reference_range")

        if isinstance(value, dict):
            value_unit_code = value.get("unit_code")
            value_unit_system = value.get("unit_system")
            if not value_unit_code:
                issues.append(
                    ValidationIssue(
                        path=f"{path_prefix}/value/unit_code",
                        description="unit_code is required for quantity values",
                        severity="error",
                    )
                )

            if value_unit_system and value_unit_system != "UCUM":
                issues.append(
                    ValidationIssue(
                        path=f"{path_prefix}/value/unit_system",
                        description="unit_system should be UCUM",
                        severity="warning",
                    )
                )

            if isinstance(reference_range, dict):
                for bound_key in ("low", "high"):
                    bound = reference_range.get(bound_key)
                    if not isinstance(bound, dict):
                        continue

                    bound_unit_code = bound.get("unit_code")
                    bound_unit_system = bound.get("unit_system")
                    if value_unit_code and bound_unit_code and value_unit_code != bound_unit_code:
                        issues.append(
                            ValidationIssue(
                                path=f"{path_prefix}/reference_range/{bound_key}/unit_code",
                                description="must match value.unit_code",
                                severity="error",
                            )
                        )

                    if (
                        value_unit_system
                        and bound_unit_system
                        and value_unit_system != bound_unit_system
                    ):
                        issues.append(
                            ValidationIssue(
                                path=f"{path_prefix}/reference_range/{bound_key}/unit_system",
                                description="must match value.unit_system",
                                severity="error",
                            )
                        )
        else:
            if isinstance(reference_range, dict) and (
                isinstance(reference_range.get("low"), dict)
                or isinstance(reference_range.get("high"), dict)
            ):
                issues.append(
                    ValidationIssue(
                        path=f"{path_prefix}/reference_range",
                        description=(
                            "reference_range with numeric bounds is ignored for "
                            "non-quantity values"
                        ),
                        severity="warning",
                    )
                )

    return ValidationResult(is_valid=not any(_is_error(item) for item in issues), issues=issues)
