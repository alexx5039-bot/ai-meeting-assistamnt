from enum import StrEnum

class MeetingStatus(StrEnum):
    PENDING = "pending"
    UPLOADED = "uploaded"
    TRANSCRIBING = "transcribing"
    SUMMARIZING = "summarizing"
    COMPLETED = "completed"
    FAILED = "failed"