-- 중복 방지용 260126
ALTER TABLE publisher ADD CONSTRAINT uq_publisher_name UNIQUE (name);
ALTER TABLE author ADD CONSTRAINT uq_author_code UNIQUE (author_code);
ALTER TABLE book ADD CONSTRAINT uq_book_isbn UNIQUE (isbn);
ALTER TABLE author_book_map
    ADD CONSTRAINT uq_author_book UNIQUE (book_id, author_id);

-- 생년월일 -> 년도만 존재 260126
ALTER TABLE author
ALTER COLUMN birth TYPE VARCHAR(11)
USING birth::VARCHAR;