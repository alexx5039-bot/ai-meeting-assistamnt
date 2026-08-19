from app.services.summary.base import SummaryService


class LLMSummaryService(SummaryService):

    def __init__(self, llm):
        self.llm = llm

    async def summarize(self, transcript: str) -> str:
        response = await self.llm.ainvoke(
            f"""
                    Summarize the following meeting transcript.

                    Transcript:
                    {transcript}
                    """
        )

        return response.content