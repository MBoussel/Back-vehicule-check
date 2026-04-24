from __future__ import annotations

from typing import Optional

from pydantic import BaseModel

from app.models.enums import FuelType, VehicleStatus


class VehicleBase(BaseModel):
    brand: str
    model: str
    plate_number: str
    fuel_type: FuelType
    current_mileage: int = 0
    status: VehicleStatus = VehicleStatus.AVAILABLE

    deposit_amount: Optional[float] = None
    franchise_amount: Optional[float] = None
    included_km: Optional[int] = None
    extra_km_price: Optional[float] = None
    immobilization_fee_per_day: Optional[float] = None
    key_loss_fee: Optional[float] = None


class VehicleCreate(VehicleBase):
    pass


class VehicleUpdate(BaseModel):
    brand: Optional[str] = None
    model: Optional[str] = None
    plate_number: Optional[str] = None
    fuel_type: Optional[FuelType] = None
    current_mileage: Optional[int] = None
    status: Optional[VehicleStatus] = None

    deposit_amount: Optional[float] = None
    franchise_amount: Optional[float] = None
    included_km: Optional[int] = None
    extra_km_price: Optional[float] = None
    immobilization_fee_per_day: Optional[float] = None
    key_loss_fee: Optional[float] = None


class VehicleResponse(VehicleBase):
    id: int

    class Config:
        from_attributes = True