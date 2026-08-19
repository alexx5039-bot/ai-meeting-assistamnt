from collections.abc import AsyncGenerator

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, oauth2
from langchain_mistralai import ChatMistralAI
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import decode_token
from app.models import User
from app.repositories.meeting import MeetingRepository
from app.db.database import AsyncSessionLocal
from app.repositories.summary import SummaryRepository
from app.repositories.transcript import TranscriptRepository
from app.repositories.user import UserRepository
from app.services.audio import AudioService
from app.services.meeting import MeetingService
from app.services.summary.base import SummaryService
from app.services.summary.llm import LLMSummaryService
from app.services.transcription.base import TranscriptionService
from app.services.user import AuthService
from app.services.transcription.whisper import WhisperTranscriptionService

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login"
)

async def get_db() -> AsyncGenerator[AsyncSession | None]:
    async with AsyncSessionLocal() as session:
        yield session

def get_llm():
    return ChatMistralAI(
        model="mistral-small-latest",
        api_key=settings.MISTRAL_API_KEY,
        temperature=0,
    )

async def get_meeting_repository(
        db: AsyncSession = Depends(get_db)
) -> MeetingRepository:
    return MeetingRepository(db)

async def get_audio_service() -> AudioService:
    return AudioService()

_transcription_service = WhisperTranscriptionService()

async def get_transcription_service() -> TranscriptionService:
    return _transcription_service

async def get_transcript_repository(db: AsyncSession = Depends(get_db)) -> TranscriptRepository:
    return TranscriptRepository(db)

async def get_summary_repository(db: AsyncSession = Depends(get_db)) -> SummaryRepository:
    return SummaryRepository(db)

async def get_summary_service(llm = Depends(get_llm)) -> SummaryService:
    return LLMSummaryService(llm=llm)


async def get_meeting_service(
        repository: MeetingRepository = Depends(get_meeting_repository),
        audio_service: AudioService = Depends(get_audio_service),
        transcription_service: TranscriptionService = Depends(get_transcription_service),
        transcript_repository: TranscriptRepository = Depends(get_transcript_repository),
        summary_repository: SummaryRepository = Depends(get_summary_repository),
        summary_service: SummaryService = Depends(get_summary_service),

) -> MeetingService:
    return MeetingService(
        repository,
        audio_service,
        transcription_service,
        transcript_repository,
        summary_repository,
        summary_service
    )

async def get_user_repository(
        db: AsyncSession = Depends(get_db)
) -> UserRepository:
    return UserRepository(db)


async def get_user_service(
        repository: UserRepository = Depends(get_user_repository)
) -> AuthService:
    return AuthService(repository)




async def get_current_user(
        token: str = Depends(oauth2_scheme),
        repository: UserRepository = Depends(get_user_repository)
) -> User | None:

    payload = decode_token(token)
    user_id = payload.get("sub")

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    user = await repository.get_by_id(int(user_id))

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    return user


