from sqlalchemy import select

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.summary import Summary

class SummaryRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, meeting_id: int, text: str) -> Summary:
        summary = Summary(meeting_id=meeting_id,
                          text=text
                          )
        self.db.add(summary)
        await self.db.commit()
        await self.db.refresh(summary)

        return summary

    async def get_by_meeting(self, meeting_id: int) -> Summary | None:
        stmt = select(Summary).where(Summary.meeting_id == meeting_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    