from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile, HTTPException, status

from app.core.config import Settings, settings


ALLOWED_AUDIO_TYPES = {
    "audio/mpeg",
    "audio/wav",
    "audio/x-wav",
    "audio/mp4",
    "audio/webm",
    "audio/ogg",
}

class AudioService:

    async def save_audio(self, file: UploadFile) -> str:

        if file.content_type not in ALLOWED_AUDIO_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported audio format",
            )

        settings.upload_dir.mkdir(
            parents=True,
            exist_ok=True
        )
        extensions = Path(file.filename or "").suffix
        filename = f"{uuid4()}{extensions}"
        file_path = settings.upload_dir / filename

        with file_path.open("wb") as buffer:
            while chunk := await file.read(1024 * 1024):
                buffer.write(chunk)
        return str(file_path)
