from typing import TYPE_CHECKING

from sqlalchemy import String

from app.db.base import BaseModel
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from app.models.meeting import Meeting


class User(BaseModel):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(
        String(60),
        unique=True,
        index=True,
        nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    meetings: Mapped["Meeting"] = relationship(
        back_populates="user",
        cascade="all, delete-orphan"
    )