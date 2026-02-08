from __future__ import annotations

from medlabs_sdk.core.models import ExtractedReport, NormalizedObservation, NormalizedReport
from medlabs_sdk.core.normalize.names import canonicalize_name
from medlabs_sdk.core.normalize.numbers import parse_float, parse_range
from medlabs_sdk.core.normalize.units import normalize_unit


def normalize(report: ExtractedReport) -> NormalizedReport:
    warnings = list(report.warnings)
    observations: list[NormalizedObservation] = []

    for index, field in enumerate(report.fields):
        code = canonicalize_name(field.name_raw)
        if not code:
            warnings.append(f"Field {index} has empty name")
            continue

        numeric_value = parse_float(field.value_raw)
        normalized_value = numeric_value if numeric_value is not None else field.value_raw.strip()

        ref_low, ref_high = parse_range(field.ref_raw)
        if field.ref_raw.strip() and ref_low is None and ref_high is None:
            warnings.append(f"Field '{field.name_raw}' has unparsed reference range")

        observations.append(
            NormalizedObservation(
                code=code,
                value=normalized_value,
                unit=normalize_unit(field.unit_raw),
                ref_low=ref_low,
                ref_high=ref_high,
                source_name=field.name_raw,
                confidence=field.confidence,
                evidence=field.evidence,
                flags_raw=field.flags_raw,
            )
        )

    return NormalizedReport(
        document=report.document,
        observations=observations,
        warnings=warnings,
        meta=dict(report.meta),
    )
