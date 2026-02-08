from __future__ import annotations

import pytest
from medlabs_sdk.providers.prompted_llm_client import PromptedLLMClient


class StubPromptProvider:
    def get_prompt(self, *, prompt_name: str, prompt_version: str) -> str:
        return f"prompt:{prompt_name}:{prompt_version}"


class StubGenerator:
    def __init__(self) -> None:
        self.called_with: dict | None = None

    def generate_structured(
        self,
        *,
        system_prompt: str,
        input_text: str,
        output_schema: dict,
        temperature: float = 0.0,
    ) -> dict:
        self.called_with = {
            "system_prompt": system_prompt,
            "input_text": input_text,
            "output_schema": output_schema,
            "temperature": temperature,
        }
        return {"fields": []}


def test_prompted_llm_client_composes_prompt_and_generator() -> None:
    generator = StubGenerator()
    client = PromptedLLMClient(
        prompt_provider=StubPromptProvider(),
        generator=generator,
    )

    payload = client.extract_structured(
        prompt_name="medlabs.extract",
        prompt_version="v1",
        input_text="hello",
        output_schema={"type": "object"},
        temperature=0.1,
    )

    assert payload == {"fields": []}
    assert generator.called_with is not None
    assert generator.called_with["system_prompt"] == "prompt:medlabs.extract:v1"


def test_prompted_llm_client_uses_fallback_without_provider() -> None:
    generator = StubGenerator()
    client = PromptedLLMClient(
        prompt_provider=None,
        generator=generator,
        fallback_prompt="fallback prompt",
    )

    payload = client.extract_structured(
        prompt_name="ignored",
        prompt_version="ignored",
        input_text="hello",
        output_schema={"type": "object"},
    )

    assert payload == {"fields": []}
    assert generator.called_with is not None
    assert generator.called_with["system_prompt"] == "fallback prompt"


class FailingPromptProvider:
    def get_prompt(self, *, prompt_name: str, prompt_version: str) -> str:
        del prompt_name, prompt_version
        raise RuntimeError("prompt error")


def test_prompted_llm_client_falls_back_on_prompt_error() -> None:
    generator = StubGenerator()
    client = PromptedLLMClient(
        prompt_provider=FailingPromptProvider(),
        generator=generator,
        fallback_prompt="fallback prompt",
        strict_prompt_provider=False,
    )

    payload = client.extract_structured(
        prompt_name="medlabs.extract",
        prompt_version="v1",
        input_text="hello",
        output_schema={"type": "object"},
    )

    assert payload == {"fields": []}
    assert generator.called_with is not None
    assert generator.called_with["system_prompt"] == "fallback prompt"


def test_prompted_llm_client_raises_in_strict_mode() -> None:
    generator = StubGenerator()
    client = PromptedLLMClient(
        prompt_provider=FailingPromptProvider(),
        generator=generator,
        strict_prompt_provider=True,
    )

    with pytest.raises(RuntimeError, match="prompt error"):
        client.extract_structured(
            prompt_name="medlabs.extract",
            prompt_version="v1",
            input_text="hello",
            output_schema={"type": "object"},
        )
