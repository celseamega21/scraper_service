from fastapi import FastAPI
from scraper.services import Scraper
from pydantic import BaseModel, EmailStr

app = FastAPI()

class Item(BaseModel):
    product_url: str
    email: EmailStr
    subscription_type: str

@app.post("/scrape")
async def scrape(item: Item):
    pass