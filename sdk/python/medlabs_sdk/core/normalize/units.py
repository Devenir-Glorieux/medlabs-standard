from __future__ import annotations

_UNIT_ALIASES: dict[str, str] = {
    "g/l": "g/L",
    "g/dl": "g/dL",
    "mg/dl": "mg/dL",
    "mmol/l": "mmol/L",
    "umol/l": "umol/L",
    "u/l": "U/L",
    "iu/l": "U/L",
    "x10^9/l": "10*9/L",
    "10^9/l": "10*9/L",
    "10*9/l": "10*9/L",
    "x10^12/l": "10*12/L",
    "10^12/l": "10*12/L",
    "10*12/l": "10*12/L",
    "sg": "1",
    "ph": "1",
    "%": "%",
    "": "",
}

_UNIT_DISPLAY: dict[str, str] = {
    "10*9/L": "10^9/L",
    "10*12/L": "10^12/L",
    "1": "1",
}


def normalize_unit(unit_raw: str) -> str:
    key = unit_raw.strip().lower()
    if key in _UNIT_ALIASES:
        return _UNIT_ALIASES[key]
    return unit_raw.strip()


def unit_display(unit: str) -> str:
    if unit in _UNIT_DISPLAY:
        return _UNIT_DISPLAY[unit]
    return unit
