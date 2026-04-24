from app.models.check import Check


def format_enum_value(value) -> str:
    if value is None:
        return "-"
    raw = getattr(value, "value", str(value))
    return raw.replace("_", " ").title()


def fuel_to_percent(fuel_level) -> int:
    if fuel_level is None:
        return 0

    fuel_map = {
        "FULL": 100,
        "THREE_QUARTERS": 75,
        "HALF": 50,
        "QUARTER": 25,
        "RESERVE": 5,
    }

    return fuel_map.get(getattr(fuel_level, "name", ""), 0)


def compare_checks(depart: Check, retour: Check) -> dict:
    departure_fuel_percent = fuel_to_percent(depart.fuel_level)
    return_fuel_percent = fuel_to_percent(retour.fuel_level)

    return {
        "departure_mileage": depart.mileage,
        "return_mileage": retour.mileage,
        "km_diff": retour.mileage - depart.mileage,
        "departure_fuel_level": format_enum_value(depart.fuel_level),
        "return_fuel_level": format_enum_value(retour.fuel_level),
        "fuel_diff": return_fuel_percent - departure_fuel_percent,
        "departure_cleanliness": format_enum_value(depart.cleanliness),
        "return_cleanliness": format_enum_value(retour.cleanliness),
        "cleanliness_changed": retour.cleanliness != depart.cleanliness,
        "possible_new_damage": (retour.notes or "").strip() != (depart.notes or "").strip(),
        "departure_notes": depart.notes,
        "return_notes": retour.notes,
    }