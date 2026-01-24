from abc import ABC, abstractmethod

from medlabs_sdk.core.models import ExtractedReport, RawDocument

class Extractor(ABC):
    @abstractmethod
    def extract(self, document: RawDocument) -> ExtractedReport:
        raise NotImplementedError
