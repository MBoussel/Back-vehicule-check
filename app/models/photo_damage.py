from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Float, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base

if TYPE_CHECKING:
    from app.models.check_photo import CheckPhoto


class PhotoDamage(Base):
    __tablename__ = "photo_damages"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    check_photo_id: Mapped[int] = mapped_column(
        ForeignKey("check_photos.id", ondelete="CASCADE"),
        nullable=False,
    )

    x_percent: Mapped[float] = mapped_column(Float, nullable=False)
    y_percent: Mapped[float] = mapped_column(Float, nullable=False)

    comment: Mapped[str | None] = mapped_column(String(500), nullable=True)

    severity: Mapped[str | None] = mapped_column(String(50), nullable=True)

    damage_type: Mapped[str | None] = mapped_column(String(50), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    photo: Mapped["CheckPhoto"] = relationship(back_populates="damages")

    def __repr__(self) -> str:
        return f"<PhotoDamage id={self.id} photo_id={self.check_photo_id}>"