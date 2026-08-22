from abc import ABC, abstractmethod


class SummaryService(ABC):

    @abstractmethod
    async def summarize(self, transcript: str) -> str:
        pass
