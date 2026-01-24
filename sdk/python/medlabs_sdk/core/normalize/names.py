ALIAS_MAP: dict[str, str] = {
    "hemoglobin": "hemoglobin",
    "hgb": "hemoglobin",
    "glucose": "glucose",
}


def canonicalize_name(name: str) -> str:
    key = name.strip().lower()
    if not key:
        return key
    return ALIAS_MAP.get(key, key.replace(" ", "_"))
