from fastapi import FastAPI
from app.scraper import Scraper
from pydantic import BaseModel
from app.utils import clean_price, notify_failed
import httpx
import time
from httpx import TimeoutException, ConnectError, HTTPStatusError
from app.exception import ScraperError

app = FastAPI()

CORE_URL = "http://core-api:8080"

class TaskPayload(BaseModel):
    task_id: int
    product_url: str

@app.get("/health")
def health():
    return {"status": "ok"}

# run task scraping and send the result to core
@app.post("/run-task")
def run_task(payload: TaskPayload):
    # notify running
    httpx.post(
        f"{CORE_URL}/api/tasks/{payload.task_id}/status/",
        json={"status": "RUNNING"},
        timeout=3
    )

    # scraping
    try:
        scraped = Scraper(payload.product_url).scrape_product()
    except ScraperError:
        notify_failed(payload.task_id, "SCRAPING_FAILED")
        return {"status": "failed"}
    
    product_name = scraped.get("product_name")
    price = clean_price(scraped.get("discount_price"))

    # callback result
    for attempt in range(3):
        try:
            r = httpx.post(
                f"{CORE_URL}/api/scraping/callback/",
                json={
                    "task_id": payload.task_id,
                    "product_name": product_name,
                    "product_price": price,
                    "status": "SUCCESS"
                },
                timeout=5
            )

            r.raise_for_status()

            httpx.post(
                f"{CORE_URL}/api/tasks/{payload.task_id}/status/",
                json={"status": "DONE"}
            )
            return {"status": "success"}

        except (TimeoutException, ConnectError):
            time.sleep(2 ** attempt)
            continue

        except HTTPStatusError:
            httpx.post(
                f"{CORE_URL}/api/tasks/{payload.task_id}/status/",
                json={"task_status": "FAILED"}
            )
            return {"status": "failed"}

    httpx.post(
        f"{CORE_URL}/api/tasks/{payload.task_id}/status/",
        json={"task_status": "FAILED"}
    )
    return {"status": "failed"}