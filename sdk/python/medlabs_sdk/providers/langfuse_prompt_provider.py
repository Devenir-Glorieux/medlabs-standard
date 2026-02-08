from __future__ import annotations

from typing import Any


class LangfusePromptProvider:
    def __init__(
        self,
        *,
        public_key: str | None = None,
        secret_key: str | None = None,
        host: str | None = None,
        langfuse_client: Any | None = None,
    ) -> None:
        self.public_key = public_key
        self.secret_key = secret_key
        self.host = host
        self._langfuse = langfuse_client

    def get_prompt(self, *, prompt_name: str, prompt_version: str) -> str:
        langfuse_client = self._resolve_langfuse_client()
        try:
            prompt = langfuse_client.get_prompt(prompt_name, version=prompt_version)
        except Exception as exc:  # pragma: no cover - provider runtime path
            raise RuntimeError(
                f"Failed to load prompt '{prompt_name}' version '{prompt_version}' from Langfuse"
            ) from exc

        if hasattr(prompt, "compile"):
            compiled = prompt.compile()
            if isinstance(compiled, str) and compiled.strip():
                return compiled

        for field_name in ("prompt", "text", "content"):
            value = getattr(prompt, field_name, None)
            if isinstance(value, str) and value.strip():
                return value

        if isinstance(prompt, str) and prompt.strip():
            return prompt

        raise RuntimeError(
            f"Prompt '{prompt_name}' version '{prompt_version}' was loaded but has no text content"
        )

    def _resolve_langfuse_client(self) -> Any:
        if self._langfuse is not None:
            return self._langfuse

        try:
            from langfuse import Langfuse
        except ImportError as exc:  # pragma: no cover - dependency error path
            raise RuntimeError(
                "Install optional dependency 'langfuse' to use LangfusePromptProvider"
            ) from exc

        kwargs: dict[str, Any] = {}
        if self.public_key:
            kwargs["public_key"] = self.public_key
        if self.secret_key:
            kwargs["secret_key"] = self.secret_key
        if self.host:
            kwargs["host"] = self.host

        self._langfuse = Langfuse(**kwargs)
        return self._langfuse
