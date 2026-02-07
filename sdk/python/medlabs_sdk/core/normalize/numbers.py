from __future__ import annotations

import re

_RANGE_RE = re.compile(r"(-?\d+(?:[\.,]\d+)?)\s*[-\u2013]\s*(-?\d+(?:[\.,]\d+)?)")
_NUMBER_RE = re.compile(r"-?\d+(?:[\.,]\d+)?")


def parse_float(value_raw: str) -> float | None:
    value = value_raw.strip()
    if not value or _RANGE_RE.search(value):
        return None

    match = _NUMBER_RE.search(value)
    if not match:
        return None

    return float(match.group(0).replace(",", "."))


def parse_range(ref_raw: str) -> tuple[float | None, float | None]:
    ref = ref_raw.strip()
    if not ref:
        return None, None

    match = _RANGE_RE.search(ref)
    if not match:
        return None, None

    low = float(match.group(1).replace(",", "."))
    high = float(match.group(2).replace(",", "."))
    return low, high
