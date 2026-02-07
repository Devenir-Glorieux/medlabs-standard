import json
from pathlib import Path

from medlabs_sdk.core.validate import validate_jsonschema

ROOT = Path(__file__).resolve().parents[1]


def test_validate_jsonschema_accepts_golden_fixture() -> None:
    fixture = ROOT / "standard" / "examples" / "v0.1" / "cbc" / "cbc-example-1.json"
    payload = json.loads(fixture.read_text(encoding="utf-8"))

    result = validate_jsonschema(payload, panel_code="CBC")

    assert result.is_valid
    assert not result.errors


def test_validate_jsonschema_reports_path_and_severity() -> None:
    payload = {
        "id": "panel-1",
        "resource_type": "panel",
        "standard_version": "0.1",
        "panel_code": {"system": "MEDLABS-PANEL", "code": "CBC", "display": "Complete Blood Count"},
        "status": "final",
        "source": {
            "document_id": "doc-1",
            "lab_name": "X",
            "report_date": "2026-02-07",
            "raw_text": "cbc",
        },
    }

    result = validate_jsonschema(payload, panel_code="CBC")

    assert not result.is_valid
    assert result.errors
    assert result.errors[0].path == "/"
    assert result.errors[0].severity == "error"
