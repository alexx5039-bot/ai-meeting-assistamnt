from abc import ABC, abstractstaticmethod, abstractmethod


class TranscriptionService:

    @abstractmethod
    async def transcribe(
            self,
            audio_path: str
    ) -> str:
        pass
