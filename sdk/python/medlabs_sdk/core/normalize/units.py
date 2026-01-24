UNIT_ALIASES: dict[str, str] = {
    "g/l": "g/L",
    "mg/dl": "mg/dL",
    "mmol/l": "mmol/L",
    "umol/l": "umol/L",
    "u/l": "U/L",
}


def normalize_unit(unit_raw: str) -> str:
    if not unit_raw:
        return ""
    key = unit_raw.strip().lower()
    return UNIT_ALIASES.get(key, unit_raw.strip())
