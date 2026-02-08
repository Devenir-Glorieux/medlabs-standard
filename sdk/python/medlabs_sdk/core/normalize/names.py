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
    "ph": "ph",
    "protein": "protein",
    "ketones": "ketones",
    "nitrite": "nitrite",
    "leukocyte esterase": "leukocyte_esterase",
    "leukocyte_esterase": "leukocyte_esterase",
    "mcv": "mcv",
    "mch": "mch",
    "mchc": "mchc",
    "rdw": "rdw",
    "mpv": "mpv",
    "pct": "pct",
    "pdw": "pdw",
    "нейтрофильные_гранулоциты_neut": "neutrophils_abs",
    "нейтрофильные_гранулоциты_neut_pct": "neutrophils_pct",
    "лимфоциты_lymph": "lymphocytes_abs",
    "лимфоциты_lymph_pct": "lymphocytes_pct",
    "моноциты_mono": "monocytes_abs",
    "моноциты_mono_pct": "monocytes_pct",
    "эозинофилы_eo": "eosinophils_abs",
    "эозинофилы_eo_pct": "eosinophils_pct",
    "базофилы_baso": "basophils_abs",
    "базофилы_baso_pct": "basophils_pct",
    "соэ_метод_кинетики_агрегации_эритроцитов": "esr",
    "color_urine": "urine_color",
    "цвет_мочи": "urine_color",
    "clarity": "urine_clarity",
    "прозрачность": "urine_clarity",
    "reaction_urine": "urine_ph",
    "реакция_мочи": "urine_ph",
    "specific_gravity_urine": "specific_gravity",
    "удельный_вес": "specific_gravity",
    "protein_urine": "urine_protein",
    "белок_мочи": "urine_protein",
    "glucose_urine": "urine_glucose",
    "глюкоза_мочи": "urine_glucose",
    "ketone_bodies": "ketones",
    "кетоновые_тела": "ketones",
    "bilirubin_urine": "urine_bilirubin",
    "билирубин_в_моче": "urine_bilirubin",
    "urobilinogen_urine": "urine_urobilinogen",
    "уробилиноген_в_моче": "urine_urobilinogen",
    "nitrites": "nitrite",
    "нитриты": "nitrite",
    "лейкоциты_в_моче": "urine_leukocytes",
    "эритроциты_в_моче": "urine_erythrocytes",
    "гемоглобин_в_моче": "urine_hemoglobin",
    "эритроциты": "erythrocytes",
    "нелизированные_эритроциты": "urine_non_lysed_erythrocytes",
    "лейкоциты": "leukocytes",
    "скопления_лейкоцитов": "urine_leukocyte_clumps",
    "эпителиальные_клетки": "epithelial_cells",
    "клетки_плоского_эпителия": "squamous_epithelial_cells",
    "клетки_неплоского_эпителия": "non_squamous_epithelial_cells",
    "клетки_переходного_эпителия": "transitional_epithelial_cells",
    "эпителиальные_клетки_почечных_канальцев": "renal_tubular_epithelial_cells",
    "цилиндры": "casts",
    "гиалиновые_цилиндры": "hyaline_casts",
    "негиалиновые_цилиндры": "non_hyaline_casts",
    "бактерии": "bacteria",
    "кристаллы_оксалаты": "oxalate_crystals",
    "дрожжевидные_клетки": "yeast",
    "сперматозоиды": "sperm",
    "слизь": "mucus",
}


def canonicalize_name(name: str) -> str:
    normalized = re.sub(r"\s+", " ", name.strip().lower().replace("ё", "е"))
    if not normalized:
        return ""

    key = _tokenize_name(normalized)
    if key in _ALIAS_MAP:
        return _ALIAS_MAP[key]
    return key


def _tokenize_name(value: str) -> str:
    prepared = value.replace("%", " pct ")
    tokenized = re.sub(r"[^0-9a-zа-я]+", "_", prepared, flags=re.IGNORECASE)
    return tokenized.strip("_")
