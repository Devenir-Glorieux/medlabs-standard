from typing import Any

from medlabs_sdk.core.models import NormalizedObservation, NormalizedReport, StandardPanel

def _observation_to_dict(obs: NormalizedObservation) -> dict[str, Any]:
    return {
        "code": obs.code,
        "value": obs.value,
        "unit": obs.unit,
        "ref_low": obs.ref_low,
        "ref_high": obs.ref_high,
        "source_name": obs.source_name,
        "confidence": obs.confidence,
        "evidence": obs.evidence,
    }


def to_standard_panel(
    report: NormalizedReport,
    panel: str,
    standard_version: str = "0.1",
) -> StandardPanel:
    observations: list[dict[str, Any]] = [_observation_to_dict(obs) for obs in report.observations]
    return StandardPanel(
        panel=panel,
        standard_version=standard_version,
        observations=observations,
        meta=report.meta,
    )
