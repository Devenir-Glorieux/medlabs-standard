from __future__ import annotations

from typing import Any

from medlabs_sdk.providers.langfuse_prompt_provider import LangfusePromptProvider
from medlabs_sdk.providers.openai_client import OpenAIClient
from medlabs_sdk.providers.prompted_llm_client import PromptedLLMClient


class LangfuseOpenAIClient(PromptedLLMClient):
    """Backward-compatible convenience client.

    Prefer explicit composition in new code:
    - LangfusePromptProvider
    - OpenAIClient (with optional base_url)
    - PromptedLLMClient
    """

    def __init__(
        self,
        *,
        model: str = "gpt-4o-mini",
        api_key: str | None = None,
        base_url: str | None = None,
        public_key: str | None = None,
        secret_key: str | None = None,
        host: str | None = None,
        fallback_prompt: str = "Извлеки согласно схемы и верни только JSON.",
        strict_prompt_provider: bool = False,
        openai_client: Any | None = None,
        langfuse_client: Any | None = None,
    ) -> None:
        prompt_provider = LangfusePromptProvider(
            public_key=public_key,
            secret_key=secret_key,
            host=host,
            langfuse_client=langfuse_client,
        )
        generator = OpenAIClient(
            model=model,
            api_key=api_key,
            base_url=base_url,
            openai_client=openai_client,
        )
        super().__init__(
            prompt_provider=prompt_provider,
            generator=generator,
            fallback_prompt=fallback_prompt,
            strict_prompt_provider=strict_prompt_provider,
        )
