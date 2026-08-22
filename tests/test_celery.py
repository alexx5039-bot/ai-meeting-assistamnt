from unittest.mock import patch

import pytest

from app.worker.tasks import process_meeting_task


def test_process_meeting_task_success():
    with patch(
        "app.worker.tasks.asyncio.run"
    ) as mock_asyncio_run:

        process_meeting_task.run(
            meeting_id=1,
            user_id=1,
        )

        mock_asyncio_run.assert_called_once()


def test_process_meeting_task_retry():
    error = Exception("Processing failed")

    with patch(
        "app.worker.tasks.asyncio.run",
        side_effect=error,
    ), patch.object(
        process_meeting_task,
        "retry",
        side_effect=Exception("Retry"),
    ) as mock_retry:

        with pytest.raises(Exception, match="Retry"):
            process_meeting_task.run(
                meeting_id=1,
                user_id=1,
            )

        mock_retry.assert_called_once_with(
            exc=error,
            countdown=60,
        )