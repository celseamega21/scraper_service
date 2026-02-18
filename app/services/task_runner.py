from app.services.scraper import Scraper
from app.services.utils import clean_price, notify_failed
import httpx
import time
from httpx import ConnectError, HTTPStatusError, ReadTimeout
from app.services.exception import ScraperError

CORE_URL = "http://core-api:8080"

def run_task(payload):
    # notify running
    httpx.post(
        f"{CORE_URL}/api/v1/scraper/tasks/{payload.task_id}/status/",
        json={"status": "RUNNING"},
        timeout=5
    )

    # scraping
    try:
        scraped = Scraper(payload.product_url).scrape_product()
    except ScraperError as e:
        notify_failed(payload.task_id, e.code)
        return {"message": "failed to scrape product"}
    
    product_name = scraped.get("product_name")
    raw_price = scraped.get("discount_price")
    price = clean_price(raw_price)

    # callback result
    for attempt in range(3):
        try:
            r = httpx.post(
                f"{CORE_URL}/api/v1/scraper/callback/",
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
                f"{CORE_URL}/api/v1/scraper/tasks/{payload.task_id}/status/",
                json={"status": "DONE"}
            )
            return {"message": "task status update successful"}

        except (ReadTimeout, ConnectError):
            time.sleep(2 ** attempt)
            continue

        except HTTPStatusError:
            httpx.post(
                f"{CORE_URL}/api/v1/scraper/tasks/{payload.task_id}/status/",
                json={"status": "FAILED"},
                timeout=3
            )
            return {"message": "task status update failed(1)"}

    httpx.post(
        f"{CORE_URL}/api/v1/scraper/tasks/{payload.task_id}/status/",
        json={"status": "FAILED"},
        timeout=3

    )
    return {"message": "task status update failed(2)"}