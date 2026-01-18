# main.py
import json
from driver import create_driver
from book_list import crawl_list_pages

driver = create_driver()

books = crawl_list_pages(
    driver,
    base_url="https://product.kyobobook.co.kr/category/KOR/0101",
    start_page=1,
    end_page=1
)

print(f"총 수집된 책 수: {len(books)}")

driver.quit()

# ✅ JSON 파일로 저장
with open("books.json", "w", encoding="utf-8") as f:
    json.dump(books, f, ensure_ascii=False, indent=2)

print("books.json 저장 완료")