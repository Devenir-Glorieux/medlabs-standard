from __future__ import annotations

from pathlib import Path
from time import perf_counter
from typing import Any

from medlabs_sdk.contracts import LLMClient, Tracer
from medlabs_sdk.core.extract import AIExtractor
from medlabs_sdk.core.ingest import PdfIngestError, PdfIngestor, TextIngestor
from medlabs_sdk.core.map import to_standard_panel
from medlabs_sdk.core.models import PipelineResult, RawDocument
from medlabs_sdk.core.normalize import normalize
from medlabs_sdk.core.validate import validate_jsonschema
from medlabs_sdk.observability import configure_logging, get_logger
from medlabs_sdk.providers.noop_tracer import NoopTracer


class MedLabsPipeline:
    def __init__(
        self,
        *,
        llm_client: LLMClient,
        prompt_name: str,
        prompt_version: str,
        tracer: Tracer | None = None,
        schema_dir: str | Path | None = None,
        log_level: str = "INFO",
    ) -> None:
        configure_logging(log_level)
        self.logger = get_logger()
        self.tracer = tracer or NoopTracer()
        self.extractor = AIExtractor(
            llm_client,
            prompt_name=prompt_name,
            prompt_version=prompt_version,
            temperature=0.0,
        )
        self.pdf_ingestor = PdfIngestor()
        self.text_ingestor = TextIngestor()
        self.schema_dir = Path(schema_dir) if schema_dir else None

    def parse_text(
        self,
        text: str,
        *,
        panel: str,
        document_meta: dict[str, Any] | None = None,
    ) -> PipelineResult:
        start = perf_counter()
        document = self.text_ingestor.ingest(text)
        if document_meta:
            document.meta.update(document_meta)
        self._log_step(
            pipeline_step="ingest",
            duration_ms=self._elapsed_ms(start),
            status="ok",
            warning_count=0,
            error_count=0,
            source=document.source,
            pages=max(1, len(document.pages)),
            text_size=len(document.text),
        )
        return self._run_rest(document=document, panel=panel)

    def parse_pdf(
        self,
        source: str,
        *,
        panel: str,
        document_meta: dict[str, Any] | None = None,
    ) -> PipelineResult:
        start = perf_counter()
        try:
            with self.tracer.span("ingest", source=source):
                document = self.pdf_ingestor.ingest(source)
        except PdfIngestError:
            self._log_step(
                pipeline_step="ingest",
                duration_ms=self._elapsed_ms(start),
                status="error",
                warning_count=0,
                error_count=1,
                source=source,
                pages=0,
                text_size=0,
            )
            raise

        if document_meta:
            document.meta.update(document_meta)

        self._log_step(
            pipeline_step="ingest",
            duration_ms=self._elapsed_ms(start),
            status="ok",
            warning_count=0,
            error_count=0,
            source=source,
            pages=len(document.pages),
            text_size=len(document.text),
        )
        return self._run_rest(document=document, panel=panel)

    def _run_rest(self, *, document: RawDocument, panel: str) -> PipelineResult:
        extract_start = perf_counter()
        with self.tracer.span(
            "extract",
            prompt_name=self.extractor.prompt_name,
            prompt_version=self.extractor.prompt_version,
        ):
            extracted = self.extractor.extract(document)
        self._log_step(
            pipeline_step="extract",
            duration_ms=self._elapsed_ms(extract_start),
            status="ok",
            warning_count=len(extracted.warnings),
            error_count=0,
        )

        normalize_start = perf_counter()
        normalized = normalize(extracted)
        self._log_step(
            pipeline_step="normalize",
            duration_ms=self._elapsed_ms(normalize_start),
            status="ok",
            warning_count=len(normalized.warnings),
            error_count=0,
        )

        map_start = perf_counter()
        mapped = to_standard_panel(normalized, panel=panel)
        self._log_step(
            pipeline_step="map",
            duration_ms=self._elapsed_ms(map_start),
            status="ok",
            warning_count=len(mapped.warnings),
            error_count=0,
        )

        validate_start = perf_counter()
        validation = validate_jsonschema(
            mapped.data,
            panel_code=mapped.data.get("panel_code", {}).get("code"),
            schema_dir=self.schema_dir,
        )
        self._log_step(
            pipeline_step="validate",
            duration_ms=self._elapsed_ms(validate_start),
            status="ok" if validation.is_valid else "error",
            warning_count=len(validation.warnings),
            error_count=len(validation.errors),
        )

        return PipelineResult(
            document=document,
            extracted=extracted,
            normalized=normalized,
            mapped=mapped,
            validation=validation,
        )

    @staticmethod
    def _elapsed_ms(start: float) -> int:
        return int((perf_counter() - start) * 1000)

    def _log_step(
        self,
        *,
        pipeline_step: str,
        duration_ms: int,
        status: str,
        warning_count: int,
        error_count: int,
        **extra: Any,
    ) -> None:
        self.logger.info(
            "pipeline.step",
            pipeline_step=pipeline_step,
            duration_ms=duration_ms,
            status=status,
            warning_count=warning_count,
            error_count=error_count,
            **extra,
        )
