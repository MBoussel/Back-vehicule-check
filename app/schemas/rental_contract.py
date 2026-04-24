from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel

from app.schemas.vehicle import VehicleResponse


class ContractCheckSummary(BaseModel):
    id: int
    type_check: str
    check_date: datetime
    status: str

    class Config:
        from_attributes = True


class RentalContractBase(BaseModel):
    contract_number: str
    vehicle_id: int

    customer_first_name: str
    customer_last_name: str
    customer_email: Optional[str] = None
    customer_phone: Optional[str] = None
    customer_address: Optional[str] = None

    license_number: str
    license_issue_date: Optional[date] = None
    license_country: Optional[str] = None
    license_front_photo_url: Optional[str] = None
    license_back_photo_url: Optional[str] = None

    secondary_driver_first_name: Optional[str] = None
    secondary_driver_last_name: Optional[str] = None
    secondary_driver_email: Optional[str] = None
    secondary_driver_phone: Optional[str] = None
    secondary_license_number: Optional[str] = None
    secondary_license_issue_date: Optional[date] = None
    secondary_license_country: Optional[str] = None
    secondary_license_front_photo_url: Optional[str] = None
    secondary_license_back_photo_url: Optional[str] = None

    start_date: datetime
    end_date: datetime

    deposit_amount: Optional[Decimal] = None
    franchise_amount: Optional[Decimal] = None
    rental_price: Optional[Decimal] = None

    pickup_location: Optional[str] = None
    return_location: Optional[str] = None
    delivery_fee: Optional[Decimal] = None

    status: str = "draft"
    signature_mode: str = "onsite"
    signed_pdf_url: Optional[str] = None
    terms_and_conditions: Optional[str] = None


class RentalContractCreate(RentalContractBase):
    pass


class RentalContractUpdate(BaseModel):
    contract_number: Optional[str] = None
    vehicle_id: Optional[int] = None

    customer_first_name: Optional[str] = None
    customer_last_name: Optional[str] = None
    customer_email: Optional[str] = None
    customer_phone: Optional[str] = None
    customer_address: Optional[str] = None

    license_number: Optional[str] = None
    license_issue_date: Optional[date] = None
    license_country: Optional[str] = None
    license_front_photo_url: Optional[str] = None
    license_back_photo_url: Optional[str] = None

    secondary_driver_first_name: Optional[str] = None
    secondary_driver_last_name: Optional[str] = None
    secondary_driver_email: Optional[str] = None
    secondary_driver_phone: Optional[str] = None
    secondary_license_number: Optional[str] = None
    secondary_license_issue_date: Optional[date] = None
    secondary_license_country: Optional[str] = None
    secondary_license_front_photo_url: Optional[str] = None
    secondary_license_back_photo_url: Optional[str] = None

    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

    deposit_amount: Optional[Decimal] = None
    franchise_amount: Optional[Decimal] = None
    rental_price: Optional[Decimal] = None

    pickup_location: Optional[str] = None
    return_location: Optional[str] = None
    delivery_fee: Optional[Decimal] = None

    status: Optional[str] = None
    signature_mode: Optional[str] = None
    signed_pdf_url: Optional[str] = None
    terms_and_conditions: Optional[str] = None


class RentalContractResponse(RentalContractBase):
    id: int
    created_at: datetime
    updated_at: datetime

    vehicle: Optional[VehicleResponse] = None
    checks: list[ContractCheckSummary] = []

    class Config:
        from_attributes = True