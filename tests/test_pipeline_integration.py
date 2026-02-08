from __future__ import annotations

from typing import Any

from medlabs_sdk.pipeline import MedLabsPipeline
from medlabs_sdk.providers.noop_tracer import NoopTracer


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
                    "evidence": {"line": 10, "page": 1, "raw_text": "WBC 5,4 x10^9/L (4.0-10.0)"},
                    "confidence": 0.95,
                },
                {
                    "name_raw": "RBC",
                    "value_raw": "4.65",
                    "unit_raw": "x10^12/L",
                    "ref_raw": "4.2-5.6",
                    "evidence": {"line": 11, "page": 1, "raw_text": "RBC 4.65 x10^12/L (4.2-5.6)"},
                    "confidence": 0.94,
                },
                {
                    "name_raw": "HGB",
                    "value_raw": "14.1",
                    "unit_raw": "g/dL",
                    "ref_raw": "13.0-17.0",
                    "evidence": {"line": 12, "page": 1, "raw_text": "HGB 14.1 g/dL (13.0-17.0)"},
                    "confidence": 0.92,
                },
            ]
        }


def test_pipeline_end_to_end_with_mock_llm() -> None:
    pipeline = MedLabsPipeline(
        llm_client=MockLLMClient(),
        prompt_name="medlabs.extract",
        prompt_version="v1",
        tracer=NoopTracer(),
    )

    result = pipeline.parse_text(
        "mock input",
        panel="CBC",
        document_meta={
            "document_id": "doc-123",
            "lab_name": "Integration Lab",
            "report_date": "2026-02-07",
            "panel_raw_text": "Complete Blood Count",
        },
    )

    assert result.validation.is_valid
    assert result.mapped.data["panel_code"]["code"] == "CBC"
    assert len(result.mapped.data["observations"]) == 3
    assert pipeline.workflow_node_names == ("extract", "normalize", "map", "validate")
    assert pipeline.workflow_edges == (
        ("extract", "normalize", "always"),
        ("normalize", "map", "always"),
        ("map", "validate", "always"),
    )
    assert pipeline.last_state is not None
    assert [step.pipeline_step for step in pipeline.last_state.steps] == [
        "ingest",
        "extract",
        "normalize",
        "map",
        "validate",
    ]
