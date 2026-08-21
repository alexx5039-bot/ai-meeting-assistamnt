import asyncio

from fastapi import HTTPException

from app.core.config import settings
from app.worker.celery_app import celery_app

from app.repositories.meeting import MeetingRepository
from app.repositories.transcript import TranscriptRepository
from app.repositories.summary import SummaryRepository

from app.services.meeting import MeetingService
from app.services.audio import AudioService
from app.services.transcription.whisper import WhisperTranscriptionService
from app.services.summary.llm import LLMSummaryService
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from app.db.dependencies import get_llm

transcription_service = WhisperTranscriptionService()

@celery_app.task(
    bind=True,
    max_retries=3,
)
def process_meeting_task(
    self,
    meeting_id: int,
    user_id: int,
):
    async def run():
        engine = create_async_engine(
            settings.database_url,
            echo=True,
        )

        session_factory = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

        try:
            async with session_factory() as db:
                repository = MeetingRepository(db)
                transcript_repository = TranscriptRepository(db)
                summary_repository = SummaryRepository(db)

                audio_service = AudioService()

                llm = get_llm()
                summary_service = LLMSummaryService(llm)

                meeting_service = MeetingService(
                    repository=repository,
                    audio_service=audio_service,
                    transcription_service=transcription_service,
                    transcript_repository=transcript_repository,
                    summary_repository=summary_repository,
                    summary_service=summary_service,
                )

                await meeting_service.process_meeting(
                    meeting_id=meeting_id,
                    user_id=user_id,
                )

        finally:
            await engine.dispose()

    try:
        asyncio.run(run())

    except HTTPException:
        raise

    except Exception as exc:
        raise self.retry(
            exc=exc,
            countdown=60,
        )