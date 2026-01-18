# author_crawler.py
import requests
import re
from bs4 import BeautifulSoup

_author_cache = {}  # 작가 캐시


def crawl_author_detail(author_code: str) -> dict:
    """
    교보문고 인물 상세 페이지 SSR(__next_f.push)에서
    - 작가 소개 (chrcIntcCntt)
    - 출생 연도 (chrcBrdy)
    추출
    """

    # 1️⃣ 캐시 확인
    if author_code in _author_cache:
        return _author_cache[author_code]

    print(f"[author] 크롤링 중인 작가 코드: {author_code}")

    url = f"https://store.kyobobook.co.kr/person/detail/{author_code}"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept-Language": "ko-KR,ko;q=0.9",
        "Accept": "text/html"
    }

    res = requests.get(url, headers=headers, timeout=10)
    if res.status_code != 200:
        print("[author] page request failed")
        return {}

    soup = BeautifulSoup(res.text, "html.parser")

    # 2️⃣ target script 찾기
    target_script = None
    for s in soup.find_all("script"):
        text = s.get_text()
        if "self.__next_f.push" in text and "chrcIntcCntt" in text:
            target_script = text
            print("[DEBUG] target script FOUND")
            break

    if not target_script:
        print("[DEBUG] target script NOT FOUND")
        return {}

    # 3️⃣ push payload 문자열만 추출
    push_match = re.search(
        r'self\.__next_f\.push\(\[\d+,\s*"(.*)"\]\)',
        target_script,
        re.DOTALL
    )

    if not push_match:
        print("[DEBUG] push payload NOT FOUND")
        return {}

    escaped_payload = push_match.group(1)

    # 4️⃣ escape 해제 (★ 핵심)
    try:
        decoded_payload = escaped_payload.encode("utf-8").decode("utf-8")
        decoded_payload = decoded_payload.replace('\\"', '"')
        decoded_payload = decoded_payload.replace('\\\\', '\\')
    except Exception as e:
        print("[DEBUG] unicode_escape decode failed:", e)
        return {}

    # 5️⃣ 필드 추출 함수
    def extract_field(text: str, key: str) -> str:
        """
        decode 된 payload에서 key 값 추출
        """
        pattern = rf'"{key}":"(.*?)"'
        m = re.search(pattern, text, re.DOTALL)
        return m.group(1).strip() if m else ""

    intro = extract_field(decoded_payload, "chrcIntcCntt")
    birth_raw = extract_field(decoded_payload, "chrcBrdy")

    # 6️⃣ 출생 연도 정제
    birth = ""
    if birth_raw:
        m = re.search(r"\d{4}", birth_raw)
        birth = m.group() if m else ""

    result = {
        "intro": intro,
        "birth": birth
    }

    # 7️⃣ 캐시 저장
    _author_cache[author_code] = result
    return result
