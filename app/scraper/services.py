from pydantic import BaseModel
from bs4 import BeautifulSoup
import httpx
from logging import getLogger

logger = getLogger(__name__)

class Item(BaseModel):
    name: str
    discount_price: str
    original_price: str | None = None

class Scraper:
    def __init__(self, url:str):
        self.url = url

    def get_soup(self, url) -> BeautifulSoup:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"}
        
        try:
            r = httpx.get(url=url, headers=headers)
            r.raise_for_status()
            return BeautifulSoup(r.text, 'html.parser')
        except httpx.HTTPStatusError as e:
            logger.warning(f"Bad status {e.response.status_code} for URL: {url}")
            return None
        except httpx.RequestError as e:
            logger.error(f"Network error while requesting {url}: {e}")
            return None
        
    def scrape_product(self):
        results = []
        logger.info("Fetching url...")

        soup = self.get_soup(self.url)

        if not soup:
            logger.warning("Failed to fetch data.")
            return results
        
        name = soup.select_one("div.css-1nylpq2").get_text(strip=True)
        original_price = soup.select_one("div.original-price span:nth-of-type(2)")
        discount_price = soup.select_one("div.price")

        if original_price and discount_price:
            original_price = original_price.get_text(strip=True)
            discount_price = discount_price.get_text(strip=True)
        else:
            discount_price = discount_price.get_text(strip=True)
            original_price = discount_price

        product = Item(
            name=name,
            discount_price=discount_price,
            original_price=original_price
        )
        results.append(product)

        if not results:
            raise Exception("No products found.")
        
        return {
            "product_name": name,
            "original_price": original_price,
            "discount_price": discount_price
        }