import pytest
from fastapi.testclient import TestClient
from app.main import app
from httpx import Response, Request, HTTPStatusError

client = TestClient(app)

@pytest.fixture
def mock_success(mocker):
    # mock scraping result
    mocker.patch(
        "app.services.scraper.Scraper.scrape_product",
        return_value={
            "product_name": "Test Product",
            "product_name": 250000
        }
    )

    request = Request("POST", "http://core-api")
    response = Response(200, request=request)

    mocker.patch(
        "app.services.utils.httpx.post",
        return_value=response
    )

def test_run_task_success(mock_success):
    response = client.post(
        "/run-task",
        json={
            "task_id": 1, 
            "product_url": "https://tk.tokopedia.com/ZSmaftX9b/"
        }
    )

    assert response.status_code == 200

def test_run_task_400(mocker):
    mocker.patch(
        "app.services.scraper.Scraper.scrape_product",
        return_value={
            "product_name": "Test Product",
            "product_name": "Rp 250.000"
        }
    )

    request = Request("POST", "http://core-api")
    response_400 = Response(400, request=request)

    error = HTTPStatusError(
        "client error",
        request=request,
        response=response_400
    )

    mock_post = mocker.patch(
        "app.services.utils.httpx.post",
        side_effect=error
    )

    response = client.post(
        "/run-task",
        json={
            "task_id": 1, 
            "product_url": "https://tk.tokopedia.com/ZSmaftX9b/"
        }
    )

    assert mock_post.call_count == 1