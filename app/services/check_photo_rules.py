from app.models.check import Check
from app.models.enums import CheckStatus, PhotoType

REQUIRED_PHOTO_TYPES = {
    PhotoType.FRONT,
    PhotoType.WINDSHIELD,
    PhotoType.WHEEL_FRONT_LEFT,   
    PhotoType.FRONT_LEFT_ANGLE,
    PhotoType.REAR_LEFT_ANGLE,
    PhotoType.WHEEL_REAR_LEFT,
    PhotoType.REAR,
    PhotoType.WHEEL_REAR_RIGHT,
    PhotoType.REAR_RIGHT_ANGLE,
    PhotoType.FRONT_RIGHT_ANGLE,
    PhotoType.WHEEL_FRONT_RIGHT,
    PhotoType.DASHBOARD,
    PhotoType.FRONT_SEAT,
    PhotoType.REAR_SEAT,
    PhotoType.TRUNK, 
}


def get_uploaded_photo_types(check: Check) -> set[PhotoType]:
    return {photo.photo_type for photo in check.photos}


def get_missing_required_photo_types(check: Check) -> list[PhotoType]:
    uploaded_types = get_uploaded_photo_types(check)
    missing = REQUIRED_PHOTO_TYPES - uploaded_types
    return sorted(missing, key=lambda item: item.value)


def validate_check_required_photos(check: Check) -> None:
    """
    Un check en DRAFT peut être incomplet.
    Un check en COMPLETED doit contenir toutes les photos obligatoires.
    """
    if check.status != CheckStatus.COMPLETED:
        return

    missing = get_missing_required_photo_types(check)
    if missing:
        missing_values = [photo_type.value for photo_type in missing]
        raise ValueError(
            f"Missing required photos: {', '.join(missing_values)}"
        )


def is_required_photo_type(photo_type: PhotoType) -> bool:
    return photo_type in REQUIRED_PHOTO_TYPES