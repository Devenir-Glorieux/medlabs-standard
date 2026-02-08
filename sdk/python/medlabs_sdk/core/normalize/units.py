from __future__ import annotations

_UNIT_ALIASES: dict[str, str] = {
    "g/l": "g/L",
    "г/л": "g/L",
    "g/dl": "g/dL",
    "г/дл": "g/dL",
    "mg/dl": "mg/dL",
    "мг/дл": "mg/dL",
    "mmol/l": "mmol/L",
    "ммоль/л": "mmol/L",
    "umol/l": "umol/L",
    "μmol/l": "umol/L",
    "µmol/l": "umol/L",
    "мкмоль/л": "umol/L",
    "u/l": "U/L",
    "ед/л": "U/L",
    "iu/l": "U/L",
    "x10^9/l": "10*9/L",
    "10^9/l": "10*9/L",
    "10*9/l": "10*9/L",
    "x10^9/л": "10*9/L",
    "10^9/л": "10*9/L",
    "10*9/л": "10*9/L",
    "10^9 клеток/л": "10*9/L",
    "10*9 клеток/л": "10*9/L",
    "10^9 кл/л": "10*9/L",
    "тыс/мкл": "10*9/L",
    "x10^12/l": "10*12/L",
    "10^12/l": "10*12/L",
    "10*12/l": "10*12/L",
    "x10^12/л": "10*12/L",
    "10^12/л": "10*12/L",
    "10*12/л": "10*12/L",
    "10^12 клеток/л": "10*12/L",
    "10*12 клеток/л": "10*12/L",
    "млн/мкл": "10*12/L",
    "fl": "fL",
    "sg": "1",
    "ph": "1",
    "ед/мкл": "{cells}/uL",
    "клеток/мкл": "{cells}/uL",
    "клетки/мкл": "{cells}/uL",
    "мм/час": "mm/h",
    "мм/ч": "mm/h",
    "%": "%",
    "": "",
}

_UNIT_DISPLAY: dict[str, str] = {
    "10*9/L": "10^9/L",
    "10*12/L": "10^12/L",
    "1": "1",
    "{cells}/uL": "ед/мкл",
    "mm/h": "мм/час",
}


def normalize_unit(unit_raw: str) -> str:
    key = _normalize_unit_key(unit_raw)
    if key in _UNIT_ALIASES:
        return _UNIT_ALIASES[key]
    return unit_raw.strip()


def unit_display(unit: str) -> str:
    if unit in _UNIT_DISPLAY:
        return _UNIT_DISPLAY[unit]
    return unit


def _normalize_unit_key(unit_raw: str) -> str:
    key = " ".join(unit_raw.strip().lower().split())
    key = key.replace("ё", "е")
    key = key.replace("μ", "u")
    key = key.replace("µ", "u")
    key = key.replace("×", "x")
    return key
