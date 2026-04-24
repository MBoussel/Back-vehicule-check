from datetime import datetime

from pydantic import BaseModel, Field

from app.models.enums import DamageSeverity


class PhotoDamageCreate(BaseModel):
    x_percent: float = Field(..., ge=0, le=100)
    y_percent: float = Field(..., ge=0, le=100)
    comment: str | None = Field(default=None, max_length=500)
    severity: DamageSeverity = Field(default=DamageSeverity.MINOR)
    
    damage_type: str | None = None


class PhotoDamageUpdate(BaseModel):
    x_percent: float | None = Field(default=None, ge=0, le=100)
    y_percent: float | None = Field(default=None, ge=0, le=100)
    comment: str | None = Field(default=None, max_length=500)
    severity: DamageSeverity | None = None


class PhotoDamageResponse(BaseModel):
    id: int
    check_photo_id: int
    x_percent: float
    y_percent: float
    comment: str | None
    severity: DamageSeverity


    damage_type: str | None

    created_at: datetime

    model_config = {
        "from_attributes": True
    }