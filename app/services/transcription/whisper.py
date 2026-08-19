import asyncio
import os
import whisper

from app.core.config import settings
from app.services.transcription.base import TranscriptionService


class WhisperTranscriptionService(TranscriptionService):

    def __init__(self):
        ffmpeg_dir = os.path.dirname(settings.FFMPEG_PATH)

        os.environ["PATH"] = (
                ffmpeg_dir
                + os.pathsep
                + os.environ["PATH"]
        )

        self.model = whisper.load_model(settings.WHISPER_MODEL)

    async def transcribe(
            self,
            audio_path: str,
    ) -> str:
        result = await asyncio.to_thread(
            self.model.transcribe,
            audio_path,
        )

        return result["text"]