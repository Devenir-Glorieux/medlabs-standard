from medlabs_sdk.core.models import ExtractedReport, NormalizedObservation, NormalizedReport
from medlabs_sdk.core.normalize.names import canonicalize_name
from medlabs_sdk.core.normalize.numbers import parse_float, parse_range
from medlabs_sdk.core.normalize.units import normalize_unit

def normalize(report: ExtractedReport) -> NormalizedReport:
    observations: list[NormalizedObservation] = []
    for field in report.fields:
        value = parse_float(field.value_raw)
        if value is None:
            value_out = field.value_raw
        else:
            value_out = value
        ref_low, ref_high = parse_range(field.ref_raw)
        observations.append(
            NormalizedObservation(
                code=canonicalize_name(field.name_raw),
                value=value_out,
                unit=normalize_unit(field.unit_raw),
                ref_low=ref_low,
                ref_high=ref_high,
                source_name=field.name_raw,
                confidence=field.confidence,
                evidence=field.evidence,
            )
        )
    return NormalizedReport(document=report.document, observations=observations, meta=report.meta)
