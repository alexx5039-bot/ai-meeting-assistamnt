from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.meeting import Meeting

class MeetingRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, title: str, user_id: int) -> Meeting:
        meeting = Meeting(title=title, user_id=user_id)
        self.db.add(meeting)
        await self.db.commit()
        return await self.db.refresh(meeting)

    async def get_by_id(self, meeting_id, user_id: int) -> Meeting | None:
        stmt = select(Meeting).where(
            Meeting.id == meeting_id,
            Meeting.user_id == user_id
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_title(self, title: str, user_id: int) -> Meeting | None:
        stmt = select(Meeting).where(
            Meeting.title == title,
            Meeting.user_id == user_id
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_user(self, user_id: int) -> list[Meeting]:
        stmt = (select(Meeting)
                .where(Meeting.user_id == user_id)
                .order_by(Meeting.created_at).desc())
        result = await self.db.execute(stmt)
        return  list(result.scalars().all())

