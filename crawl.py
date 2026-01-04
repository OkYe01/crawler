# kyobo_selenium_crawl.py
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import json
import time

options = Options()
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)")

driver = webdriver.Chrome(options=options)
def parse_author_block(author_block):

    if author_block is None:
        return "", "", ""

    texts = [t.strip() for t in author_block.stripped_strings]

    author, publisher, pub_date = "", "", ""

    try:
        # 구조: [작가, "· 출판사", "· 출판일"]
        author = texts[0]

        publisher = texts[1].replace("·", "").strip()  # "· 출판사" → "출판사"
        pub_date = texts[2].replace("·", "").strip()   # "· 2025.12.17" → "2025.12.17"

    except Exception as e:
        print(f"⚠️ Parsing error: {e}")

    return author, publisher, pub_date

try:
    url = "https://product.kyobobook.co.kr/category/KOR/0101#?page=1&type=all&per=50&sort=new"
    driver.get(url)
    time.sleep(2)

    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")

    book_list = []
    books = soup.select(".prod_item")

    for b in books:
        title = b.select_one(".prod_name")
        author_block = b.select_one(".prod_author")
        price_tag = b.select_one(".price_normal .val")
        intro = b.select_one(".prod_introduction")

        # 가격 숫자만 추출 (예 : 정가13,000원 -> 13000)
        price = (
            int(price_tag.get_text(strip=True).replace(",", "").replace("원", ""))
            if price_tag else None
        )
        # 작가 / 출판사 / 출판일 분리
        author, publisher, pub_date = parse_author_block(author_block)

        book_list.append({
            "title": title.get_text(strip=True) if title else "",
            "author": author,
            "publisher": publisher,
            "pub_date": pub_date,
            "price": price,
            "intro": intro.get_text(strip=True) if intro else ""
        })

    with open("books.json", "w", encoding="utf-8") as f:
        json.dump(book_list, f, ensure_ascii=False, indent=2)

    print(f"Saved {len(book_list)} items to books.json")

finally:
    driver.quit()
