from __future__ import annotations

import json
from typing import Any, Protocol


class PromptProvider(Protocol):
    def get_prompt(self, *, prompt_name: str, prompt_version: str) -> str:
        ...


class OpenAIClient:
    def __init__(
        self,
        *,
        model: str = "gpt-4o-mini",
        api_key: str | None = None,
        prompt_provider: PromptProvider,
        openai_client: Any | None = None,
    ) -> None:
        self.model = model
        self.api_key = api_key
        self.prompt_provider = prompt_provider
        self._openai = openai_client

    def extract_structured(
        self,
        *,
        prompt_name: str,
        prompt_version: str,
        input_text: str,
        output_schema: dict[str, Any],
        temperature: float = 0.0,
    ) -> dict[str, Any]:
        openai_client = self._resolve_openai_client()
        prompt_text = self.prompt_provider.get_prompt(
            prompt_name=prompt_name,
            prompt_version=prompt_version,
        )

        response = openai_client.chat.completions.create(
            model=self.model,
            temperature=temperature,
            messages=[
                {"role": "system", "content": prompt_text},
                {"role": "user", "content": input_text},
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "medlabs_extract",
                    "schema": output_schema,
                },
            },
        )

        content = response.choices[0].message.content
        payload_text = self._content_to_text(content)
        payload = json.loads(payload_text)
        if not isinstance(payload, dict):
            raise RuntimeError("OpenAI response JSON must be an object")
        return payload

    def _resolve_openai_client(self) -> Any:
        if self._openai is not None:
            return self._openai

        try:
            from openai import OpenAI
        except ImportError as exc:  # pragma: no cover - dependency error path
            raise RuntimeError("Install optional dependency 'openai' to use OpenAIClient") from exc

        kwargs: dict[str, Any] = {}
        if self.api_key:
            kwargs["api_key"] = self.api_key

        self._openai = OpenAI(**kwargs)
        return self._openai

    @staticmethod
    def _content_to_text(content: Any) -> str:
        if isinstance(content, str) and content.strip():
            return content

        if isinstance(content, list):
            chunks: list[str] = []
            for item in content:
                if isinstance(item, dict):
                    text = item.get("text")
                    if isinstance(text, str):
                        chunks.append(text)
            joined = "".join(chunks).strip()
            if joined:
                return joined

        raise RuntimeError("OpenAI response did not contain JSON content")
