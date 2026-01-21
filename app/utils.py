import httpx
import time

def clean_price(price):
    """"Clean price string from non-numeric characters"""
    if isinstance(price, int):
        return price 
    if isinstance(price, str):
        cleaned = ''.join(c for c in price if c.isdigit())
        return int(cleaned) if cleaned else 0
    return 0

CORE_URL = "http://localhost:8000"

def notify_failed(task_id: int, error: str):
    payload = {
            "task_id": task_id,
            "status": "FAILED",
            "error": error
    }
    
    for _ in range(3):
        try:
            r = httpx.post(
                f"{CORE_URL}/api/scraping/callback/",
                json=payload,
                timeout=5
            )
            r.raise_for_status()
            return
        except Exception:
            time.sleep(2)