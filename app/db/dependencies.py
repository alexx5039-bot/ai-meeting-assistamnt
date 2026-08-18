from collections.abc import AsyncGenerator

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, oauth2
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_token
from app.models import User
from app.repositories.meeting import MeetingRepository
from app.db.database import AsyncSessionLocal
from app.repositories.user import UserRepository
from app.services.audio import AudioService
from app.services.meeting import MeetingService
from app.services.user import AuthService

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login"
)

async def get_db() -> AsyncGenerator[AsyncSession | None]:
    async with AsyncSessionLocal() as session:
        yield session

async def get_meeting_repository(
        db: AsyncSession = Depends(get_db)
) -> MeetingRepository:
    return MeetingRepository(db)

async def get_audio_service() -> AudioService:
    return AudioService()

async def get_meeting_service(
        repository: MeetingRepository = Depends(get_meeting_repository),
        audio_service: AudioService = Depends(get_audio_service)
) -> MeetingService:
    return MeetingService(repository, audio_service)

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


