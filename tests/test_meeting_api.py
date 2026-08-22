from datetime import UTC, datetime
from unittest.mock import AsyncMock, Mock, patch

from fastapi.testclient import TestClient

from app.api.routes.meeting import get_current_user, get_meeting_service
from app.main import app
from app.models.enum import MeetingStatus

client = TestClient(app)


def override_current_user():
    user = Mock()
    user.id = 1
    return user


def override_meeting_service():
    return Mock()


app.dependency_overrides[get_current_user] = override_current_user

def test_create_meeting():
    service = Mock()

    meeting = Mock()
    meeting.id = 1
    meeting.title = "Test meeting"
    meeting.status = "pending"
    meeting.audio_path = None
    meeting.created_at = "2026-08-22T10:00:00"

    service.create_meeting = AsyncMock(
        return_value=meeting
    )

    app.dependency_overrides[get_meeting_service] = (
        lambda: service
    )

    response = client.post(
        "/meetings",
        json={
            "title": "Test meeting"
        },
    )

    assert response.status_code == 201

    service.create_meeting.assert_awaited_once()

    app.dependency_overrides.pop(
        get_meeting_service,
        None,
    )


def test_get_meetings():
    service = Mock()

    meeting = Mock()
    meeting.id = 1
    meeting.title = "Test meeting"
    meeting.status = "pending"
    meeting.audio_path = None
    meeting.created_at = "2026-08-22T10:00:00"

    service.get_user_meetings = AsyncMock(
        return_value=[meeting]
    )

    app.dependency_overrides[get_meeting_service] = (
        lambda: service
    )

    response = client.get("/meetings")

    assert response.status_code == 200

    service.get_user_meetings.assert_awaited_once_with(1)

    app.dependency_overrides.pop(
        get_meeting_service,
        None,
    )

@patch("app.api.routes.meeting.process_meeting_task")
def test_process_meeting(mock_task):
    response = client.post("/meetings/1/process")

    assert response.status_code == 202

    assert response.json() == {
        "meeting_id": 1,
        "status": "processing",
    }

    mock_task.delay.assert_called_once_with(
        meeting_id=1,
        user_id=1,
    )

def test_create_meeting_unauthorized():
    app.dependency_overrides.pop(
        get_current_user,
        None,
    )

    response = client.post(
        "/meetings",
        json={
            "title": "Test meeting"
        },
    )

    assert response.status_code == 401

    app.dependency_overrides[
        get_current_user
    ] = override_current_user


def test_get_meeting():
    service = Mock()

    meeting = Mock()
    meeting.id = 1
    meeting.title = "Test meeting"
    meeting.status = MeetingStatus.PENDING
    meeting.audio_path = None
    meeting.created_at = datetime.now(UTC)
    meeting.transcript = None
    meeting.summary = None

    service.get_meeting = AsyncMock(
        return_value=meeting
    )

    app.dependency_overrides[get_meeting_service] = (
        lambda: service
    )

    response = client.get("/meetings/1")

    assert response.status_code == 200

    assert response.json()["id"] == 1
    assert response.json()["title"] == "Test meeting"
    assert response.json()["status"] == "pending"
    assert response.json()["audio_path"] is None
    assert response.json()["transcript"] is None
    assert response.json()["summary"] is None

    service.get_meeting.assert_awaited_once_with(
        meeting_id=1,
        user_id=1,
    )

    app.dependency_overrides.pop(
        get_meeting_service,
        None,
    )