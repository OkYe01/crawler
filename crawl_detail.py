# kyobo_selenium_crawl.py
import re

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

def crawl_detail_page(driver, detail_url):
    driver.get(detail_url)
    time.sleep(1.5)

    soup = BeautifulSoup(driver.page_source, "html.parser")

    isbn = ""
    page_cnt = ""
    book_size = ""

    table = soup.find("table")
    if table:
        for row in table.find_all("tr"):
            th = row.find("th")
            td = row.find("td")

            if not th or not td:
                continue

            key = th.get_text(strip=True)

            if "ISBN" in key:
                isbn = td.get_text(strip=True)
            elif "쪽수" in key or "페이지" in key:
                page_cnt = td.get_text(strip=True).replace("쪽", "")
            elif "크기" in key:
                text = td.get_text(" ", strip=True)
                match = re.search(r"\d+\s*\*\s*\d+", text)
                book_size = match.group() if match else ""

    return {
        "isbn": isbn,
        "page_cnt": page_cnt,
        "book_size": book_size
    }


try:
    url = "https://product.kyobobook.co.kr/category/KOR/0101#?page=5&type=best&per=20"
    driver.get(url)
    time.sleep(2)

    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")

    book_list = []
    books = soup.select(".prod_item")



    for b in books:
        title = b.select_one(".prod_name")
        author_block = b.select_one(".prod_author")
        price = b.select_one(".price_normal")
        link_book = b.select_one("a.prod_link")
        intro = b.select_one(".prod_introduction")


        print("books:", len(books))
        print("link:", link_book["href"] if link_book else None)
        print("table:", soup.find("table") is not None)

# 작가 / 출판사 / 출판일 분리
        author, publisher, pub_date = parse_author_block(author_block)

        price_text = price.get_text(strip=True)

        book_list.append({
            "title": title.get_text(strip=True) if title else "",
            "author": author,
            "publisher": publisher,
            "pub_date": pub_date,
            "price": int(re.sub(r"[^\d]", "", price_text)) if price else "",
            "intro": intro.get_text(strip=True) if intro else "",
            "link": link_book["href"] if link_book else ""
        })
        # =========================
        # ⭐ 상세페이지 크롤링 추가
        # =========================
        if link_book and link_book.get("href"):
            detail_data = crawl_detail_page(driver, link_book["href"])
            book_list[-1].update(detail_data)


    with open("books_selenium.json", "w", encoding="utf-8") as f:
        json.dump(book_list, f, ensure_ascii=False, indent=2)

    print(f"Saved {len(book_list)} items to books_selenium.json")

finally:
    driver.quit()
