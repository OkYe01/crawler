# Kyobo Book Crawler & DB Inserter

교보문고 신간 도서를 Selenium으로 크롤링하고  
수집된 데이터를 PostgreSQL 데이터베이스에 저장하는 파이썬 프로젝트입니다.

---

## Project Structure

    .
    ├── crawl.py
    ├── db_insert.py
    ├── books_selenium.json
    └── README.md

---

## crawl.py

교보문고 신간 도서 목록을 크롤링하여 JSON 파일로 저장합니다.

### Features
- Selenium (Headless Chrome) 사용
- 도서 정보 수집
  - title
  - author
  - publisher
  - pub_date
  - price
  - intro
- 결과를 `books_selenium.json` 파일로 저장

### Run

    python crawl.py

---

## db_insert.py

크롤링된 도서 데이터를 PostgreSQL 데이터베이스에 저장합니다.

### Database Connection

    host: localhost
    port: 5432
    dbname: ****
    user: ****
    password: ****

※ 환경에 맞게 수정 필요

### Run

    python db_insert.py

---

## Requirements

    pip install selenium beautifulsoup4 psycopg2-binary

Chrome 브라우저 및 ChromeDriver가 필요합니다.

---

## Notes

- 본 프로젝트는 학습 및 내부 데이터 수집 목적입니다.
- 크롤링 대상 사이트의 정책을 반드시 확인하세요.
- 과도한 요청은 차단될 수 있습니다.
