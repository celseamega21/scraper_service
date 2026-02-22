from app.services.scraper import Scraper
from app.services.exception import ScraperError
from app.schemas.task import TaskPayload
from app.services.callback import send_failed_callback, send_success_callback
from app.services.utils import clean_price

def process_task(payload: TaskPayload):
    try:
        scraped = Scraper(payload.product_url).scrape_product()
        product_name = scraped.get("product_name")
        raw_price = scraped.get("price")
        price = clean_price(raw_price)
        data = {
            "product_name": product_name,
            "product_price": price,
        }
        send_success_callback(payload.task_id, data)

    except ScraperError as e:
        send_failed_callback(payload.task_id, e.code)

    except Exception as e:
        send_failed_callback(payload.task_id, str(e))