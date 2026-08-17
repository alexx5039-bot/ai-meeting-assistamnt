from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import BaseModel
if TYPE_CHECKING:
    from app.models.meeting import Meeting

class Summary(BaseModel):
    __tablename__ = "summaries"

    meeting_id: Mapped[int] = mapped_column(
        ForeignKey("meetings.id", ondelete="CASCADE"),
        unique=True
    )
    text: Mapped[str] = mapped_column(Text)

    meeting: Mapped["Meeting"] = relationship(
        back_populates="summary"
    )
