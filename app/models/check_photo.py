from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base
from app.models.enums import PhotoType

if TYPE_CHECKING:
    from app.models.check import Check
    from app.models.photo_damage import PhotoDamage


class CheckPhoto(Base):
    __tablename__ = "check_photos"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    check_id: Mapped[int] = mapped_column(
        ForeignKey("checks.id", ondelete="CASCADE"),
        nullable=False,
    )

    photo_type: Mapped[PhotoType] = mapped_column(
    Enum(
        PhotoType,
        values_callable=lambda enum_cls: [e.value for e in enum_cls],
        name="photo_type_enum",
    ),
    nullable=False,
)

    file_url: Mapped[str] = mapped_column(String(500), nullable=False)
    file_name: Mapped[str | None] = mapped_column(String(255), nullable=True)

    display_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    has_damage: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    damage_comment: Mapped[str | None] = mapped_column(String(500), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    check: Mapped["Check"] = relationship(back_populates="photos")
    damages: Mapped[list["PhotoDamage"]] = relationship(
        back_populates="photo",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<CheckPhoto id={self.id} type={self.photo_type}>"