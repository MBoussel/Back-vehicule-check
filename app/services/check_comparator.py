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
        "one_eighth": 12,
        "two_eighths": 25,
        "three_eighths": 37,
        "half": 50,
        "five_eighths": 62,
        "six_eighths": 75,
        "seven_eighths": 87,
        "full": 100,
    }

    value = getattr(fuel_level, "value", fuel_level)

    return fuel_map.get(str(value).lower(), 0)


def compare_checks(depart: Check, retour: Check) -> dict:
    departure_fuel_percent = fuel_to_percent(depart.fuel_level)
    return_fuel_percent = fuel_to_percent(retour.fuel_level)

    return {
        "departure_mileage": depart.mileage,
        "return_mileage": retour.mileage,
        "km_diff": retour.mileage - depart.mileage,
        "departure_fuel_level": depart.fuel_level,
        "return_fuel_level": retour.fuel_level,
        "fuel_diff": return_fuel_percent - departure_fuel_percent,
        "departure_cleanliness": format_enum_value(depart.cleanliness),
        "return_cleanliness": format_enum_value(retour.cleanliness),
        "cleanliness_changed": retour.cleanliness != depart.cleanliness,
        "possible_new_damage": (retour.notes or "").strip() != (depart.notes or "").strip(),
        "departure_notes": depart.notes,
        "return_notes": retour.notes,
    }