from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base
from app.models.enums import CheckStatus, CheckType, CleanlinessLevel, FuelLevel

if TYPE_CHECKING:
    from app.models.check_photo import CheckPhoto
    from app.models.rental_contract import RentalContract
    from app.models.user import User
    from app.models.vehicle import Vehicle


class Check(Base):
    __tablename__ = "checks"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    vehicle_id: Mapped[int] = mapped_column(
        ForeignKey("vehicles.id", ondelete="CASCADE"),
        nullable=False,
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )
    contract_id: Mapped[int | None] = mapped_column(
        ForeignKey("rental_contracts.id", ondelete="SET NULL"),
        nullable=True,
    )

    type_check: Mapped[CheckType] = mapped_column(
        Enum(CheckType, name="check_type_enum"),
        nullable=False,
    )
    check_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    mileage: Mapped[int] = mapped_column(Integer, nullable=False)
    fuel_level: Mapped[FuelLevel] = mapped_column(
        Enum(FuelLevel, name="fuel_level_enum"),
        nullable=False,
    )
    cleanliness: Mapped[CleanlinessLevel] = mapped_column(
        Enum(CleanlinessLevel, name="cleanliness_level_enum"),
        nullable=False,
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    booking_reference: Mapped[str | None] = mapped_column(String(100), nullable=True)
    client_name: Mapped[str | None] = mapped_column(String(150), nullable=True)

    status: Mapped[CheckStatus] = mapped_column(
        Enum(CheckStatus, name="check_status_enum"),
        nullable=False,
        default=CheckStatus.COMPLETED,
    )

    signature_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    agent_signature_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

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

    vehicle: Mapped["Vehicle"] = relationship(back_populates="checks")
    user: Mapped["User"] = relationship(back_populates="checks")
    contract: Mapped["RentalContract | None"] = relationship(back_populates="checks")
    photos: Mapped[list["CheckPhoto"]] = relationship(
        back_populates="check",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Check id={self.id} type={self.type_check}>"