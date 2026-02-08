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
    "mcv": {
        "system": "LOINC",
        "code": "787-2",
        "display": "MCV [Entitic volume] by Automated count",
    },
    "mch": {
        "system": "LOINC",
        "code": "785-6",
        "display": "MCH [Entitic mass] by Automated count",
    },
    "mchc": {
        "system": "LOINC",
        "code": "786-4",
        "display": "MCHC [Mass/volume] by Automated count",
    },
    "rdw": {"system": "LOINC", "code": "788-0", "display": "Erythrocyte distribution width"},
    "mpv": {
        "system": "LOINC",
        "code": "32623-1",
        "display": "Platelet mean volume [Entitic volume] in Blood",
    },
    "pdw": {"system": "LOCAL", "code": "PDW", "display": "Platelet distribution width"},
    "pct": {"system": "LOCAL", "code": "PCT", "display": "Plateletcrit"},
    "neutrophils_abs": {
        "system": "LOCAL",
        "code": "NEUT_ABS",
        "display": "Neutrophils (absolute)",
    },
    "neutrophils_pct": {
        "system": "LOCAL",
        "code": "NEUT_PCT",
        "display": "Neutrophils (%)",
    },
    "lymphocytes_abs": {
        "system": "LOCAL",
        "code": "LYMPH_ABS",
        "display": "Lymphocytes (absolute)",
    },
    "lymphocytes_pct": {
        "system": "LOCAL",
        "code": "LYMPH_PCT",
        "display": "Lymphocytes (%)",
    },
    "monocytes_abs": {"system": "LOCAL", "code": "MONO_ABS", "display": "Monocytes (absolute)"},
    "monocytes_pct": {"system": "LOCAL", "code": "MONO_PCT", "display": "Monocytes (%)"},
    "eosinophils_abs": {
        "system": "LOCAL",
        "code": "EO_ABS",
        "display": "Eosinophils (absolute)",
    },
    "eosinophils_pct": {"system": "LOCAL", "code": "EO_PCT", "display": "Eosinophils (%)"},
    "basophils_abs": {"system": "LOCAL", "code": "BASO_ABS", "display": "Basophils (absolute)"},
    "basophils_pct": {"system": "LOCAL", "code": "BASO_PCT", "display": "Basophils (%)"},
    "esr": {"system": "LOINC", "code": "4537-7", "display": "Erythrocyte sedimentation rate"},
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
    "urine_ph": {"system": "LOCAL", "code": "URINE_PH", "display": "Urine pH"},
    "protein": {"system": "LOCAL", "code": "PROTEIN", "display": "Protein"},
    "urine_protein": {"system": "LOCAL", "code": "URINE_PROTEIN", "display": "Urine protein"},
    "urine_glucose": {"system": "LOCAL", "code": "URINE_GLUCOSE", "display": "Urine glucose"},
    "ketones": {"system": "LOCAL", "code": "KETONES", "display": "Ketones"},
    "urine_bilirubin": {
        "system": "LOCAL",
        "code": "URINE_BILIRUBIN",
        "display": "Urine bilirubin",
    },
    "urine_urobilinogen": {
        "system": "LOCAL",
        "code": "URINE_UROBILINOGEN",
        "display": "Urine urobilinogen",
    },
    "nitrite": {"system": "LOCAL", "code": "NITRITE", "display": "Nitrite"},
    "leukocyte_esterase": {
        "system": "LOCAL",
        "code": "LEUK_ESTERASE",
        "display": "Leukocyte esterase",
    },
    "urine_color": {"system": "LOCAL", "code": "URINE_COLOR", "display": "Urine color"},
    "urine_clarity": {"system": "LOCAL", "code": "URINE_CLARITY", "display": "Urine clarity"},
    "urine_leukocytes": {
        "system": "LOCAL",
        "code": "URINE_LEUKOCYTES",
        "display": "Urine leukocytes",
    },
    "urine_erythrocytes": {
        "system": "LOCAL",
        "code": "URINE_ERYTHROCYTES",
        "display": "Urine erythrocytes",
    },
    "urine_non_lysed_erythrocytes": {
        "system": "LOCAL",
        "code": "URINE_NON_LYSED_ERYTHROCYTES",
        "display": "Urine non-lysed erythrocytes",
    },
    "urine_hemoglobin": {
        "system": "LOCAL",
        "code": "URINE_HEMOGLOBIN",
        "display": "Urine hemoglobin",
    },
    "urine_leukocyte_clumps": {
        "system": "LOCAL",
        "code": "URINE_LEUKOCYTE_CLUMPS",
        "display": "Urine leukocyte clumps",
    },
    "epithelial_cells": {
        "system": "LOCAL",
        "code": "EPITHELIAL_CELLS",
        "display": "Epithelial cells",
    },
    "squamous_epithelial_cells": {
        "system": "LOCAL",
        "code": "SQUAMOUS_EPITHELIAL_CELLS",
        "display": "Squamous epithelial cells",
    },
    "non_squamous_epithelial_cells": {
        "system": "LOCAL",
        "code": "NON_SQUAMOUS_EPITHELIAL_CELLS",
        "display": "Non-squamous epithelial cells",
    },
    "transitional_epithelial_cells": {
        "system": "LOCAL",
        "code": "TRANSITIONAL_EPITHELIAL_CELLS",
        "display": "Transitional epithelial cells",
    },
    "renal_tubular_epithelial_cells": {
        "system": "LOCAL",
        "code": "RENAL_TUBULAR_EPITHELIAL_CELLS",
        "display": "Renal tubular epithelial cells",
    },
    "casts": {"system": "LOCAL", "code": "CASTS", "display": "Casts"},
    "hyaline_casts": {"system": "LOCAL", "code": "HYALINE_CASTS", "display": "Hyaline casts"},
    "non_hyaline_casts": {
        "system": "LOCAL",
        "code": "NON_HYALINE_CASTS",
        "display": "Non-hyaline casts",
    },
    "bacteria": {"system": "LOCAL", "code": "BACTERIA", "display": "Bacteria"},
    "oxalate_crystals": {
        "system": "LOCAL",
        "code": "OXALATE_CRYSTALS",
        "display": "Oxalate crystals",
    },
    "yeast": {"system": "LOCAL", "code": "YEAST", "display": "Yeast-like cells"},
    "sperm": {"system": "LOCAL", "code": "SPERM", "display": "Spermatozoa"},
    "mucus": {"system": "LOCAL", "code": "MUCUS", "display": "Mucus"},
}

_PANEL_ALLOWED_CODES: dict[str, set[str]] = {
    "CBC": {
        "wbc",
        "rbc",
        "hemoglobin",
        "hematocrit",
        "platelets",
        "mcv",
        "mch",
        "mchc",
        "rdw",
        "mpv",
        "pct",
        "pdw",
        "neutrophils_abs",
        "neutrophils_pct",
        "lymphocytes_abs",
        "lymphocytes_pct",
        "monocytes_abs",
        "monocytes_pct",
        "eosinophils_abs",
        "eosinophils_pct",
        "basophils_abs",
        "basophils_pct",
        "esr",
    },
    "BIOCHEM": {"glucose", "creatinine", "urea", "alt", "ast"},
    "URINALYSIS": {
        "color",
        "appearance",
        "specific_gravity",
        "ph",
        "urine_ph",
        "protein",
        "urine_protein",
        "urine_glucose",
        "ketones",
        "nitrite",
        "leukocyte_esterase",
        "urine_color",
        "urine_clarity",
        "urine_bilirubin",
        "urine_urobilinogen",
        "urine_leukocytes",
        "urine_erythrocytes",
        "urine_non_lysed_erythrocytes",
        "urine_hemoglobin",
        "urine_leukocyte_clumps",
        "epithelial_cells",
        "squamous_epithelial_cells",
        "non_squamous_epithelial_cells",
        "transitional_epithelial_cells",
        "renal_tubular_epithelial_cells",
        "casts",
        "hyaline_casts",
        "non_hyaline_casts",
        "bacteria",
        "oxalate_crystals",
        "yeast",
        "sperm",
        "mucus",
    },
}

_PANEL_CODE_ALIASES: dict[str, dict[str, str]] = {
    "CBC": {"leukocytes": "wbc", "erythrocytes": "rbc"},
    "URINALYSIS": {
        "leukocytes": "urine_leukocytes",
        "erythrocytes": "urine_erythrocytes",
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
        "ОБЩИЙ АНАЛИЗ КРОВИ": "CBC",
        "БИОХИМИЯ": "BIOCHEM",
        "ОБЩИЙ АНАЛИЗ МОЧИ": "URINALYSIS",
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


def _observation_code(*, observation_code: str, source_name: str) -> dict[str, str]:
    coding = _OBSERVATION_CODE_MAP.get(observation_code)
    if coding:
        return coding

    display = source_name or observation_code.replace("_", " ").title()
    return {
        "system": "LOCAL",
        "code": observation_code.upper(),
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


def _resolve_code_for_panel(observation: NormalizedObservation, *, panel_code: str) -> str:
    if observation.code == "leukocytes":
        if observation.unit == "10*9/L":
            return "wbc"
        if observation.unit == "{cells}/uL":
            return "urine_leukocytes"

    if observation.code == "erythrocytes":
        if observation.unit == "10*12/L":
            return "rbc"
        if observation.unit == "{cells}/uL":
            return "urine_erythrocytes"

    panel_aliases = _PANEL_CODE_ALIASES.get(panel_code, {})
    aliased_code = panel_aliases.get(observation.code)
    if aliased_code:
        return aliased_code

    return observation.code


def _filter_observations_for_panel(
    observations: list[NormalizedObservation],
    *,
    panel_code: str,
) -> tuple[list[tuple[NormalizedObservation, str]], list[str]]:
    allowed_codes = _PANEL_ALLOWED_CODES.get(panel_code)
    resolved_observations = [
        (observation, _resolve_code_for_panel(observation, panel_code=panel_code))
        for observation in observations
    ]
    if not allowed_codes:
        return resolved_observations, []

    included: list[tuple[NormalizedObservation, str]] = []
    dropped: list[str] = []
    for observation, resolved_code in resolved_observations:
        if resolved_code in allowed_codes:
            included.append((observation, resolved_code))
            continue
        dropped.append(observation.source_name or observation.code)

    if not dropped:
        return included, []

    if not included:
        return resolved_observations, [
            (
                f"Panel filter for '{panel_code}' matched nothing, "
                "kept all observations as fallback"
            )
        ]

    sample = ", ".join(dropped[:3])
    suffix = "..." if len(dropped) > 3 else ""
    return included, [
        (
            f"Filtered {len(dropped)} observations outside panel '{panel_code}': "
            f"{sample}{suffix}"
        )
    ]


def _observation_payload(
    observation: NormalizedObservation,
    *,
    observation_code: str,
    panel_code: str,
    index: int,
    document_meta: dict[str, Any],
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "id": f"obs-{panel_code.lower()}-{index:03d}-{uuid4().hex[:6]}",
        "resource_type": "observation",
        "code": _observation_code(
            observation_code=observation_code,
            source_name=observation.source_name,
        ),
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

    filtered_observations, filter_warnings = _filter_observations_for_panel(
        report.observations,
        panel_code=panel_code,
    )
    warnings.extend(filter_warnings)

    observations = [
        _observation_payload(
            observation=observation,
            observation_code=observation_code,
            panel_code=panel_code,
            index=index + 1,
            document_meta=report.document.meta,
        )
        for index, (observation, observation_code) in enumerate(filtered_observations)
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
