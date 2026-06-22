"""
LCK scraper：根據當前日期推算應查哪個 Rounds 子頁面。
LCK 2026 賽程：Rounds 1-2（4月）→ Road to MSI（6月）→ Rounds 3-4（8月）→ ...
時間以 KST 標示，轉換為台灣時間（UTC+8）。
"""
import datetime
import re
import requests
from bs4 import BeautifulSoup
from zoneinfo import ZoneInfo

TARGET_TZ = ZoneInfo("Asia/Taipei")
SOURCE_TZ = ZoneInfo("Asia/Seoul")  # KST

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; sports-notify/1.0; +https://github.com/sports-notify)",
    "Accept-Language": "en-US,en;q=0.9",
}

# LCK 2026 各賽段及其日期範圍（用於選對應頁面）
# (start_date, end_date, url)
_ROUNDS = [
    (datetime.date(2026, 4, 1),  datetime.date(2026, 5, 31), "https://liquipedia.net/leagueoflegends/LCK/2026/Rounds_1-2"),
    (datetime.date(2026, 6, 1),  datetime.date(2026, 6, 20), "https://liquipedia.net/leagueoflegends/LCK/2026/Road_to_MSI"),
    (datetime.date(2026, 7, 15), datetime.date(2026, 9, 13), "https://liquipedia.net/leagueoflegends/LCK/2026/Rounds_3-4"),
]

_TIME_RE = re.compile(
    r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*\s+(\d{1,2})[, ]+\d{4}\s*-\s*(\d{2}:\d{2})\s*[EK][DS]T",
    re.IGNORECASE,
)
_MONTH_MAP = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
}


def _find_url(target_date: datetime.date) -> str | None:
    for start, end, url in _ROUNDS:
        if start <= target_date <= end:
            return url
    return None


def _parse_page(url: str, target_date: datetime.date) -> list[dict]:
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
    except Exception as e:
        print(f"[lck] 無法取得 {url}: {e}")
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    text = soup.get_text(" ", strip=True)

    results = []
    parts = _TIME_RE.split(text)

    i = 1
    while i + 3 <= len(parts):
        month_str, day_str, time_str = parts[i], parts[i + 1], parts[i + 2]
        block = parts[i + 3]
        i += 4

        month = _MONTH_MAP.get(month_str[:3].lower())
        if not month:
            continue

        day = int(day_str)
        hour, minute = map(int, time_str.split(":"))

        year = target_date.year
        try:
            dt_source = datetime.datetime(year, month, day, hour, minute, tzinfo=SOURCE_TZ)
        except ValueError:
            continue
        dt_twn = dt_source.astimezone(TARGET_TZ)

        if dt_twn.date() != target_date:
            continue

        # LCK teams: link text like [T1], [Gen.G Esports], etc.
        teams = re.findall(r"\[([A-Za-z0-9][A-Za-z0-9 .]{1,30}?)\]", block[:500])
        teams = [t.strip() for t in teams if not t.startswith("http") and 2 <= len(t) <= 25]
        if len(teams) < 2:
            continue

        results.append({
            "time": dt_twn.strftime("%H:%M"),
            "team1": teams[0],
            "team2": teams[1],
            "note": "",
        })

    return results


def get_matches(target_date: datetime.date) -> list[dict]:
    url = _find_url(target_date)
    if not url:
        return []
    return _parse_page(url, target_date)
