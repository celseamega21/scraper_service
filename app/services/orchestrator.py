from services.scraper import Scraper
from services.exception import ScraperError
from schemas.task import TaskPayload
from services.callback import send_failed_callback, send_success_callback
from services.utils import clean_price

def process_task(payload: TaskPayload):
    try:
        scraped = Scraper(payload.product_url).scrape_product()
        product_name = scraped.get("product_name")
        raw_price = scraped.get("discount_price")
        price = clean_price(raw_price)
        data = {
            "product_name": product_name,
            "product_price": price,
        }
        send_success_callback(payload.task_id, data)
        print("Send callback to core successfully")

    except ScraperError as e:
        send_failed_callback(payload.task_id, e.code)

    except Exception as e:
        send_failed_callback(payload.task_id, str(e))