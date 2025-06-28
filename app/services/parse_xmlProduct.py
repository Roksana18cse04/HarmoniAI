import cloudscraper
from bs4 import BeautifulSoup

def get_products_from_xml(url):
    scraper = cloudscraper.create_scraper()
    response = scraper.get(url)
    soup = BeautifulSoup(response.content, "xml")

    # Try both <item> and <entry>
    items = soup.find_all("item")
    if not items:
        items = soup.find_all("entry")

    products = []
    for item in items:
        def get(tag): 
            el = item.find(tag)
            return el.text.strip() if el and el.text else ""

        product = {
            "product_id": get("g:id") or get("id"),
            "title": get("title"),
            "link": get("link"),
            "image_link": get("g:image_link"),
            "price": get("g:price"),
            "brand": get("g:brand"),
            "color": get("g:color") or get("color"),
            "gender": get("g:gender"),
            "category": get("g:product_type")
        }
        products.append(product)

    print(f"-------- Fetched {len(products)} products from {url}")
    return products



