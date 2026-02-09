import psycopg2

try:
    conn = psycopg2.connect(
        host="localhost",      # 또는 127.0.0.1
        dbname="Papery",
        user="postgres",
        password="root",
        port=5432              # 기본 포트
    )

    print("✅ DB 연결 성공!")
    conn.close()

except Exception as e:
    print("❌ DB 연결 실패...")
    print(e)
