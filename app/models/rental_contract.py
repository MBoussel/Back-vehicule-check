from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Date, DateTime, ForeignKey, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base

if TYPE_CHECKING:
    from app.models.check import Check
    from app.models.vehicle import Vehicle


class RentalContract(Base):
    __tablename__ = "rental_contracts"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    contract_number: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
    )

    vehicle_id: Mapped[int] = mapped_column(
        ForeignKey("vehicles.id", ondelete="RESTRICT"),
        nullable=False,
    )

    customer_first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    customer_last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    customer_email: Mapped[str | None] = mapped_column(String(150), nullable=True)
    customer_phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    customer_address: Mapped[str | None] = mapped_column(String(255), nullable=True)

    license_number: Mapped[str] = mapped_column(String(100), nullable=False)
    license_issue_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    license_country: Mapped[str | None] = mapped_column(String(100), nullable=True)
    license_front_photo_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    license_back_photo_url: Mapped[str | None] = mapped_column(Text, nullable=True)

    secondary_driver_first_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    secondary_driver_last_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    secondary_driver_email: Mapped[str | None] = mapped_column(String(150), nullable=True)
    secondary_driver_phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    secondary_license_number: Mapped[str | None] = mapped_column(String(100), nullable=True)
    secondary_license_issue_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    secondary_license_country: Mapped[str | None] = mapped_column(String(100), nullable=True)
    secondary_license_front_photo_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    secondary_license_back_photo_url: Mapped[str | None] = mapped_column(Text, nullable=True)

    start_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    deposit_amount: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    franchise_amount: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    rental_price: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)

    pickup_location: Mapped[str | None] = mapped_column(Text, nullable=True)
    return_location: Mapped[str | None] = mapped_column(Text, nullable=True)
    delivery_fee: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)

    status: Mapped[str] = mapped_column(String(50), nullable=False, default="draft")
    signature_mode: Mapped[str] = mapped_column(String(50), nullable=False, default="onsite")

    signed_pdf_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    terms_and_conditions: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    vehicle: Mapped["Vehicle"] = relationship(back_populates="contracts")
    checks: Mapped[list["Check"]] = relationship(back_populates="contract")

    def __repr__(self) -> str:
        return f"<RentalContract id={self.id} contract_number={self.contract_number}>"