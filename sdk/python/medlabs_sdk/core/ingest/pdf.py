from __future__ import annotations

from medlabs_sdk.core.ingest.base import Ingestor
from medlabs_sdk.core.models import RawDocument


class PdfIngestError(RuntimeError):
    pass


class PdfIngestor(Ingestor):
    def ingest(self, source: str) -> RawDocument:
        try:
            from pypdf import PdfReader
        except ImportError as exc:  # pragma: no cover - dependency error path
            raise RuntimeError("Install 'pypdf' to use PdfIngestor") from exc

        reader = PdfReader(source)
        pages: list[str] = []
        for page in reader.pages:
            pages.append((page.extract_text() or "").strip())

        text = "\n\n".join(chunk for chunk in pages if chunk)
        if not text.strip():
            raise PdfIngestError("PDF is scanned, OCR required")

        return RawDocument(
            text=text,
            pages=pages,
            source=source,
            meta={"page_count": len(pages), "text_size": len(text)},
        )
