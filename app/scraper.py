from pydantic import BaseModel
from bs4 import BeautifulSoup
import httpx
from logging import getLogger
from .exception import ScraperError
from httpx import HTTPStatusError, RequestError, TimeoutException

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
            r = httpx.get(url=url, headers=headers, timeout=10, follow_redirects=True)
            r.raise_for_status()
            return BeautifulSoup(r.text, 'html.parser')
        
        except TimeoutException:
            raise ScraperError("SCRAPING_TIMEOUT", "Timeout from source")
        
        except HTTPStatusError as e:
            if e.response.status_code == 404:
                raise ScraperError("SCRAPING_NOT_FOUND", "Product page not found")
            raise ScraperError("SCRAPING_HTTP_ERROR", f"Bad status {e.response.status_code}")
        
        except RequestError as e:
            raise ScraperError("SCRAPING_NETWORK_ERROR", "Network error") from e

    def scrape_product(self):
        results = []
        logger.info("Fetching url...")

        soup = self.get_soup(self.url)
        
        try:
            name = soup.select_one("div.css-1nylpq2").get_text(strip=True)
            original_price = soup.select_one("div.original-price span:nth-of-type(2)")
            discount_price = soup.select_one("div.price")
        except (AttributeError, ValueError) as e:
            raise ScraperError("SCRAPING_PARSE_ERROR", "HTML changed") from e        

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
        
        return {
            "product_name": name,
            "original_price": original_price,
            "discount_price": discount_price
        }
    
    def scrape_initial_product(self):
        soup = self.get_soup()

        name = soup.select_one("div.css-1nylpq2").get_text(strip=True)
        
        return {"name": name}