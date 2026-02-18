import httpx
from httpx import TimeoutException,ConnectError, HTTPStatusError
import time

def clean_price(price):
    """"Clean price string from non-numeric characters"""
    if isinstance(price, int):
        return price 
    if isinstance(price, str):
        cleaned = ''.join(c for c in price if c.isdigit())
        return int(cleaned) if cleaned else 0
    return 0

CORE_URL = "http://core-api:8080"

def notify_failed(task_id: int, error: str):
    payload = {
            "task_id": task_id,
            "status": "FAILED",
            "error": error
    }
    
    for attempt in range(3): 
        try:
            r = httpx.post(
                f"{CORE_URL}/api/v1/scraper/scraping/callback/",
                json=payload,
                timeout=5
            )
            r.raise_for_status()
            return
        
        except (TimeoutException, ConnectError):
            time.sleep(2 ** attempt)

        except HTTPStatusError as e:
            if 500 <= e.response.status_code < 600:
                time.sleep(2 ** attempt)
            else:
                return