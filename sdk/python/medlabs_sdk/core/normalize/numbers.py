import re
from typing import Optional, Tuple

_RANGE_RE = re.compile("(-?\\d+(?:[\\.,]\\d+)?)\\s*[-\\u2013]\\s*(-?\\d+(?:[\\.,]\\d+)?)")
_SINGLE_RE = re.compile("-?\\d+(?:[\\.,]\\d+)?")


def parse_float(value_raw: str) -> Optional[float]:
    if not value_raw:
        return None
    value = value_raw.strip()
    if _RANGE_RE.search(value):
        return None
    match = _SINGLE_RE.search(value)
    if not match:
        return None
    return float(match.group(0).replace(",", "."))


def parse_range(ref_raw: str) -> Tuple[Optional[float], Optional[float]]:
    if not ref_raw:
        return None, None
    match = _RANGE_RE.search(ref_raw)
    if not match:
        return None, None
    low = float(match.group(1).replace(",", "."))
    high = float(match.group(2).replace(",", "."))
    return low, high
