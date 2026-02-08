from __future__ import annotations

import logging
from typing import Any

from medlabs_sdk.contracts import PromptProvider, StructuredGenerator

_LOGGER = logging.getLogger(__name__)
_DEFAULT_FALLBACK_PROMPT = "Извлеки согласно схемы и верни только JSON."


class PromptedLLMClient:
    """Adapter that composes prompt storage with model transport.

    - PromptProvider resolves prompt by (name, version)
    - StructuredGenerator performs model inference
    """

    def __init__(
        self,
        *,
        prompt_provider: PromptProvider | None,
        generator: StructuredGenerator,
        fallback_prompt: str = _DEFAULT_FALLBACK_PROMPT,
        strict_prompt_provider: bool = False,
    ) -> None:
        self.prompt_provider = prompt_provider
        self.generator = generator
        self.fallback_prompt = fallback_prompt
        self.strict_prompt_provider = strict_prompt_provider

    def extract_structured(
        self,
        *,
        prompt_name: str,
        prompt_version: str,
        input_text: str,
        output_schema: dict[str, Any],
        temperature: float = 0.0,
    ) -> dict[str, Any]:
        system_prompt = self._resolve_prompt(
            prompt_name=prompt_name,
            prompt_version=prompt_version,
        )
        return self.generator.generate_structured(
            system_prompt=system_prompt,
            input_text=input_text,
            output_schema=output_schema,
            temperature=temperature,
        )

    def _resolve_prompt(self, *, prompt_name: str, prompt_version: str) -> str:
        if self.prompt_provider is None:
            if self.strict_prompt_provider:
                raise RuntimeError("Prompt provider is required but not configured")
            return self.fallback_prompt

        try:
            prompt = self.prompt_provider.get_prompt(
                prompt_name=prompt_name,
                prompt_version=prompt_version,
            )
        except Exception:
            if self.strict_prompt_provider:
                raise
            _LOGGER.warning(
                "Prompt provider failed, using fallback prompt",
                extra={
                    "prompt_name": prompt_name,
                    "prompt_version": prompt_version,
                },
            )
            return self.fallback_prompt

        if not isinstance(prompt, str) or not prompt.strip():
            if self.strict_prompt_provider:
                raise RuntimeError("Prompt provider returned empty prompt")
            _LOGGER.warning(
                "Prompt provider returned empty prompt, using fallback",
                extra={
                    "prompt_name": prompt_name,
                    "prompt_version": prompt_version,
                },
            )
            return self.fallback_prompt

        return prompt
