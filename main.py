from fastapi import FastAPI, HTTPException
from app.scraper.services import Scraper
from pydantic import BaseModel
from app.utils import clean_price
import httpx

app = FastAPI()

class TaskPayload(BaseModel):
    task_id: int
    product_url: str

@app.post("/run-task")
async def run_task(payload: TaskPayload):
    try:
        scraped = Scraper(payload.product_url).scrape_product()
    except:
        raise HTTPException(
            status_code=400,
            detail="Failed to scrape product"
        )
    
    product_name = scraped.get("product_name")
    price = clean_price(scraped.get("discount_price"))

    httpx.post(
        "http://localhost:8000/api/scraping-result/",
        json={
            'task_id': payload.task_id,
            "product_name": product_name,
            "product_price": price
        }
    )