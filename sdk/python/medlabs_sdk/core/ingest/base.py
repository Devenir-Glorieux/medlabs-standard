from __future__ import annotations

from abc import ABC, abstractmethod

from medlabs_sdk.core.models import RawDocument


class Ingestor(ABC):
    @abstractmethod
    def ingest(self, source: str) -> RawDocument:
        raise NotImplementedError
