from datetime import datetime
from pydantic import BaseModel, ConfigDict, field_validator
from app.models.enum import MeetingStatus


class MeetingCreate(BaseModel):
    title: str

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Meeting title cannot be empty")

        return value

class MeetingResponse(BaseModel):
    id: int
    title: str
    status: MeetingStatus
    audio_path: str | None
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )