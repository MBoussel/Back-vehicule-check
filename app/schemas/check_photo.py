from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.models.enums import PhotoType


class CheckPhotoCreate(BaseModel):
    photo_type: PhotoType
    file_url: str
    file_name: Optional[str] = None
    display_order: int = 0
    has_damage: bool = False
    damage_comment: Optional[str] = None


class CheckPhotoUploadResponse(BaseModel):
    id: int
    check_id: int
    photo_type: PhotoType
    file_url: str
    file_name: Optional[str] = None
    display_order: int
    has_damage: bool
    damage_comment: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True