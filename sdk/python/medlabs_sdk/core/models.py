from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional, Union

Evidence = dict[str, Any]
Value = Union[float, str, None]


@dataclass
class RawDocument:
    text: str
    pages: list[str] = field(default_factory=list)
    meta: dict[str, Any] = field(default_factory=dict)
    artifacts: dict[str, Any] = field(default_factory=dict)


@dataclass
class ExtractedField:
    name_raw: str
    value_raw: str
    unit_raw: str
    ref_raw: str
    flags_raw: str
    evidence: Evidence
    confidence: float


@dataclass
class ExtractedReport:
    document: RawDocument
    fields: list[ExtractedField] = field(default_factory=list)
    meta: dict[str, Any] = field(default_factory=dict)


@dataclass
class NormalizedObservation:
    code: str
    value: Value
    unit: str
    ref_low: Optional[float] = None
    ref_high: Optional[float] = None
    source_name: str = ""
    confidence: float = 0.0
    evidence: Evidence = field(default_factory=dict)


@dataclass
class NormalizedReport:
    document: RawDocument
    observations: list[NormalizedObservation] = field(default_factory=list)
    meta: dict[str, Any] = field(default_factory=dict)


@dataclass
class StandardPanel:
    panel: str
    standard_version: str
    observations: list[dict[str, Any]] = field(default_factory=list)
    meta: dict[str, Any] = field(default_factory=dict)


@dataclass
class ValidationResult:
    is_valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    details: dict[str, Any] = field(default_factory=dict)
