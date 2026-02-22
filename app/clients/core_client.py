import httpx
import time
from httpx import ConnectError, HTTPStatusError, ReadTimeout
import logging

logger = logging.getLogger(__name__)

CORE_URL = "http://core-api:8080"

def send_callback(payload):
    for attempt in range(3):
        try:
            r = httpx.post(
                f"{CORE_URL}/api/v1/scraper/callback/",
                json=payload,
                timeout=(3, 10)
            )
            r.raise_for_status()
            return

        except (ReadTimeout, ConnectError) as e:
            if attempt == 2:
                logger.warning(
                    f"Network error: {str(e)}"
                )
            else:
                time.sleep(2 ** attempt)

        except HTTPStatusError as e:
            if 400 <= e.response.status_code < 500:
                return
            time.sleep(2 ** attempt)