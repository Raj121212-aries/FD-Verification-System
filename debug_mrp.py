import requests
from bs4 import BeautifulSoup

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
url = "https://www.amazon.in/Sony-PlayStation-Console-Standalone-Standard/dp/B0BRCP72X8"
page = requests.get(url, headers=headers)
soup = BeautifulSoup(page.text, "html.parser")
print(soup.prettify()[:2000])
import re
mrps = re.findall(r'M\.R\.P\..*?₹([0-9,]+)', soup.text)
print("Regex MRPs:", mrps)
