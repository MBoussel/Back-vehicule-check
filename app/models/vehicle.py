from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, Float, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base
from app.models.enums import FuelType, VehicleStatus

if TYPE_CHECKING:
    from app.models.check import Check
    from app.models.rental_contract import RentalContract


class Vehicle(Base):
    __tablename__ = "vehicles"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    brand: Mapped[str] = mapped_column(String(100), nullable=False)
    model: Mapped[str] = mapped_column(String(100), nullable=False)
    plate_number: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    fuel_type: Mapped[FuelType] = mapped_column(
        Enum(FuelType, name="fuel_type_enum"),
        nullable=False,
    )
    current_mileage: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    status: Mapped[VehicleStatus] = mapped_column(
        Enum(VehicleStatus, name="vehicle_status_enum"),
        nullable=False,
        default=VehicleStatus.AVAILABLE,
    )

    deposit_amount: Mapped[float | None] = mapped_column(Float, nullable=True)
    franchise_amount: Mapped[float | None] = mapped_column(Float, nullable=True)
    included_km: Mapped[int | None] = mapped_column(Integer, nullable=True)
    extra_km_price: Mapped[float | None] = mapped_column(Float, nullable=True)
    immobilization_fee_per_day: Mapped[float | None] = mapped_column(Float, nullable=True)
    key_loss_fee: Mapped[float | None] = mapped_column(Float, nullable=True)

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

    checks: Mapped[list["Check"]] = relationship(
        back_populates="vehicle",
        cascade="all, delete-orphan",
    )

    contracts: Mapped[list["RentalContract"]] = relationship(
        back_populates="vehicle",
    )

    def __repr__(self) -> str:
        return f"<Vehicle id={self.id} plate={self.plate_number}>"