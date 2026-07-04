import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import time
import re


def scrape_amazon(keyword):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
    }

    all_products = []

    url = f"https://www.amazon.in/s?k={keyword}"

    while url:
        print(f"Scraping: {url}")

        response = requests.get(url, headers=headers, timeout=30)

        if response.status_code != 200:
            print("Blocked or error")
            break

        soup = BeautifulSoup(response.text, "html.parser")

        items = soup.select("div[data-component-type='s-search-result']")

        if not items:
            print("No products found, stopping.")
            break

        for item in items:
            name = item.select_one("h2 span")
            price = item.select_one("span.a-price-whole")
            rating = item.select_one("span.a-icon-alt")
            reviews = item.select_one("span.a-size-mini.puis-normal-weight-text")
            asin = item.get("data-asin")
            image = item.select_one("img.s-image")

            clean_rating = None
            if rating:
                match = re.search(r"[\d.]+", rating.text)
                if match:
                    clean_rating = f"{match.group()}/5"

            clean_reviews = None
            if reviews:
                clean_reviews = re.sub(r"\D", "", reviews.text)

            all_products.append({
                "asin": asin,
                "name": name.text.strip() if name else None,
                "price": price.text.strip() if price else None,
                "rating": clean_rating if clean_rating else None,
                "reviews": clean_reviews if clean_reviews else None,
                "product_url": f"https://www.amazon.in/dp/{asin}" if asin else None,
                "image_url": image["src"] if image else None,
            })

        # Next page
        next_btn = soup.select_one("a.s-pagination-next")

        if next_btn and "s-pagination-disabled" not in next_btn.get("class", []):
            next_url = next_btn.get("href")
            url = "https://www.amazon.in" + next_url
        else:
            print("No next page found. Stopping.")
            break

        time.sleep(2)

    return all_products



products = scrape_amazon("phone")


df = pd.DataFrame(products)
df.to_csv("amazon.csv", index=False)

# SAVE JSON
with open("amazon.json", "w", encoding="utf-8") as f:
    json.dump(products, f, indent=2, ensure_ascii=False)

print("DONE:", len(products))