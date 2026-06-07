import requests
from bs4 import BeautifulSoup
import random

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
]

url = "https://www.amazon.in/Apple-iPhone-13-128GB-Blue/dp/B09G9BL5CP"
headers = {
    "User-Agent": random.choice(USER_AGENTS),
    "Accept-Language": "en-US,en;q=0.9",
}

page = requests.get(url, headers=headers)
with open("amazon_test.html", "w", encoding="utf-8") as f:
    f.write(page.text)
