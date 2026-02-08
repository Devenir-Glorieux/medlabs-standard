from __future__ import annotations

import json
from typing import Any

from medlabs_sdk.pipeline import MedLabsPipeline


class MockLLMClient:
    def extract_structured(
        self,
        *,
        prompt_name: str,
        prompt_version: str,
        input_text: str,
        output_schema: dict[str, Any],
        temperature: float = 0.0,
    ) -> dict[str, Any]:
        del prompt_name, prompt_version, input_text, output_schema, temperature
        return {
            "fields": [
                {
                    "name_raw": "WBC",
                    "value_raw": "5,4",
                    "unit_raw": "x10^9/L",
                    "ref_raw": "4.0-10.0",
                    "confidence": 0.95,
                    "evidence": {"page": 1, "line": 10, "raw_text": "WBC 5,4 x10^9/L (4.0-10.0)"},
                },
                {
                    "name_raw": "HGB",
                    "value_raw": "14.1",
                    "unit_raw": "g/dL",
                    "ref_raw": "13.0-17.0",
                    "confidence": 0.92,
                    "evidence": {"page": 1, "line": 11, "raw_text": "HGB 14.1 g/dL (13.0-17.0)"},
                },
            ]
        }


def main() -> None:
    pipeline = MedLabsPipeline(
        llm_client=MockLLMClient(),
        prompt_name="medlabs.extract",
        prompt_version="v1",
    )

    result = pipeline.parse_text(
        text="mock lab report",
        panel="CBC",
        document_meta={
            "document_id": "example-mock-001",
            "lab_name": "Example Lab",
            "report_date": "2026-02-07",
            "panel_raw_text": "Complete Blood Count",
        },
    )

    print("=== mapped payload ===")
    print(json.dumps(result.mapped.data, indent=2, ensure_ascii=False))
    print("=== validation ===")
    print(
        json.dumps(
            {
                "is_valid": result.validation.is_valid,
                "issues": [issue.__dict__ for issue in result.validation.issues],
            },
            indent=2,
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
