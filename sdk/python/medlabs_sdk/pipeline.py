from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from time import perf_counter
from typing import TYPE_CHECKING, Any

from medlabs_sdk.contracts import LLMClient, Tracer
from medlabs_sdk.core.extract import AIExtractor
from medlabs_sdk.core.ingest import PdfIngestError, PdfIngestor, TextIngestor
from medlabs_sdk.core.map import to_standard_panel
from medlabs_sdk.core.models import (
    ExtractedReport,
    NormalizedReport,
    PipelineResult,
    RawDocument,
    StandardPanel,
    ValidationResult,
)
from medlabs_sdk.core.normalize import normalize
from medlabs_sdk.core.validate import validate_jsonschema
from medlabs_sdk.logger import configure_logger, get_logger
from medlabs_sdk.providers.noop_tracer import NoopTracer

if TYPE_CHECKING:
    from medlabs_sdk.config import MedLabsSettings


PipelineNodeHandler = Callable[["PipelineState"], None]
PipelineEdgePredicate = Callable[["PipelineState"], bool]


@dataclass
class PipelineStepState:
    pipeline_step: str
    duration_ms: int
    status: str
    warning_count: int
    error_count: int
    attrs: dict[str, Any] = field(default_factory=dict)


@dataclass
class PipelineState:
    panel: str
    document: RawDocument
    extracted: ExtractedReport | None = None
    normalized: NormalizedReport | None = None
    mapped: StandardPanel | None = None
    validation: ValidationResult | None = None
    steps: list[PipelineStepState] = field(default_factory=list)


@dataclass(frozen=True)
class PipelineEdge:
    target: str
    label: str = "always"
    predicate: PipelineEdgePredicate | None = None


@dataclass(frozen=True)
class PipelineNode:
    name: str
    handler: PipelineNodeHandler
    edges: tuple[PipelineEdge, ...] = ()


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
        configure_logger(log_level)
        self.logger = get_logger()
        self.tracer = tracer or NoopTracer()
        self.last_state: PipelineState | None = None
        self.extractor = AIExtractor(
            llm_client,
            prompt_name=prompt_name,
            prompt_version=prompt_version,
            temperature=0.0,
        )
        self.pdf_ingestor = PdfIngestor()
        self.text_ingestor = TextIngestor()
        self.schema_dir = Path(schema_dir) if schema_dir else None
        self._workflow_entry_node = "extract"
        self._workflow_nodes = self._build_workflow_nodes()
        self._assert_workflow_is_valid()

    @classmethod
    def from_env(cls) -> MedLabsPipeline:
        try:
            from medlabs_sdk.config import MedLabsSettings
        except ImportError as exc:
            raise RuntimeError(
                "Install provider extras to build pipeline from env: "
                "`uv sync --extra providers`"
            ) from exc

        return cls.from_settings(MedLabsSettings())

    @classmethod
    def from_settings(cls, settings: MedLabsSettings) -> MedLabsPipeline:
        try:
            from medlabs_sdk.providers import (
                LangfusePromptProvider,
                LangfuseTracer,
                NoopTracer,
                OpenAIClient,
                PromptedLLMClient,
            )
        except ImportError as exc:
            raise RuntimeError(
                "Provider modules are not available. Install provider extras: "
                "`uv sync --extra providers`"
            ) from exc

        prompt_provider = None
        has_langfuse_credentials = all(
            [settings.langfuse_public_key, settings.langfuse_secret_key, settings.langfuse_host]
        )
        if settings.enable_langfuse_prompts and has_langfuse_credentials:
            prompt_provider = LangfusePromptProvider(
                public_key=settings.langfuse_public_key,
                secret_key=settings.langfuse_secret_key,
                host=settings.langfuse_host,
            )

        generator = OpenAIClient(
            model=settings.openai_model,
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url,
        )
        llm_client = PromptedLLMClient(
            prompt_provider=prompt_provider,
            generator=generator,
            fallback_prompt=settings.prompt_fallback,
            strict_prompt_provider=settings.fail_on_prompt_error,
        )

        tracer: Tracer
        if settings.enable_tracing and has_langfuse_credentials:
            tracer = LangfuseTracer(
                public_key=settings.langfuse_public_key,
                secret_key=settings.langfuse_secret_key,
                host=settings.langfuse_host,
            )
        else:
            tracer = NoopTracer()

        return cls(
            llm_client=llm_client,
            prompt_name=settings.prompt_name,
            prompt_version=settings.prompt_version,
            tracer=tracer,
            schema_dir=settings.schema_dir_path(),
            log_level=settings.log_level,
        )

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
        state = PipelineState(panel=panel, document=document)
        self._record_step(
            state=state,
            pipeline_step="ingest",
            duration_ms=self._elapsed_ms(start),
            status="ok",
            warning_count=0,
            error_count=0,
            source=document.source,
            pages=max(1, len(document.pages)),
            text_size=len(document.text),
        )
        self._run_processing_workflow(state=state)
        self.last_state = state
        return self._result_from_state(state)

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
            self.logger.info(
                "pipeline.step",
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

        state = PipelineState(panel=panel, document=document)
        self._record_step(
            state=state,
            pipeline_step="ingest",
            duration_ms=self._elapsed_ms(start),
            status="ok",
            warning_count=0,
            error_count=0,
            source=source,
            pages=len(document.pages),
            text_size=len(document.text),
        )
        self._run_processing_workflow(state=state)
        self.last_state = state
        return self._result_from_state(state)

    @property
    def workflow_node_names(self) -> tuple[str, ...]:
        return tuple(self._workflow_nodes.keys())

    @property
    def workflow_edges(self) -> tuple[tuple[str, str, str], ...]:
        result: list[tuple[str, str, str]] = []
        for source, node in self._workflow_nodes.items():
            for edge in node.edges:
                result.append((source, edge.target, edge.label))
        return tuple(result)

    def _build_workflow_nodes(self) -> dict[str, PipelineNode]:
        return {
            "extract": PipelineNode(
                name="extract",
                handler=self._node_extract,
                edges=(PipelineEdge(target="normalize"),),
            ),
            "normalize": PipelineNode(
                name="normalize",
                handler=self._node_normalize,
                edges=(PipelineEdge(target="map"),),
            ),
            "map": PipelineNode(
                name="map",
                handler=self._node_map,
                edges=(PipelineEdge(target="validate"),),
            ),
            "validate": PipelineNode(name="validate", handler=self._node_validate),
        }

    def _assert_workflow_is_valid(self) -> None:
        if self._workflow_entry_node not in self._workflow_nodes:
            raise RuntimeError(f"Unknown workflow entry node: {self._workflow_entry_node}")

        for source, node in self._workflow_nodes.items():
            if source != node.name:
                raise RuntimeError(
                    "Workflow node key mismatch: "
                    f"key='{source}', node.name='{node.name}'"
                )
            for edge in node.edges:
                if edge.target not in self._workflow_nodes:
                    raise RuntimeError(
                        f"Workflow edge target '{edge.target}' does not exist"
                    )

    def _run_processing_workflow(self, *, state: PipelineState) -> None:
        node_name: str | None = self._workflow_entry_node
        max_steps = len(self._workflow_nodes) * 4
        executed_steps = 0

        while node_name is not None:
            executed_steps += 1
            if executed_steps > max_steps:
                raise RuntimeError("Workflow execution exceeded safe step limit")

            node = self._workflow_nodes[node_name]
            node.handler(state)
            node_name = self._resolve_next_node(node=node, state=state)

    def _resolve_next_node(self, *, node: PipelineNode, state: PipelineState) -> str | None:
        if not node.edges:
            return None

        matching_edges = [
            edge
            for edge in node.edges
            if edge.predicate is None or edge.predicate(state)
        ]
        if not matching_edges:
            return None

        if len(matching_edges) > 1:
            labels = ", ".join(edge.label for edge in matching_edges)
            raise RuntimeError(
                f"Workflow node '{node.name}' matched multiple outgoing edges: {labels}"
            )
        return matching_edges[0].target

    def _node_extract(self, state: PipelineState) -> None:
        extract_start = perf_counter()
        with self.tracer.span(
            "extract",
            prompt_name=self.extractor.prompt_name,
            prompt_version=self.extractor.prompt_version,
        ):
            state.extracted = self.extractor.extract(state.document)
        self._record_step(
            state=state,
            pipeline_step="extract",
            duration_ms=self._elapsed_ms(extract_start),
            status="ok",
            warning_count=len(state.extracted.warnings),
            error_count=0,
        )

    def _node_normalize(self, state: PipelineState) -> None:
        if state.extracted is None:
            raise RuntimeError("Pipeline state is missing extracted report")

        normalize_start = perf_counter()
        state.normalized = normalize(state.extracted)
        self._record_step(
            state=state,
            pipeline_step="normalize",
            duration_ms=self._elapsed_ms(normalize_start),
            status="ok",
            warning_count=len(state.normalized.warnings),
            error_count=0,
        )

    def _node_map(self, state: PipelineState) -> None:
        if state.normalized is None:
            raise RuntimeError("Pipeline state is missing normalized report")

        map_start = perf_counter()
        state.mapped = to_standard_panel(state.normalized, panel=state.panel)
        self._record_step(
            state=state,
            pipeline_step="map",
            duration_ms=self._elapsed_ms(map_start),
            status="ok",
            warning_count=len(state.mapped.warnings),
            error_count=0,
        )

    def _node_validate(self, state: PipelineState) -> None:
        if state.mapped is None:
            raise RuntimeError("Pipeline state is missing mapped panel")

        validate_start = perf_counter()
        state.validation = validate_jsonschema(
            state.mapped.data,
            panel_code=state.mapped.data.get("panel_code", {}).get("code"),
            schema_dir=self.schema_dir,
        )
        self._record_step(
            state=state,
            pipeline_step="validate",
            duration_ms=self._elapsed_ms(validate_start),
            status="ok" if state.validation.is_valid else "error",
            warning_count=len(state.validation.warnings),
            error_count=len(state.validation.errors),
        )

    def _result_from_state(self, state: PipelineState) -> PipelineResult:
        if (
            state.extracted is None
            or state.normalized is None
            or state.mapped is None
            or state.validation is None
        ):
            raise RuntimeError("Pipeline did not finish all steps")

        return PipelineResult(
            document=state.document,
            extracted=state.extracted,
            normalized=state.normalized,
            mapped=state.mapped,
            validation=state.validation,
        )

    @staticmethod
    def _elapsed_ms(start: float) -> int:
        return int((perf_counter() - start) * 1000)

    def _record_step(
        self,
        *,
        state: PipelineState,
        pipeline_step: str,
        duration_ms: int,
        status: str,
        warning_count: int,
        error_count: int,
        **extra: Any,
    ) -> None:
        state.steps.append(
            PipelineStepState(
                pipeline_step=pipeline_step,
                duration_ms=duration_ms,
                status=status,
                warning_count=warning_count,
                error_count=error_count,
                attrs=dict(extra),
            )
        )
        self.logger.info(
            "pipeline.step",
            pipeline_step=pipeline_step,
            duration_ms=duration_ms,
            status=status,
            warning_count=warning_count,
            error_count=error_count,
            **extra,
        )
