from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel


class ContractClosureBase(BaseModel):
    extra_km_fee: Decimal = Decimal("0")
    fuel_fee: Decimal = Decimal("0")
    cleaning_fee: Decimal = Decimal("0")
    damage_fee: Decimal = Decimal("0")
    other_fee: Decimal = Decimal("0")
    discount_amount: Decimal = Decimal("0")
    notes: Optional[str] = None
    status: str = "draft"


class ContractClosureCreate(ContractClosureBase):
    pass


class ContractClosureUpdate(BaseModel):
    extra_km_fee: Optional[Decimal] = None
    fuel_fee: Optional[Decimal] = None
    cleaning_fee: Optional[Decimal] = None
    damage_fee: Optional[Decimal] = None
    other_fee: Optional[Decimal] = None
    discount_amount: Optional[Decimal] = None
    notes: Optional[str] = None
    status: Optional[str] = None


class ContractClosureResponse(ContractClosureBase):
    id: int
    contract_id: int

    rental_days: int
    departure_mileage: int
    return_mileage: int
    driven_km: int
    included_km: int
    extra_km: int

    rental_price: Decimal
    final_total: Decimal

    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True