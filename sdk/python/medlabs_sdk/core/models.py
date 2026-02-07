from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

Evidence = dict[str, Any]
Value = float | str | bool | None
Severity = Literal["error", "warning"]


@dataclass
class RawDocument:
    text: str
    pages: list[str] = field(default_factory=list)
    source: str = ""
    meta: dict[str, Any] = field(default_factory=dict)
    artifacts: dict[str, Any] = field(default_factory=dict)


@dataclass
class ExtractedField:
    name_raw: str
    value_raw: str
    unit_raw: str = ""
    ref_raw: str = ""
    flags_raw: str = ""
    evidence: Evidence = field(default_factory=dict)
    confidence: float = 0.0


@dataclass
class ExtractedReport:
    document: RawDocument
    fields: list[ExtractedField] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    meta: dict[str, Any] = field(default_factory=dict)


@dataclass
class NormalizedObservation:
    code: str
    value: Value
    unit: str
    ref_low: float | None = None
    ref_high: float | None = None
    source_name: str = ""
    confidence: float = 0.0
    evidence: Evidence = field(default_factory=dict)
    flags_raw: str = ""


@dataclass
class NormalizedReport:
    document: RawDocument
    observations: list[NormalizedObservation] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    meta: dict[str, Any] = field(default_factory=dict)


@dataclass
class StandardPanel:
    data: dict[str, Any]
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return dict(self.data)


@dataclass
class ValidationIssue:
    path: str
    description: str
    severity: Severity


@dataclass
class ValidationResult:
    is_valid: bool
    issues: list[ValidationIssue] = field(default_factory=list)

    @property
    def errors(self) -> list[ValidationIssue]:
        return [issue for issue in self.issues if issue.severity == "error"]

    @property
    def warnings(self) -> list[ValidationIssue]:
        return [issue for issue in self.issues if issue.severity == "warning"]


@dataclass
class PipelineResult:
    document: RawDocument
    extracted: ExtractedReport
    normalized: NormalizedReport
    mapped: StandardPanel
    validation: ValidationResult
