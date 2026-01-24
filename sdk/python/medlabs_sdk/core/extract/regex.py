from medlabs_sdk.core.models import ExtractedReport, RawDocument
from medlabs_sdk.core.extract.base import Extractor

class RegexExtractor(Extractor):
    def extract(self, document: RawDocument) -> ExtractedReport:
        raise NotImplementedError("Regex extraction is not implemented")
