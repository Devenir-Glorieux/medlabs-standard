from medlabs_sdk.core.models import ExtractedReport, RawDocument
from medlabs_sdk.core.extract.base import Extractor
from medlabs_sdk.llm.base import LLMClient

class AIExtractor(Extractor):
    def __init__(self, client: "LLMClient") -> None:
        self.client = client

    def extract(self, document: RawDocument) -> ExtractedReport:
        raise NotImplementedError("AI extraction is not implemented")
