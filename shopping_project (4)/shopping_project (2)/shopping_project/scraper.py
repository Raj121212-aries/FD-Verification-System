import requests
from bs4 import BeautifulSoup
import time
import urllib.parse
import random

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0"
]

def get_product_data(url):

    if not url.startswith("http"):
        url = "https://" + url

    if "/ref=" in url:
        url = url.split("/ref=")[0]

    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.google.com/",
        "Connection": "keep-alive"
    }

    try:
        session = requests.Session()
        page = session.get(url, headers=headers, timeout=10)

        if page.status_code != 200 or "captcha" in page.text.lower():
            return {
                "title": "Blocked by Amazon",
                "price": "Not Found",
                "rating": "Not Found",
                "mrp": "Not Found",
                "reviews": "Not Found"
            }

        soup = BeautifulSoup(page.content, "html.parser")

        # 📦 Title
        title_tag = soup.find(id="productTitle")
        title = title_tag.get_text().strip() if title_tag else "Not Found"

        # 💰 Price
        price = "Not Found"
        price_selectors = [
            soup.select_one("#corePriceDisplay_desktop_feature_div .a-price-whole"),
            soup.select_one("#corePrice_desktop .a-price-whole"),
            soup.select_one(".a-price-whole")
        ]
        
        for tag in price_selectors:
            if tag:
                price_text = tag.get_text().strip()
                if price_text:
                    # Clean trailing dot which Amazon sometimes adds
                    if price_text.endswith("."):
                        price_text = price_text[:-1]
                    price = price_text
                    break

        if price == "Not Found":
            price_tag = soup.find("span", {"class": "a-offscreen"})
            if price_tag:
                price = price_tag.get_text().strip()

        # ⭐ Rating
        rating_tag = soup.find("span", {"class": "a-icon-alt"})
        rating = rating_tag.get_text() if rating_tag else "Not Found"

        # 💸 MRP
        mrp = "Not Found"
        mrp_selectors = [
            soup.select_one('span.a-price.a-text-price span.a-offscreen'),
            soup.select_one('span.a-price[data-a-strike="true"] span.a-offscreen'),
            soup.select_one('#corePriceDisplay_desktop_feature_div span.a-text-price span.a-offscreen'),
            soup.select_one('.basisPrice .a-offscreen'),
            soup.find("span", {"class": "a-text-price"})
        ]
        
        for tag in mrp_selectors:
            if tag:
                mrp_text = tag.get_text().strip()
                if not mrp_text:
                    continue
                if "₹" in mrp_text:
                    parts = mrp_text.split("₹")
                    if len(parts) > 2:
                        mrp = "₹" + parts[1]
                    else:
                        mrp = "₹" + parts[-1]
                    break
                else:
                    mrp = "₹" + mrp_text
                    break
                    
        # 📝 Reviews
        reviews_tag = soup.find(id="acrCustomerReviewText")
        reviews = reviews_tag.get_text() if reviews_tag else "Not Found"

        return {
            "title": title,
            "price": price,
            "rating": rating,
            "mrp": mrp,
            "reviews": reviews
        }

    except Exception as e:
        print("Scraping error:", e)
        return {
            "title": "Error",
            "price": "Not Found",
            "rating": "Not Found",
            "mrp": "Not Found",
            "reviews": "Not Found"
        }

def get_amazon_alternatives(title_keywords):
    query = " ".join(title_keywords.split()[:4])
    url = f"https://www.amazon.in/s?k={urllib.parse.quote(query)}"
    
    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.google.com/"
    }
    
    try:
        session = requests.Session()
        page = session.get(url, headers=headers, timeout=8)
        if page.status_code != 200:
            return []
            
        soup = BeautifulSoup(page.content, "html.parser")
        results = soup.find_all("div", {"data-component-type": "s-search-result"})
        
        alternatives = []
        for res in results[:3]:
            title_tag = res.find("h2")
            if not title_tag:
                 continue
            title = title_tag.get_text().strip()
            
            link_tag = title_tag.find("a")
            link = "https://www.amazon.in" + link_tag["href"] if link_tag else None
            
            price_tag = res.find("span", {"class": "a-price-whole"})
            price = "Not Found"
            if price_tag:
                price_text = price_tag.get_text().strip()
                if price_text.endswith("."):
                    price_text = price_text[:-1]
                price = price_text
            
            rating_tag = res.find("span", {"class": "a-icon-alt"})
            rating = rating_tag.get_text() if rating_tag else "Not Found"
            
            image_tag = res.find("img", {"class": "s-image"})
            image = image_tag["src"] if image_tag else None
            
            if link and price != "Not Found":
                 alternatives.append({
                     "title": title[:60] + "..." if len(title) > 60 else title,
                     "price": f"₹{price}",
                     "rating": rating,
                     "link": link,
                     "image": image
                 })
                 
        return alternatives
    except Exception as e:
        print("Error fetching alternatives:", e)
        return []