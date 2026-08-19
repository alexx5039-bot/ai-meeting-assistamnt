from abc import ABC, abstractmethod


class TranscriptionService(ABC):

    @abstractmethod
    async def transcribe(
            self,
            audio_path: str
    ) -> str:
        pass
