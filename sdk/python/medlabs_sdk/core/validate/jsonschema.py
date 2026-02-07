from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from medlabs_sdk.core.models import ValidationIssue, ValidationResult
from medlabs_sdk.core.validate.rules import validate_rules

_SCHEMA_BY_PANEL: dict[str, str] = {
    "CBC": "cbc.json",
    "BIOCHEM": "biochem.json",
    "URINALYSIS": "urinalysis.json",
}


def _default_schema_dir() -> Path:
    return Path(__file__).resolve().parents[5] / "standard" / "schema" / "v0.1"


def _schema_path_for_panel(panel_code: str, schema_dir: Path | None = None) -> Path:
    normalized = panel_code.strip().upper()
    filename = _SCHEMA_BY_PANEL.get(normalized)
    if not filename:
        raise ValueError(f"Unsupported panel code: {panel_code}")
    root = schema_dir or _default_schema_dir()
    return root / filename


def _jsonschema_issues(payload: dict[str, Any], schema_path: Path) -> list[ValidationIssue]:
    try:
        from jsonschema import Draft202012Validator
        from referencing import Registry, Resource
    except ImportError as exc:  # pragma: no cover - dependency error path
        raise RuntimeError("Install 'jsonschema' to validate payloads") from exc

    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    registry = Registry()
    for candidate in schema_path.parent.glob("*.json"):
        candidate_schema = json.loads(candidate.read_text(encoding="utf-8"))
        resource = Resource.from_contents(candidate_schema)
        registry = registry.with_resource(candidate.as_uri(), resource)
        registry = registry.with_resource(candidate.name, resource)
        schema_id = candidate_schema.get("$id")
        if isinstance(schema_id, str) and schema_id:
            registry = registry.with_resource(schema_id, resource)

    validator = Draft202012Validator(schema, registry=registry)

    issues: list[ValidationIssue] = []
    for error in sorted(validator.iter_errors(payload), key=lambda item: list(item.absolute_path)):
        path_parts = [str(part) for part in error.absolute_path]
        path = "/" + "/".join(path_parts) if path_parts else "/"
        issues.append(
            ValidationIssue(
                path=path,
                description=error.message,
                severity="error",
            )
        )
    return issues


def validate_jsonschema(
    payload: dict[str, Any],
    schema_path: str | Path | None = None,
    *,
    panel_code: str | None = None,
    schema_dir: str | Path | None = None,
) -> ValidationResult:
    issues: list[ValidationIssue] = []

    try:
        if schema_path is not None:
            resolved_schema_path = Path(schema_path)
        elif panel_code is not None:
            resolved_schema_path = _schema_path_for_panel(
                panel_code,
                schema_dir=Path(schema_dir) if schema_dir else None,
            )
        else:
            raise ValueError("Either schema_path or panel_code must be provided")

        issues.extend(_jsonschema_issues(payload, resolved_schema_path))
    except Exception as exc:
        issues.append(
            ValidationIssue(
                path="/",
                description=f"Schema validation failed to run: {exc}",
                severity="error",
            )
        )

    rule_result = validate_rules(payload)
    issues.extend(rule_result.issues)

    has_errors = any(issue.severity == "error" for issue in issues)
    return ValidationResult(is_valid=not has_errors, issues=issues)
