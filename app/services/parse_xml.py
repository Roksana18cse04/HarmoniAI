
import cloudscraper
from bs4 import BeautifulSoup

def get_products_from_xml(url):
    scraper = cloudscraper.create_scraper()
    response = scraper.get(url)
    soup = BeautifulSoup(response.content, "xml")

    items = soup.find_all("item")
    products = []
    for item in items:
        def get(tag): return item.find(tag).text.strip() if item.find(tag) else ""
        product = {
            "title": get("title"),
            "link": get("link"),
            "image": get("g:image_link"),
            "price": get("g:price"),
            "brand": get("g:brand"),
            "color": get("g:color"),
            "gender": get("g:gender"),
            "category": get("g:product_type")
        }
        products.append(product)
    return products
