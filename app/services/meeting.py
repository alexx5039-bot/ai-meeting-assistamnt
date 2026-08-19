from fastapi import HTTPException, status, UploadFile

from app.models.enum import MeetingStatus
from app.repositories.summary import SummaryRepository
from app.repositories.transcript import TranscriptRepository
from app.schemas.meeting import MeetingCreate
from app.repositories.meeting import MeetingRepository
from app.models.meeting import Meeting

from app.services.audio import AudioService
from app.services.summary.base import SummaryService
from app.services.transcription.base import TranscriptionService


class MeetingService:

    def __init__(self,
                 repository: MeetingRepository,
                 audio_service: AudioService,
                 transcription_service: TranscriptionService,
                 transcript_repository: TranscriptRepository,
                 summary_repository: SummaryRepository,
                 summary_service: SummaryService
                 ):
        self.repository = repository
        self.audio_service =audio_service
        self.transcription_service = transcription_service
        self.transcript_repository = transcript_repository
        self.summary_repository = summary_repository
        self.summary_service = summary_service


    async def create_meeting(self, data: MeetingCreate, user_id: int) -> Meeting:

        existing = await self.repository.get_by_title(
            title=data.title,
            user_id=user_id,
        )

        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Meeting with this title already exists",
            )

        return await self.repository.create(title=data.title, user_id=user_id)


    async def get_meeting(self, meeting_id: int, user_id: int) -> Meeting | None:
        meeting = await self.repository.get_by_id(
            meeting_id=meeting_id,
            user_id=user_id
        )
        if meeting is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Meeting not found",
            )
        return meeting


    async def get_user_meetings(self, user_id: int) -> list[Meeting]:
        return await self.repository.get_by_user(user_id=user_id)


    async def upload_audio(
            self,
            meeting_id: int,
            user_id: int,
            file: UploadFile,
    ) -> Meeting:

        meeting = await self.repository.get_by_id(
            meeting_id=meeting_id,
            user_id=user_id,
        )

        if meeting is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Meeting not found",
            )

        audio_path = await self.audio_service.save_audio(file)

        return await self.repository.update_audio_path(
            meeting=meeting,
            audio_path=audio_path,
        )

    async def process_meeting(
            self,
            meeting_id: int,
            user_id: int,
    ) -> Meeting:
        meeting = await self.repository.get_by_id(
            meeting_id=meeting_id,
            user_id=user_id
        )
        if meeting is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Meeting not found",
            )
        if not meeting.audio_path:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Meeting has no audio file",
            )
        if meeting.status != MeetingStatus.UPLOADED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Meeting is not ready for processing",
            )
        existing_transcript = await self.transcript_repository.get_by_meeting(
            meeting.id
        )

        if existing_transcript:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Meeting already has a transcript",
            )

        try:
            await self.repository.update_status(
                meeting=meeting,
                status=MeetingStatus.TRANSCRIBING
            )


            transcript_text = await self.transcription_service.transcribe(
                meeting.audio_path
            )
            await self.transcript_repository.create(
                meeting_id=meeting_id,
                text=transcript_text
            )
            await self.repository.update_status(
                meeting=meeting,
                status=MeetingStatus.SUMMARIZING
            )
            existing_summary = await self.summary_repository.get_by_meeting(
                meeting.id
            )

            if existing_summary:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Meeting already has a summary",
                )

            summary_text = await self.summary_service.summarize(transcript_text)

            await self.summary_repository.create(
                meeting_id=meeting_id,
                text=summary_text
            )
            await self.repository.update_status(
                meeting=meeting,
                status=MeetingStatus.COMPLETED,
            )

            meeting = await self.repository.get_by_id_with_details(
                meeting_id=meeting_id,
                user_id=user_id,
            )

            return meeting

        except Exception:
            await self.repository.update_status(
                meeting=meeting,
                status=MeetingStatus.FAILED
            )
            raise