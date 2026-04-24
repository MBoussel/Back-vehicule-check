from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.models.enums import (
    CheckStatus,
    CheckType,
    CleanlinessLevel,
    FuelLevel,
    PhotoType,
)
from app.schemas.photo_damage import PhotoDamageResponse


class CheckPhotoCreate(BaseModel):
    photo_type: PhotoType
    file_url: str
    file_name: Optional[str] = None
    display_order: int = 0
    has_damage: bool = False
    damage_comment: Optional[str] = None


class CheckPhotoResponse(BaseModel):
    id: int
    photo_type: PhotoType
    file_url: str
    file_name: Optional[str] = None
    display_order: int
    has_damage: bool
    damage_comment: Optional[str] = None
    created_at: datetime
    damages: list[PhotoDamageResponse] = []

    class Config:
        from_attributes = True


class CheckBase(BaseModel):
    vehicle_id: int
    contract_id: Optional[int] = None
    type_check: CheckType
    mileage: int
    fuel_level: FuelLevel
    cleanliness: CleanlinessLevel
    notes: Optional[str] = None
    booking_reference: Optional[str] = None
    client_name: Optional[str] = None
    status: CheckStatus = CheckStatus.COMPLETED


class CheckCreate(CheckBase):
    photos: list[CheckPhotoCreate] = []


class CheckResponse(CheckBase):
    id: int
    check_date: datetime
    created_at: datetime
    updated_at: datetime
    signature_url: Optional[str] = None
    agent_signature_url: Optional[str] = None
    photos: list[CheckPhotoResponse] = []

    class Config:
        from_attributes = True