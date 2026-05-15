from scraper import get_product_data
import sys

urls = [
    "https://www.amazon.in/Apple-iPhone-13-128GB-Blue/dp/B09G9BL5CP",
    "https://www.amazon.in/Sony-PlayStation-Console-Standalone-Standard/dp/B0BRCP72X8",
    "https://www.amazon.in/Samsung-Galaxy-Storm-128GB-Storage/dp/B0B4F2XCA3"
]

for u in urls:
    print("Testing:", u)
    data = get_product_data(u)
    print(f"Price: {data['price']} | MRP: {data['mrp']}")
    print("-" * 50)
