import enum


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    AGENT = "agent"


class FuelType(str, enum.Enum):
    ESSENCE = "essence"
    DIESEL = "diesel"
    HYBRID = "hybrid"
    ELECTRIC = "electric"


class VehicleStatus(str, enum.Enum):
    AVAILABLE = "available"
    RENTED = "rented"
    MAINTENANCE = "maintenance"
    INACTIVE = "inactive"


class CheckType(str, enum.Enum):
    DEPARTURE = "departure"
    RETURN = "return"


class FuelLevel(str, enum.Enum):
    ONE_EIGHTH = "one_eighth"
    TWO_EIGHTHS = "two_eighths"
    THREE_EIGHTHS = "three_eighths"
    HALF = "half"
    FIVE_EIGHTHS = "five_eighths"
    SIX_EIGHTHS = "six_eighths"
    SEVEN_EIGHTHS = "seven_eighths"
    FULL = "full"


class CleanlinessLevel(str, enum.Enum):
    VERY_CLEAN = "very_clean"
    CLEAN = "clean"
    MEDIUM = "medium"
    DIRTY = "dirty"


class CheckStatus(str, enum.Enum):
    DRAFT = "draft"
    COMPLETED = "completed"


class PhotoType(str, enum.Enum):
    FRONT = "front"
    REAR = "rear"
    FRONT_LEFT_ANGLE = "front_left_angle"
    FRONT_RIGHT_ANGLE = "front_right_angle"
    REAR_LEFT_ANGLE = "rear_left_angle"
    REAR_RIGHT_ANGLE = "rear_right_angle"
    WHEEL_FRONT_LEFT = "wheel_front_left"
    WHEEL_FRONT_RIGHT = "wheel_front_right"
    WHEEL_REAR_LEFT = "wheel_rear_left"
    WHEEL_REAR_RIGHT = "wheel_rear_right"
    WINDSHIELD = "windshield"
    FRONT_SEAT = "front_seat"
    REAR_SEAT = "rear_seat"
    TRUNK = "trunk"
    DASHBOARD = "dashboard"
    OTHER = "other"


class DamageSeverity(str, enum.Enum):
    MINOR = "minor"
    MODERATE = "moderate"
    SEVERE = "severe"