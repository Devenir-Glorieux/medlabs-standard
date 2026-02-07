from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from medlabs_sdk.core.models import NormalizedObservation, NormalizedReport, StandardPanel
from medlabs_sdk.core.normalize.units import unit_display

_PANEL_DEFINITIONS: dict[str, dict[str, str]] = {
    "CBC": {"display": "Complete Blood Count"},
    "BIOCHEM": {"display": "Biochemistry Panel"},
    "URINALYSIS": {"display": "Urinalysis Panel"},
}

_OBSERVATION_CODE_MAP: dict[str, dict[str, str]] = {
    "wbc": {
        "system": "LOINC",
        "code": "6690-2",
        "display": "Leukocytes [#/volume] in Blood",
    },
    "rbc": {
        "system": "LOINC",
        "code": "789-8",
        "display": "Erythrocytes [#/volume] in Blood",
    },
    "hemoglobin": {
        "system": "LOINC",
        "code": "718-7",
        "display": "Hemoglobin [Mass/volume] in Blood",
    },
    "hematocrit": {
        "system": "LOINC",
        "code": "4544-3",
        "display": "Hematocrit [Volume Fraction] of Blood",
    },
    "platelets": {
        "system": "LOINC",
        "code": "777-3",
        "display": "Platelets [#/volume] in Blood",
    },
    "glucose": {
        "system": "LOINC",
        "code": "2345-7",
        "display": "Glucose [Moles/volume] in Blood",
    },
    "creatinine": {
        "system": "LOINC",
        "code": "2160-0",
        "display": "Creatinine [Moles/volume] in Serum or Plasma",
    },
    "urea": {
        "system": "LOINC",
        "code": "3094-0",
        "display": "Urea nitrogen [Moles/volume] in Serum or Plasma",
    },
    "alt": {
        "system": "LOINC",
        "code": "1742-6",
        "display": "Alanine aminotransferase [Enzymatic activity/volume] in Serum or Plasma",
    },
    "ast": {
        "system": "LOINC",
        "code": "1920-8",
        "display": "Aspartate aminotransferase [Enzymatic activity/volume] in Serum or Plasma",
    },
    "color": {"system": "LOCAL", "code": "COLOR", "display": "Color"},
    "appearance": {"system": "LOCAL", "code": "APPEARANCE", "display": "Appearance"},
    "specific_gravity": {
        "system": "LOCAL",
        "code": "SPEC_GRAV",
        "display": "Specific gravity",
    },
    "ph": {"system": "LOCAL", "code": "PH", "display": "pH"},
    "protein": {"system": "LOCAL", "code": "PROTEIN", "display": "Protein"},
    "ketones": {"system": "LOCAL", "code": "KETONES", "display": "Ketones"},
    "nitrite": {"system": "LOCAL", "code": "NITRITE", "display": "Nitrite"},
    "leukocyte_esterase": {
        "system": "LOCAL",
        "code": "LEUK_ESTERASE",
        "display": "Leukocyte esterase",
    },
}


def _normalize_panel_code(panel: str) -> str:
    normalized = panel.strip().upper()
    if normalized in _PANEL_DEFINITIONS:
        return normalized

    alias_map = {
        "COMPLETE BLOOD COUNT": "CBC",
        "BIOCHEMISTRY PANEL": "BIOCHEM",
        "URINALYSIS PANEL": "URINALYSIS",
    }
    return alias_map.get(normalized, normalized)


def _report_date(meta: dict[str, Any]) -> str:
    report_date = meta.get("report_date")
    if isinstance(report_date, str) and len(report_date) == 10:
        return report_date
    return datetime.now(timezone.utc).date().isoformat()


def _source_trace(
    document_meta: dict[str, Any],
    *,
    evidence: dict[str, Any] | None = None,
    fallback_raw_text: str,
) -> dict[str, Any]:
    trace: dict[str, Any] = {
        "document_id": str(document_meta.get("document_id", "unknown-document")),
        "lab_name": str(document_meta.get("lab_name", "Unknown Lab")),
        "report_date": _report_date(document_meta),
        "raw_text": fallback_raw_text,
    }

    if evidence:
        page = evidence.get("page")
        line = evidence.get("line")
        raw_text = evidence.get("raw_text")
        if isinstance(page, int) and page > 0:
            trace["page"] = page
        if isinstance(line, int) and line > 0:
            trace["line"] = line
        if isinstance(raw_text, str) and raw_text.strip():
            trace["raw_text"] = raw_text.strip()

    return trace


def _quantity(value: float, unit: str) -> dict[str, Any]:
    unit_code = unit or "1"
    return {
        "value": value,
        "unit_code": unit_code,
        "unit_system": "UCUM",
        "unit_display": unit_display(unit_code),
    }


def _reference_range(observation: NormalizedObservation) -> dict[str, Any] | None:
    if observation.ref_low is None and observation.ref_high is None:
        return None

    unit_code = observation.unit or "1"
    result: dict[str, Any] = {}
    if observation.ref_low is not None:
        result["low"] = _quantity(observation.ref_low, unit_code)
    if observation.ref_high is not None:
        result["high"] = _quantity(observation.ref_high, unit_code)
    return result


def _interpretation(observation: NormalizedObservation) -> str:
    value = observation.value
    if not isinstance(value, float):
        return "unknown"
    if observation.ref_low is not None and value < observation.ref_low:
        return "low"
    if observation.ref_high is not None and value > observation.ref_high:
        return "high"
    if observation.ref_low is not None or observation.ref_high is not None:
        return "normal"
    return "unknown"


def _observation_code(observation: NormalizedObservation) -> dict[str, str]:
    coding = _OBSERVATION_CODE_MAP.get(observation.code)
    if coding:
        return coding

    display = observation.source_name or observation.code.replace("_", " ").title()
    return {
        "system": "LOCAL",
        "code": observation.code.upper(),
        "display": display,
    }


def _observation_value(
    observation: NormalizedObservation,
) -> float | str | bool | None | dict[str, Any]:
    value = observation.value
    if isinstance(value, float):
        return _quantity(value, observation.unit)
    if isinstance(value, bool) or value is None:
        return value
    return str(value)


def _observation_payload(
    observation: NormalizedObservation,
    *,
    panel_code: str,
    index: int,
    document_meta: dict[str, Any],
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "id": f"obs-{panel_code.lower()}-{index:03d}-{uuid4().hex[:6]}",
        "resource_type": "observation",
        "code": _observation_code(observation),
        "value": _observation_value(observation),
        "interpretation": _interpretation(observation),
        "status": "final",
        "source": _source_trace(
            document_meta,
            evidence=observation.evidence,
            fallback_raw_text=observation.source_name,
        ),
    }

    reference_range = _reference_range(observation)
    if reference_range:
        payload["reference_range"] = reference_range

    effective_time = document_meta.get("effective_time") or document_meta.get("collected_at")
    if isinstance(effective_time, str) and effective_time:
        payload["effective_time"] = effective_time

    return payload


def to_standard_panel(
    report: NormalizedReport,
    panel: str,
    standard_version: str = "0.1",
) -> StandardPanel:
    panel_code = _normalize_panel_code(panel)
    panel_meta = _PANEL_DEFINITIONS.get(panel_code, {"display": panel_code.title()})

    warnings = list(report.warnings)
    if panel_code not in _PANEL_DEFINITIONS:
        warnings.append(f"Unknown panel '{panel}', using LOCAL metadata")

    observations = [
        _observation_payload(
            observation,
            panel_code=panel_code,
            index=index + 1,
            document_meta=report.document.meta,
        )
        for index, observation in enumerate(report.observations)
    ]

    payload: dict[str, Any] = {
        "id": f"panel-{panel_code.lower()}-{uuid4().hex[:8]}",
        "resource_type": "panel",
        "standard_version": standard_version,
        "panel_code": {
            "system": "MEDLABS-PANEL",
            "code": panel_code,
            "display": panel_meta["display"],
        },
        "panel_name": panel_meta["display"],
        "status": "final",
        "observations": observations,
        "source": _source_trace(
            report.document.meta,
            fallback_raw_text=report.document.meta.get("panel_raw_text", panel_meta["display"]),
        ),
    }

    collected_at = report.document.meta.get("collected_at")
    if isinstance(collected_at, str) and collected_at:
        payload["collected_at"] = collected_at

    reported_at = report.document.meta.get("reported_at")
    if isinstance(reported_at, str) and reported_at:
        payload["reported_at"] = reported_at

    return StandardPanel(data=payload, warnings=warnings)
