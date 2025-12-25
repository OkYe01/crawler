import psycopg2
import json

# -----------------------------
# 1) DB CONNECTION
# -----------------------------
conn = psycopg2.connect(
    host="localhost",
    dbname="papery",
    user="papery",
    password="1234",
    port=5432
)
cur = conn.cursor()

# -----------------------------
# 2) 예시 크롤링 데이터
# -----------------------------
with open("books_selenium.json", "r", encoding="utf-8") as f:
        books = json.load(f)

# -----------------------------
# 3) Author 중복 체크 후 ID 반환
# -----------------------------
def get_or_create_author(name):
    cur.execute("SELECT id FROM author WHERE name=%s", (name,))
    row = cur.fetchone()

    if row:
        return row[0]

    cur.execute("""
        INSERT INTO author(name)
        VALUES (%s) RETURNING id
    """, (name,))
    author_id = cur.fetchone()[0]
    conn.commit()
    return author_id

# -----------------------------
# 4) Publisher 중복 체크 후 ID 반환
# -----------------------------
def get_or_create_publisher(name):
    cur.execute("SELECT id FROM publisher WHERE name=%s", (name,))
    row = cur.fetchone()

    if row:
        return row[0]

    cur.execute("""
        INSERT INTO publisher(name)
        VALUES (%s) RETURNING id
    """, (name,))
    publisher_id = cur.fetchone()[0]
    conn.commit()
    return publisher_id

# -----------------------------
# 5) BOOK INSERT → ID 반환
# -----------------------------
def insert_book(book, publisher_id):

    cur.execute("""
        INSERT INTO book (title, publisher_id, published_date, price, description, isbn, pages, size)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
    """, (
        book["title"],
        publisher_id,
        book["pub_date"],
        book["price"],
        book["intro"],
        book["isbn"],
        book["page_cnt"],
        book["book_size"]
    ))
    book_id = cur.fetchone()[0]
    conn.commit()
    return book_id

# -----------------------------
# 6) AUTHOR_BOOK_MAP INSERT
# -----------------------------
def insert_author_book_map(author_id, book_id):
    cur.execute("""
        INSERT INTO author_book_map (author_id, book_id)
        VALUES (%s, %s)
    """, (author_id, book_id))
    conn.commit()

# -----------------------------
# 7) 전체 데이터 처리 흐름
# -----------------------------
for book in books:
    author_id = get_or_create_author(book["author"])
    publisher_id = get_or_create_publisher(book["publisher"])
    book_id = insert_book(book, publisher_id)
    insert_author_book_map(author_id, book_id)

cur.close()
conn.close()

print("📚 모든 데이터 저장 완료! (author_book_map 포함)")