from app.services.summary.base import SummaryService


class LLMSummaryService(SummaryService):

    async def summarize(self, transcript: str) -> str:
        return "Test Summary"