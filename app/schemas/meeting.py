from datetime import datetime
from pydantic import BaseModel, ConfigDict, field_validator
from app.models.enum import MeetingStatus

class SummaryResponse(BaseModel):
    id: int
    meeting_id: int
    text: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class TranscriptResponse(BaseModel):
    id: int
    meeting_id: int
    text: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

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

class MeetingDetailResponse(BaseModel):
    id: int
    title: str
    status: MeetingStatus
    audio_path: str | None
    created_at: datetime
    transcript: TranscriptResponse | None = None
    summary: SummaryResponse | None = None

    model_config = ConfigDict(
        from_attributes=True
    )
class ProcessingResponse(BaseModel):
    meeting_id: int
    status: str