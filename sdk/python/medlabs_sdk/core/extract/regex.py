from __future__ import annotations

import re

from medlabs_sdk.core.extract.base import Extractor
from medlabs_sdk.core.models import ExtractedField, ExtractedReport, RawDocument

_LINE_RE = re.compile(
    r"^\s*(?P<name>[A-Za-z][A-Za-z0-9_\-/ ]{1,60})[:\s]+"
    r"(?P<value>-?[0-9]+(?:[\.,][0-9]+)?|[A-Za-z]+)"
    r"(?:\s+(?P<unit>[%A-Za-z0-9\*\^/]+))?"
    r"(?:\s*\((?P<ref>[^)]{1,40})\))?\s*$"
)


class RegexExtractor(Extractor):
    def extract(self, document: RawDocument) -> ExtractedReport:
        fields: list[ExtractedField] = []
        for line in document.text.splitlines():
            match = _LINE_RE.match(line)
            if not match:
                continue
            groups = match.groupdict()
            fields.append(
                ExtractedField(
                    name_raw=(groups.get("name") or "").strip(),
                    value_raw=(groups.get("value") or "").strip(),
                    unit_raw=(groups.get("unit") or "").strip(),
                    ref_raw=(groups.get("ref") or "").strip(),
                    evidence={"raw_text": line.strip()},
                    confidence=0.3,
                )
            )

        warnings: list[str] = []
        if not fields:
            warnings.append("Regex extractor could not parse any fields")

        return ExtractedReport(document=document, fields=fields, warnings=warnings)
