import requests
from bs4 import BeautifulSoup
import time

def get_product_data(url):

    # 🔥 Fix missing https
    if not url.startswith("http"):
        url = "https://" + url

    # 🔥 Clean URL
    if "/ref=" in url:
        url = url.split("/ref=")[0]

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.google.com/",
        "Connection": "keep-alive"
    }

    try:
        time.sleep(2)
        session = requests.Session()
        page = session.get(url, headers=headers)

        if page.status_code != 200:
            return {
                "title": "Blocked by Amazon",
                "price": "Not Found",
                "rating": "Not Found",
                "mrp": "Not Found"
            }

        soup = BeautifulSoup(page.content, "html.parser")

        # 📦 Title
        title_tag = soup.find(id="productTitle")
        title = title_tag.get_text().strip() if title_tag else "Not Found"

        # 💰 Price
        price = "Not Found"
        price_tag = soup.find("span", {"class": "a-price-whole"})
        if price_tag:
            price = price_tag.get_text()

        if price == "Not Found":
            price_tag = soup.find("span", {"class": "a-offscreen"})
            if price_tag:
                price = price_tag.get_text()

        # ⭐ Rating
        rating_tag = soup.find("span", {"class": "a-icon-alt"})
        rating = rating_tag.get_text() if rating_tag else "Not Found"

        # 💸 MRP (FIXED)
        mrp_tag = soup.find("span", {"class": "a-text-price"})
        if mrp_tag:
            mrp = mrp_tag.get_text().strip()

            # 🔥 fix double value
            if "₹" in mrp:
                parts = mrp.split("₹")
                if len(parts) > 2:
                    mrp = "₹" + parts[1]
        else:
            mrp = "Not Found"

        return {
            "title": title,
            "price": price,
            "rating": rating,
            "mrp": mrp
        }

    except Exception as e:
        return {
            "title": "Error",
            "price": "Not Found",
            "rating": "Not Found",
            "mrp": "Not Found"
        }