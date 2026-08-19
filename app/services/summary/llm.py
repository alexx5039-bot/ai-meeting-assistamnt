from app.services.summary.base import SummaryService


class LLMSummaryService(SummaryService):

    def __init__(self, llm):
        self.llm = llm

    async def summarize(self, transcript: str) -> str:
        response = await self.llm.ainvoke(
            [
                (
                    "system",
                    "You are a meeting assistant. "
                    "Summarize the meeting transcript concisely. "
                    "Include key points, decisions, and action items.",
                ),
                (
                    "human",
                    transcript,
                ),
            ]
        )

        return response.content