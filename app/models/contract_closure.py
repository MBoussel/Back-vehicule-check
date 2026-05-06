from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base

if TYPE_CHECKING:
    from app.models.rental_contract import RentalContract


class ContractClosure(Base):
    __tablename__ = "contract_closures"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    contract_id: Mapped[int] = mapped_column(
        ForeignKey("rental_contracts.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )

    rental_days: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    departure_mileage: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    return_mileage: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    driven_km: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    included_km: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    extra_km: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    rental_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    extra_km_fee: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    fuel_fee: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    cleaning_fee: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    damage_fee: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    other_fee: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    discount_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=0)

    final_total: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=0)

    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="draft")

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

    contract: Mapped["RentalContract"] = relationship(back_populates="closure")