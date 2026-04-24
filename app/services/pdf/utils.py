from __future__ import annotations

from app.models.check import Check


TRANSLATIONS = {
    "AVAILABLE": "Disponible",
    "RENTED": "Loué",
    "MAINTENANCE": "En maintenance",
    "OUT_OF_SERVICE": "Hors service",
    "DEPARTURE": "Départ",
    "RETURN": "Retour",
    "CLEAN": "Propre",
    "DIRTY": "Sale",
    "VERY_DIRTY": "Très sale",
    "VERY_CLEAN": "Très propre",
    "MEDIUM": "Moyenne",
    "COMPLETED": "Terminé",
    "PENDING": "En attente",
    "DRAFT": "Brouillon",
    "SIGNED": "Signé",
    "CANCELLED": "Annulé",
    "ONSITE": "Sur place",
    "EXTERNAL": "Externe",
    "ESSENCE": "Essence",
    "DIESEL": "Diesel",
    "ELECTRIC": "Électrique",
    "HYBRID": "Hybride",
    "ONE_EIGHTH": "1/8 ou 0-13%",
    "TWO_EIGHTHS": "2/8 ou 14-25%",
    "THREE_EIGHTHS": "3/8 ou 26-38%",
    "HALF": "Moitié ou 39-50%",
    "FIVE_EIGHTHS": "5/8 ou 51-62%",
    "SIX_EIGHTHS": "6/8 ou 63-74%",
    "SEVEN_EIGHTHS": "7/8 ou 75-89%",
    "FULL": "Plein ou 90-100%",
    "MINOR": "Mineur",
    "MODERATE": "Modéré",
    "SEVERE": "Sévère",
    "SCRATCH": "Rayure",
    "DENT": "Bosse",
    "CRACK": "Fissure",
    "BROKEN": "Cassé",
    "OTHER": "Autre",
    "NONE": "-",
}

PHOTO_TRANSLATIONS = {
    "FRONT": "Avant du véhicule",
    "REAR": "Arrière du véhicule",
    "FRONT_LEFT_ANGLE": "Angle avant gauche",
    "FRONT_RIGHT_ANGLE": "Angle avant droit",
    "REAR_LEFT_ANGLE": "Angle arrière gauche",
    "REAR_RIGHT_ANGLE": "Angle arrière droit",
    "WHEEL_FRONT_LEFT": "Roue avant gauche",
    "WHEEL_FRONT_RIGHT": "Roue avant droite",
    "WHEEL_REAR_LEFT": "Roue arrière gauche",
    "WHEEL_REAR_RIGHT": "Roue arrière droite",
    "WINDSHIELD": "Pare-brise",
    "FRONT_SEAT": "Siège avant",
    "REAR_SEAT": "Siège arrière",
    "TRUNK": "Coffre",
    "DASHBOARD": "Tableau de bord",
    "OTHER": "Photo supplémentaire",
}


def translate_value(raw: str | None) -> str:
    if raw is None or raw == "":
        return "-"
    key = str(raw).strip().upper()
    return TRANSLATIONS.get(key, key.replace("_", " ").title())


def translate_photo_label(raw: str | None) -> str:
    if raw is None or raw == "":
        return "-"
    key = str(raw).strip().upper()
    return PHOTO_TRANSLATIONS.get(key, key.replace("_", " ").title())


def format_enum_label(value) -> str:
    if value is None:
        return "-"
    raw = getattr(value, "name", None) or getattr(value, "value", str(value))
    return translate_value(raw)


def safe_text(value) -> str:
    if value is None or value == "":
        return "-"
    return str(value)


def format_datetime_fr(value) -> str:
    if value is None:
        return "-"
    try:
        return value.strftime("%d/%m/%Y à %H:%M")
    except Exception:
        return str(value)


def format_date_fr(value) -> str:
    if value is None:
        return "-"
    try:
        return value.strftime("%d/%m/%Y")
    except Exception:
        return str(value)


def format_money(value) -> str:
    if value is None:
        return "-"

    try:
        amount = float(value)
        formatted = f"{amount:,.2f}"
        formatted = formatted.replace(",", " ").replace(".", ",")
        return f"{formatted} €"
    except Exception:
        return str(value)


def get_photo_type_value(photo) -> str:
    return getattr(photo.photo_type, "value", str(photo.photo_type))


def group_photos_by_type(check: Check | None) -> dict[str, object]:
    if check is None:
        return {}

    result: dict[str, object] = {}

    for photo in sorted(check.photos or [], key=lambda item: item.display_order):
        photo_type = get_photo_type_value(photo)
        if photo_type not in result:
            result[photo_type] = photo

    return result


def normalize_damage_type_label(damage) -> str:
    damage_type_raw = getattr(damage, "damage_type", None)

    if damage_type_raw is None:
        return "Autre"

    raw_value = (
        getattr(damage_type_raw, "value", None)
        or getattr(damage_type_raw, "name", None)
        or str(damage_type_raw)
    )

    normalized = str(raw_value).strip().lower()

    if "." in normalized:
        normalized = normalized.split(".")[-1]

    mapping = {
        "scratch": "Rayure",
        "dent": "Bosse",
        "crack": "Fissure",
        "broken": "Cassé",
        "other": "Autre",
    }

    return mapping.get(normalized, "Autre")


def normalize_severity_label(damage) -> str:
    severity_raw = getattr(damage, "severity", None)

    if severity_raw is None:
        return "-"

    raw_value = (
        getattr(severity_raw, "value", None)
        or getattr(severity_raw, "name", None)
        or str(severity_raw)
    )

    normalized = str(raw_value).strip().lower()

    if "." in normalized:
        normalized = normalized.split(".")[-1]

    mapping = {
        "minor": "Mineur",
        "moderate": "Modéré",
        "severe": "Sévère",
    }

    return mapping.get(normalized, translate_value(normalized))


def build_damage_summary(photo) -> list[list[str]]:
    rows = [["#", "Type", "Gravité", "Commentaire"]]
    damages = getattr(photo, "damages", None) or []

    for index, damage in enumerate(damages, start=1):
        rows.append(
            [
                str(index),
                normalize_damage_type_label(damage),
                normalize_severity_label(damage),
                safe_text(getattr(damage, "comment", None)),
            ]
        )

    return rows