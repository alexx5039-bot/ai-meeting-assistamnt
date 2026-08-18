from app.services.transcription.base import TranscriptionService

class WhisperTranscriptionService(TranscriptionService):
    async def transcribe(
            self,
            audio_path: str
    ) -> str:
        return "Test transcription"
