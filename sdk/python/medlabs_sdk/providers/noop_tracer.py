from __future__ import annotations

from contextlib import nullcontext
from typing import Any


class NoopTracer:
    def span(self, name: str, **attrs: Any):
        del name, attrs
        return nullcontext()
