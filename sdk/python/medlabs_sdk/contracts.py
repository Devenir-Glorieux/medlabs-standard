from __future__ import annotations

from contextlib import AbstractContextManager
from typing import Any, Protocol


class LLMClient(Protocol):
    def extract_structured(
        self,
        *,
        prompt_name: str,
        prompt_version: str,
        input_text: str,
        output_schema: dict[str, Any],
        temperature: float = 0.0,
    ) -> dict[str, Any]:
        ...


class PromptProvider(Protocol):
    def get_prompt(self, *, prompt_name: str, prompt_version: str) -> str:
        ...


class StructuredGenerator(Protocol):
    def generate_structured(
        self,
        *,
        system_prompt: str,
        input_text: str,
        output_schema: dict[str, Any],
        temperature: float = 0.0,
    ) -> dict[str, Any]:
        ...


class Tracer(Protocol):
    def span(self, name: str, **attrs: Any) -> AbstractContextManager[None]:
        ...
