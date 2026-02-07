from __future__ import annotations

from typing import Any

from medlabs_sdk.providers.langfuse_prompt_provider import LangfusePromptProvider
from medlabs_sdk.providers.openai_client import OpenAIClient


class LangfuseOpenAIClient(OpenAIClient):
    """Compatibility wrapper kept for backward compatibility.

    Prefer explicit composition:
    - LangfusePromptProvider
    - OpenAIClient
    """

    def __init__(
        self,
        *,
        model: str = "gpt-4o-mini",
        api_key: str | None = None,
        public_key: str | None = None,
        secret_key: str | None = None,
        host: str | None = None,
        openai_client: Any | None = None,
        langfuse_client: Any | None = None,
    ) -> None:
        prompt_provider = LangfusePromptProvider(
            public_key=public_key,
            secret_key=secret_key,
            host=host,
            langfuse_client=langfuse_client,
        )
        super().__init__(
            model=model,
            api_key=api_key,
            prompt_provider=prompt_provider,
            openai_client=openai_client,
        )
