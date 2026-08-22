from unittest.mock import AsyncMock, Mock

import pytest
from fastapi import HTTPException

from app.models.enum import MeetingStatus
from app.services.meeting import MeetingService


@pytest.fixture
def repository():
    return Mock()


@pytest.fixture
def audio_service():
    return Mock()


@pytest.fixture
def transcription_service():
    return Mock()


@pytest.fixture
def transcript_repository():
    return Mock()


@pytest.fixture
def summary_repository():
    return Mock()


@pytest.fixture
def summary_service():
    return Mock()


@pytest.fixture
def meeting_service(
    repository,
    audio_service,
    transcription_service,
    transcript_repository,
    summary_repository,
    summary_service,
):
    return MeetingService(
        repository=repository,
        audio_service=audio_service,
        transcription_service=transcription_service,
        transcript_repository=transcript_repository,
        summary_repository=summary_repository,
        summary_service=summary_service,
    )



@pytest.mark.asyncio
async def test_create_meeting(
    meeting_service,
    repository,
):
    repository.get_by_title = AsyncMock(return_value=None)

    meeting = Mock()
    repository.create = AsyncMock(return_value=meeting)

    data = Mock()
    data.title = "Test meeting"

    result = await meeting_service.create_meeting(
        data=data,
        user_id=1,
    )

    assert result == meeting

    repository.get_by_title.assert_awaited_once_with(
        title="Test meeting",
        user_id=1,
    )

    repository.create.assert_awaited_once_with(
        title="Test meeting",
        user_id=1,
    )


@pytest.mark.asyncio
async def test_create_meeting_duplicate_title(
    meeting_service,
    repository,
):
    existing_meeting = Mock()

    repository.get_by_title = AsyncMock(
        return_value=existing_meeting
    )

    data = Mock()
    data.title = "Test meeting"

    with pytest.raises(HTTPException) as exc:
        await meeting_service.create_meeting(
            data=data,
            user_id=1,
        )

    assert exc.value.status_code == 409
    assert exc.value.detail == "Meeting with this title already exists"

    repository.get_by_title.assert_awaited_once_with(
        title="Test meeting",
        user_id=1,
    )




@pytest.mark.asyncio
async def test_get_meeting(
    meeting_service,
    repository,
):
    meeting = Mock()

    repository.get_by_id = AsyncMock(
        return_value=meeting
    )

    result = await meeting_service.get_meeting(
        meeting_id=1,
        user_id=1,
    )

    assert result == meeting

    repository.get_by_id.assert_awaited_once_with(
        meeting_id=1,
        user_id=1,
    )


@pytest.mark.asyncio
async def test_get_meeting_not_found(
    meeting_service,
    repository,
):
    repository.get_by_id = AsyncMock(
        return_value=None
    )

    with pytest.raises(HTTPException) as exc:
        await meeting_service.get_meeting(
            meeting_id=1,
            user_id=1,
        )

    assert exc.value.status_code == 404
    assert exc.value.detail == "Meeting not found"




@pytest.mark.asyncio
async def test_get_user_meetings(
    meeting_service,
    repository,
):
    meetings = [
        Mock(),
        Mock(),
    ]

    repository.get_by_user = AsyncMock(
        return_value=meetings
    )

    result = await meeting_service.get_user_meetings(
        user_id=1,
    )

    assert result == meetings

    repository.get_by_user.assert_awaited_once_with(
        user_id=1,
    )




@pytest.mark.asyncio
async def test_upload_audio(
    meeting_service,
    repository,
    audio_service,
):
    meeting = Mock()

    repository.get_by_id = AsyncMock(
        return_value=meeting
    )

    audio_service.save_audio = AsyncMock(
        return_value="uploads/audio/test.mp3"
    )

    updated_meeting = Mock()

    repository.update_audio_path = AsyncMock(
        return_value=updated_meeting
    )

    file = Mock()

    result = await meeting_service.upload_audio(
        meeting_id=1,
        user_id=1,
        file=file,
    )

    assert result == updated_meeting

    repository.get_by_id.assert_awaited_once_with(
        meeting_id=1,
        user_id=1,
    )

    audio_service.save_audio.assert_awaited_once_with(
        file
    )

    repository.update_audio_path.assert_awaited_once_with(
        meeting=meeting,
        audio_path="uploads/audio/test.mp3",
    )


@pytest.mark.asyncio
async def test_upload_audio_meeting_not_found(
    meeting_service,
    repository,
):
    repository.get_by_id = AsyncMock(
        return_value=None
    )

    file = Mock()

    with pytest.raises(HTTPException) as exc:
        await meeting_service.upload_audio(
            meeting_id=1,
            user_id=1,
            file=file,
        )

    assert exc.value.status_code == 404
    assert exc.value.detail == "Meeting not found"




@pytest.mark.asyncio
async def test_process_meeting_not_found(
    meeting_service,
    repository,
):
    repository.get_by_id = AsyncMock(
        return_value=None
    )

    with pytest.raises(HTTPException) as exc:
        await meeting_service.process_meeting(
            meeting_id=1,
            user_id=1,
        )

    assert exc.value.status_code == 404
    assert exc.value.detail == "Meeting not found"


@pytest.mark.asyncio
async def test_process_meeting_without_audio(
    meeting_service,
    repository,
):
    meeting = Mock()
    meeting.audio_path = None

    repository.get_by_id = AsyncMock(
        return_value=meeting
    )

    with pytest.raises(HTTPException) as exc:
        await meeting_service.process_meeting(
            meeting_id=1,
            user_id=1,
        )

    assert exc.value.status_code == 400
    assert exc.value.detail == "Meeting has no audio file"


@pytest.mark.asyncio
async def test_process_meeting_wrong_status(
    meeting_service,
    repository,
):
    meeting = Mock()
    meeting.audio_path = "uploads/audio/test.mp3"
    meeting.status = MeetingStatus.PENDING

    repository.get_by_id = AsyncMock(
        return_value=meeting
    )

    with pytest.raises(HTTPException) as exc:
        await meeting_service.process_meeting(
            meeting_id=1,
            user_id=1,
        )

    assert exc.value.status_code == 400
    assert exc.value.detail == "Meeting is not ready for processing"


@pytest.mark.asyncio
async def test_process_meeting_existing_transcript(
    meeting_service,
    repository,
    transcript_repository,
):
    meeting = Mock()
    meeting.id = 1
    meeting.audio_path = "uploads/audio/test.mp3"
    meeting.status = MeetingStatus.UPLOADED

    repository.get_by_id = AsyncMock(
        return_value=meeting
    )

    transcript_repository.get_by_meeting = AsyncMock(
        return_value=Mock()
    )

    with pytest.raises(HTTPException) as exc:
        await meeting_service.process_meeting(
            meeting_id=1,
            user_id=1,
        )

    assert exc.value.status_code == 400
    assert exc.value.detail == "Meeting already has a transcript"


@pytest.mark.asyncio
async def test_process_meeting_success(
    meeting_service,
    repository,
    transcription_service,
    transcript_repository,
    summary_repository,
    summary_service,
):
    meeting = Mock()
    meeting.id = 1
    meeting.audio_path = "uploads/audio/test.mp3"
    meeting.status = MeetingStatus.UPLOADED

    completed_meeting = Mock()

    repository.get_by_id = AsyncMock(
        side_effect=[
            meeting,
            completed_meeting,
        ]
    )

    repository.update_status = AsyncMock()

    transcript_repository.get_by_meeting = AsyncMock(
        return_value=None
    )

    transcript_repository.create = AsyncMock()

    summary_repository.get_by_meeting = AsyncMock(
        return_value=None
    )

    summary_repository.create = AsyncMock()

    transcription_service.transcribe = AsyncMock(
        return_value="This is a transcript"
    )

    summary_service.summarize = AsyncMock(
        return_value="This is a summary"
    )

    repository.get_by_id_with_details = AsyncMock(
        return_value=completed_meeting
    )

    result = await meeting_service.process_meeting(
        meeting_id=1,
        user_id=1,
    )

    assert result == completed_meeting

    transcription_service.transcribe.assert_awaited_once_with(
        "uploads/audio/test.mp3"
    )

    transcript_repository.create.assert_awaited_once_with(
        meeting_id=1,
        text="This is a transcript",
    )

    summary_service.summarize.assert_awaited_once_with(
        "This is a transcript"
    )

    summary_repository.create.assert_awaited_once_with(
        meeting_id=1,
        text="This is a summary",
    )

    repository.update_status.assert_any_await(
        meeting=meeting,
        status=MeetingStatus.TRANSCRIBING,
    )

    repository.update_status.assert_any_await(
        meeting=meeting,
        status=MeetingStatus.SUMMARIZING,
    )

    repository.update_status.assert_any_await(
        meeting=meeting,
        status=MeetingStatus.COMPLETED,
    )

    repository.get_by_id_with_details.assert_awaited_once_with(
        meeting_id=1,
        user_id=1,
    )


@pytest.mark.asyncio
async def test_process_meeting_error_sets_failed_status(
    meeting_service,
    repository,
    transcript_repository,
    transcription_service,
):
    meeting = Mock()
    meeting.id = 1
    meeting.audio_path = "uploads/audio/test.mp3"
    meeting.status = MeetingStatus.UPLOADED

    repository.get_by_id = AsyncMock(
        return_value=meeting
    )

    repository.update_status = AsyncMock()

    transcript_repository.get_by_meeting = AsyncMock(
        return_value=None
    )

    transcription_service.transcribe = AsyncMock(
        side_effect=Exception("Whisper failed")
    )

    with pytest.raises(Exception, match="Whisper failed"):
        await meeting_service.process_meeting(
            meeting_id=1,
            user_id=1,
        )

    repository.update_status.assert_any_await(
        meeting=meeting,
        status=MeetingStatus.TRANSCRIBING,
    )

    repository.update_status.assert_any_await(
        meeting=meeting,
        status=MeetingStatus.FAILED,
    )