from __future__ import annotations

import re

_ALIAS_MAP: dict[str, str] = {
    "wbc": "wbc",
    "rbc": "rbc",
    "hgb": "hemoglobin",
    "hemoglobin": "hemoglobin",
    "hct": "hematocrit",
    "hematocrit": "hematocrit",
    "plt": "platelets",
    "platelets": "platelets",
    "glucose": "glucose",
    "creatinine": "creatinine",
    "urea": "urea",
    "alt": "alt",
    "ast": "ast",
    "color": "color",
    "appearance": "appearance",
    "specific gravity": "specific_gravity",
    "specific_gravity": "specific_gravity",
    "ph": "ph",
    "protein": "protein",
    "ketones": "ketones",
    "nitrite": "nitrite",
    "leukocyte esterase": "leukocyte_esterase",
    "leukocyte_esterase": "leukocyte_esterase",
}


def canonicalize_name(name: str) -> str:
    normalized = re.sub(r"\s+", " ", name.strip().lower())
    if not normalized:
        return ""
    if normalized in _ALIAS_MAP:
        return _ALIAS_MAP[normalized]
    return normalized.replace(" ", "_")
