from __future__ import annotations

from medlabs_sdk.core.ingest.base import Ingestor
from medlabs_sdk.core.models import RawDocument


class TextIngestor(Ingestor):
    def ingest(self, source: str) -> RawDocument:
        return RawDocument(text=source, source="inline-text")
