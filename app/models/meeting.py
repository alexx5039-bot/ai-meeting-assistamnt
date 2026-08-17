from datetime import datetime
from sqlalchemy import Enum, ForeignKey

from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, BaseModel
from app.models.enum import MeetingStatus
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.transcript import Transcript
    from app.models.summary import Summary
    from app.models.user import User


class Meeting(BaseModel):
    __tablename__ = "meetings"

    title: Mapped[str] = mapped_column(String(255))
    audio_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[MeetingStatus] = mapped_column(
        Enum(MeetingStatus),
        default=MeetingStatus.PENDING
    )
    transcript: Mapped["Transcript"] = relationship(
        back_populates="meeting",
        uselist=False,
        cascade="all, delete-orphan"
    )
    summary: Mapped["Summary"] = relationship(
        back_populates="meeting",
        uselist=False,
        cascade="all, delete-orphan"
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    user: Mapped[User] = relationship(
        back_populates="meetings",

    )