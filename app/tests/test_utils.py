import pytest
from httpx import TimeoutException, ConnectError
from app.services.utils import notify_failed

@pytest.mark.parametrize("error", [TimeoutException, ConnectError])
def test_notify_failed_retry(mocker, error):
    mock_post = mocker.patch("app.services.utils.httpx.post", side_effect=error("network error"))
    mock_sleep = mocker.patch("app.services.utils.time.sleep")

    notify_failed(task_id=1, error="ERR")

    assert mock_post.call_count == 3
    assert mock_sleep.call_count == 3