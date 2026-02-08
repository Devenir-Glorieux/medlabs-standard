from __future__ import annotations

from contextlib import AbstractContextManager, nullcontext
from typing import Any


class LangfuseTracer:
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

    def span(self, name: str, **attrs: Any) -> AbstractContextManager[None]:
        try:
            client = self._resolve_langfuse_client()
        except Exception:
            return nullcontext()

        if hasattr(client, "start_as_current_span"):
            try:
                context_manager = client.start_as_current_span(name=name, input=attrs)
                return context_manager
            except Exception:
                return nullcontext()

        return nullcontext()

    def _resolve_langfuse_client(self) -> Any:
        if self._langfuse is not None:
            return self._langfuse

        try:
            from langfuse import Langfuse
        except ImportError as exc:  # pragma: no cover - dependency error path
            raise RuntimeError(
                "Install optional dependency 'langfuse' to use LangfuseTracer"
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
