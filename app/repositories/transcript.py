from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.transcript import Transcript

class TranscriptRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, meeting_id: int, text: str) -> Transcript:
        transcript = Transcript(
            meeting_id=meeting_id,
            text=text
        )
        self.db.add(transcript)

        await self.db.commit()
        await self.db.refresh(transcript)

        return transcript

    async def get_by_meeting(
            self,
            meeting_id: int,
    ) -> Transcript | None:
        stmt = (
            select(Transcript)
            .where(Transcript.meeting_id == meeting_id)
        )

        result = await self.db.execute(stmt)

        return result.scalar_one_or_none()