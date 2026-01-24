from medlabs_sdk.core.models import RawDocument
from medlabs_sdk.core.ingest.base import Ingestor

class PdfIngestor(Ingestor):
    def ingest(self, source: str) -> RawDocument:
        raise NotImplementedError("PDF ingest is not implemented")
