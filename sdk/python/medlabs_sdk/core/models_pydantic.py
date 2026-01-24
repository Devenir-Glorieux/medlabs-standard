from __future__ import annotations

from typing import Any, Optional, Union

try:
    from pydantic.v1 import BaseModel, Field
except ImportError:  # pragma: no cover - only triggered when pydantic is missing
    from pydantic import BaseModel, Field

import medlabs_sdk.core.models as dc

Evidence = dict[str, Any]
Value = Union[float, str, None]


class MedlabsBaseModel(BaseModel):
    class Config:
        extra = "forbid"


class RawDocumentModel(MedlabsBaseModel):
    text: str
    pages: list[str] = Field(default_factory=list)
    meta: dict[str, Any] = Field(default_factory=dict)
    artifacts: dict[str, Any] = Field(default_factory=dict)

    def to_dataclass(self) -> dc.RawDocument:
        return dc.RawDocument(
            text=self.text,
            pages=list(self.pages),
            meta=dict(self.meta),
            artifacts=dict(self.artifacts),
        )

    @classmethod
    def from_dataclass(cls, value: dc.RawDocument) -> "RawDocumentModel":
        return cls.parse_obj(
            {
                "text": value.text,
                "pages": value.pages,
                "meta": value.meta,
                "artifacts": value.artifacts,
            }
        )


class ExtractedFieldModel(MedlabsBaseModel):
    name_raw: str
    value_raw: str
    unit_raw: str
    ref_raw: str
    flags_raw: str
    evidence: Evidence
    confidence: float

    def to_dataclass(self) -> dc.ExtractedField:
        return dc.ExtractedField(
            name_raw=self.name_raw,
            value_raw=self.value_raw,
            unit_raw=self.unit_raw,
            ref_raw=self.ref_raw,
            flags_raw=self.flags_raw,
            evidence=dict(self.evidence),
            confidence=self.confidence,
        )

    @classmethod
    def from_dataclass(cls, value: dc.ExtractedField) -> "ExtractedFieldModel":
        return cls.parse_obj(
            {
                "name_raw": value.name_raw,
                "value_raw": value.value_raw,
                "unit_raw": value.unit_raw,
                "ref_raw": value.ref_raw,
                "flags_raw": value.flags_raw,
                "evidence": value.evidence,
                "confidence": value.confidence,
            }
        )


class ExtractedReportModel(MedlabsBaseModel):
    document: RawDocumentModel
    fields: list[ExtractedFieldModel] = Field(default_factory=list)
    meta: dict[str, Any] = Field(default_factory=dict)

    def to_dataclass(self) -> dc.ExtractedReport:
        return dc.ExtractedReport(
            document=self.document.to_dataclass(),
            fields=[field.to_dataclass() for field in self.fields],
            meta=dict(self.meta),
        )

    @classmethod
    def from_dataclass(cls, value: dc.ExtractedReport) -> "ExtractedReportModel":
        return cls.parse_obj(
            {
                "document": RawDocumentModel.from_dataclass(value.document),
                "fields": [ExtractedFieldModel.from_dataclass(field) for field in value.fields],
                "meta": value.meta,
            }
        )


class NormalizedObservationModel(MedlabsBaseModel):
    code: str
    value: Value
    unit: str
    ref_low: Optional[float] = None
    ref_high: Optional[float] = None
    source_name: str = ""
    confidence: float = 0.0
    evidence: Evidence = Field(default_factory=dict)

    def to_dataclass(self) -> dc.NormalizedObservation:
        return dc.NormalizedObservation(
            code=self.code,
            value=self.value,
            unit=self.unit,
            ref_low=self.ref_low,
            ref_high=self.ref_high,
            source_name=self.source_name,
            confidence=self.confidence,
            evidence=dict(self.evidence),
        )

    @classmethod
    def from_dataclass(cls, value: dc.NormalizedObservation) -> "NormalizedObservationModel":
        return cls.parse_obj(
            {
                "code": value.code,
                "value": value.value,
                "unit": value.unit,
                "ref_low": value.ref_low,
                "ref_high": value.ref_high,
                "source_name": value.source_name,
                "confidence": value.confidence,
                "evidence": value.evidence,
            }
        )


class NormalizedReportModel(MedlabsBaseModel):
    document: RawDocumentModel
    observations: list[NormalizedObservationModel] = Field(default_factory=list)
    meta: dict[str, Any] = Field(default_factory=dict)

    def to_dataclass(self) -> dc.NormalizedReport:
        return dc.NormalizedReport(
            document=self.document.to_dataclass(),
            observations=[obs.to_dataclass() for obs in self.observations],
            meta=dict(self.meta),
        )

    @classmethod
    def from_dataclass(cls, value: dc.NormalizedReport) -> "NormalizedReportModel":
        return cls.parse_obj(
            {
                "document": RawDocumentModel.from_dataclass(value.document),
                "observations": [
                    NormalizedObservationModel.from_dataclass(obs) for obs in value.observations
                ],
                "meta": value.meta,
            }
        )


class StandardPanelModel(MedlabsBaseModel):
    panel: str
    standard_version: str
    observations: list[dict[str, Any]] = Field(default_factory=list)
    meta: dict[str, Any] = Field(default_factory=dict)

    def to_dataclass(self) -> dc.StandardPanel:
        return dc.StandardPanel(
            panel=self.panel,
            standard_version=self.standard_version,
            observations=[dict(item) for item in self.observations],
            meta=dict(self.meta),
        )

    @classmethod
    def from_dataclass(cls, value: dc.StandardPanel) -> "StandardPanelModel":
        return cls.parse_obj(
            {
                "panel": value.panel,
                "standard_version": value.standard_version,
                "observations": value.observations,
                "meta": value.meta,
            }
        )


class ValidationResultModel(MedlabsBaseModel):
    is_valid: bool
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    details: dict[str, Any] = Field(default_factory=dict)

    def to_dataclass(self) -> dc.ValidationResult:
        return dc.ValidationResult(
            is_valid=self.is_valid,
            errors=list(self.errors),
            warnings=list(self.warnings),
            details=dict(self.details),
        )

    @classmethod
    def from_dataclass(cls, value: dc.ValidationResult) -> "ValidationResultModel":
        return cls.parse_obj(
            {
                "is_valid": value.is_valid,
                "errors": value.errors,
                "warnings": value.warnings,
                "details": value.details,
            }
        )


__all__ = [
    "ExtractedFieldModel",
    "ExtractedReportModel",
    "MedlabsBaseModel",
    "NormalizedObservationModel",
    "NormalizedReportModel",
    "RawDocumentModel",
    "StandardPanelModel",
    "ValidationResultModel",
]
