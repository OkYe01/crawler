# book_detail.py
import re
from bs4 import BeautifulSoup
from author_crawler import crawl_author_detail

def crawl_detail_page(driver, detail_url):
    driver.get(detail_url)
    soup = BeautifulSoup(driver.page_source, "html.parser")

    # =========================
    # 1. 책 기본 정보
    # =========================

    title = ""
    intro = ""
    publisher = ""
    pub_date = ""
    price = ""
    toc = ""

    isbn = ""
    page_cnt = ""
    book_size = ""

    thumbnail_url = ""
    authors = []
    img_url = ""

    # 책 제목
    title_tag = soup.select_one("h1 .prod_title")
    if title_tag:
        title = title_tag.get_text(strip=True)

    # 책 소개 - description으로 수정
    intro_tag = soup.select_one(".intro_bottom .info_text")
    if intro_tag:
        intro = intro_tag.get_text(" ", strip=True)

    # 가격 (정가)
    price_tag = soup.select_one(".sale_price s.val")
    if price_tag:
        price = re.sub(r"[^\d]", "", price_tag.get_text())

    # 책 썸네일
    thumb_img = soup.select_one(
        ".col_prod_info.thumb img[src]"
    )
    if thumb_img:
        thumbnail_url = thumb_img.get("src", "")

    # 출판사, 출판일
    pub_box = soup.select_one("div.prod_info_text.publish_date")

    if pub_box:
        a = pub_box.select_one("a.btn_publish_link")
        publisher = a.text.strip() if a else ""

        m = re.search(r"(\d{4})년\s*(\d{1,2})월\s*(\d{1,2})일", pub_box.get_text())
        if m:
            year, month, day = m.groups()
            pub_date = f"{year}-{int(month):02d}-{int(day):02d}"

    # 목차
    toc_el = soup.select_one("li.book_contents_item")
    toc = toc_el.get_text("\n", strip=True) if toc_el else ""

    # 책 기본 정보
    table = soup.find("table")
    if table:
        for row in table.find_all("tr"):
            th = row.find("th")
            td = row.find("td")
            if not th or not td:
                continue

            key = th.get_text(strip=True)
            text = td.get_text(" ", strip=True)

            if "ISBN" in key:
                isbn = text
            elif "쪽수" in key:
                page_cnt = re.sub(r"\D", "", text)
            elif "크기" in key:
                text = td.get_text(" ", strip=True)
                match = re.search(
                    r"\d+\s*(?:\*|x|×)\s*\d+(?:\s*(?:\*|x|×)\s*\d+)?\s*mm",
                    text,
                    re.IGNORECASE
                )
                if match:
                    book_size = re.sub(r"\s+", " ", match.group()).strip()
                else:
                    book_size = ""

    if not isbn:
        print("{title} 도서 isbn 없음")
        return None

    # 작가 정보
    for tag in soup.select("[data-author-id]"):
        author_code = tag.get("data-author-id")
        author_name = tag.get_text(strip=True)
        profile_img = soup.select_one(".writer_profile img")

        if not author_code or not author_name:
            continue

        # 중복 제거
        if any(a["author_code"] == author_code for a in authors):
            continue
        author_detail = crawl_author_detail(author_code)

        if profile_img:
            img_url = (
                    profile_img.get("src")
                    or profile_img.get("data-src")
                    or ""
            )

        authors.append({
            "author_code": author_code,
            "author_name": author_name,
            "intro": author_detail.get("intro", ""),
            "birth": author_detail.get("birth", ""),
            "img": img_url
        })

    return {
        "isbn": isbn,
        "title": title,
        "intro": intro,
        "publisher": publisher,
        "pub_date": pub_date,
        "price": price,
        "toc": toc,
        "page_cnt": page_cnt,
        "book_size": book_size,
        "thumbnail_url": thumbnail_url,
        "authors": authors
    }