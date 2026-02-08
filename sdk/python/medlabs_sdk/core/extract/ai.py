from __future__ import annotations

from typing import Any

from medlabs_sdk.contracts import LLMClient
from medlabs_sdk.core.extract.base import Extractor
from medlabs_sdk.core.models import ExtractedField, ExtractedReport, RawDocument

EXTRACTION_OUTPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "required": ["fields"],
    "properties": {
        "fields": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["name_raw", "value_raw"],
                "properties": {
                    "name_raw": {"type": "string"},
                    "value_raw": {"type": "string"},
                    "unit_raw": {"type": "string"},
                    "ref_raw": {"type": "string"},
                    "flags_raw": {"type": "string"},
                    "confidence": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                    "evidence": {"type": "object"},
                },
                "additionalProperties": True,
            },
        }
    },
    "additionalProperties": True,
}


def _string(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _float_0_1(value: Any) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return 0.0
    return max(0.0, min(number, 1.0))


class AIExtractor(Extractor):
    def __init__(
        self,
        client: LLMClient,
        *,
        prompt_name: str,
        prompt_version: str,
        temperature: float = 0.0,
    ) -> None:
        self.client = client
        self.prompt_name = prompt_name
        self.prompt_version = prompt_version
        self.temperature = temperature

    def extract(self, document: RawDocument) -> ExtractedReport:
        payload = self.client.extract_structured(
            prompt_name=self.prompt_name,
            prompt_version=self.prompt_version,
            input_text=document.text,
            output_schema=EXTRACTION_OUTPUT_SCHEMA,
            temperature=self.temperature,
        )

        warnings: list[str] = []
        raw_fields = payload.get("fields", [])
        if not isinstance(raw_fields, list):
            warnings.append("Extractor output has invalid fields format")
            raw_fields = []

        fields: list[ExtractedField] = []
        for index, item in enumerate(raw_fields):
            if not isinstance(item, dict):
                warnings.append(f"fields[{index}] is not an object")
                continue

            name_raw = _string(item.get("name_raw"))
            value_raw = _string(item.get("value_raw"))
            if not name_raw or not value_raw:
                warnings.append(f"fields[{index}] is missing name_raw or value_raw")
                continue

            evidence = item.get("evidence", {})
            if not isinstance(evidence, dict):
                evidence = {}

            fields.append(
                ExtractedField(
                    name_raw=name_raw,
                    value_raw=value_raw,
                    unit_raw=_string(item.get("unit_raw")),
                    ref_raw=_string(item.get("ref_raw")),
                    flags_raw=_string(item.get("flags_raw")),
                    evidence=evidence,
                    confidence=_float_0_1(item.get("confidence")),
                )
            )

        return ExtractedReport(
            document=document,
            fields=fields,
            warnings=warnings,
            meta={
                "prompt_name": self.prompt_name,
                "prompt_version": self.prompt_version,
            },
        )
