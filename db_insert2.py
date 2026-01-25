import json
import psycopg2
from psycopg2.extras import DictCursor

DB_CONFIG = {
    "host": "localhost",
    "dbname": "Papery",
    "user": "postgres",
    "password": "root",
    "port": 5432,
}

def to_int_or_none(value):
    try:
        if value is None or value == "":
            return None
        return int(value)
    except (TypeError, ValueError):
        return None


def load_books(json_path):
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)

def upsert_publisher(cur, name):
    cur.execute("""
                INSERT INTO publisher (name)
                VALUES (%s)
                ON CONFLICT (name) DO UPDATE
                    SET name = EXCLUDED.name
                RETURNING id
                """, (name,))
    return cur.fetchone()[0]

def upsert_author(cur, author):
    cur.execute("""
                INSERT INTO author (name, intro, img, birth, author_code)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (author_code) DO UPDATE
                    SET name = EXCLUDED.name
                RETURNING id
                """, (
                    author["author_name"],
                    author.get("intro"),
                    author.get("img"),
                    author.get("birth"),
                    author["author_code"],
                ))
    return cur.fetchone()[0]

def upsert_book(cur, book, publisher_id):
    price = to_int_or_none(book.get("price"))
    pages = to_int_or_none(book.get("page_cnt"))

    cur.execute("""
                INSERT INTO book (
                    title, isbn, description, price, size,
                    pages, toc, img, published_date, publisher_id, country_id
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (isbn) DO UPDATE
                    SET title = EXCLUDED.title
                RETURNING id
                """, (
                    book["title"],
                    book["isbn"],
                    book.get("intro"),
                    price,
                    book.get("book_size"),
                    pages,
                    book.get("toc"),
                    book.get("thumbnail_url"),
                    book.get("pub_date"),
                    publisher_id,
                    1
                ))
    return cur.fetchone()[0]

def insert_author_book_map(cur, book_id, author_id):
    cur.execute("""
                INSERT INTO author_book_map (book_id, author_id, role)
                VALUES (%s, %s, %s)
                ON CONFLICT DO NOTHING
                """, (book_id, author_id, "AUTHOR"))

def main():
    books = load_books("books.json")

    conn = psycopg2.connect(**DB_CONFIG)
    try:
        with conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                for book in books:
                    # 1. 출판사
                    publisher_id = upsert_publisher(cur, book["publisher"])

                    # 2. 책
                    book_id = upsert_book(cur, book, publisher_id)

                    # 3. 작가 + 매핑
                    for author in book["authors"]:
                        author_id = upsert_author(cur, author)
                        insert_author_book_map(cur, book_id, author_id)

        print("✅ 데이터 삽입 완료")

    except Exception as e:
        conn.rollback()
        print("❌ 오류 발생:", e)

    finally:
        conn.close()

if __name__ == "__main__":
    main()
