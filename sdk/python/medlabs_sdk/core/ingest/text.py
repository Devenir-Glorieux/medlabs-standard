from medlabs_sdk.core.models import RawDocument
from medlabs_sdk.core.ingest.base import Ingestor

class TextIngestor(Ingestor):
    def ingest(self, source: str) -> RawDocument:
        return RawDocument(text=source)
