from abc import ABC, abstractmethod
from typing import Any

class LLMClient(ABC):
    @abstractmethod
    def complete(self, prompt: str, **kwargs: Any) -> str:
        raise NotImplementedError
