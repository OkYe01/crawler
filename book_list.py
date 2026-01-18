# book_list.py
from bs4 import BeautifulSoup
from book_detail import crawl_detail_page

# prod_info_box 안에 있는 a 태그만 책으로 인정
def extract_book_links(soup):
    links = []

    for box in soup.select(".prod_info_box"):
        a = box.select_one("a[href]")
        if not a:
            continue

        href = a["href"]

        if href.startswith("/"):
            href = "https://product.kyobobook.co.kr" + href

        links.append(href)

    return links


def crawl_list_pages(driver, base_url, start_page=1, end_page=5):
    results = []

    for page in range(start_page, end_page + 1):
        print(f"[crawl] 리스트 페이지 {page} 크롤링 중")

        # type 베스트로 수정
        url = f"{base_url}#?page={page}&type=best&per=20"
        driver.get(url)
        soup = BeautifulSoup(driver.page_source, "html.parser")

        detail_links = extract_book_links(soup)

        for detail_url in detail_links:
            book = crawl_detail_page(driver, detail_url)
            results.append(book)

    return results