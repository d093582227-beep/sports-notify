"""
LOL 國際賽 scraper：自動偵測當前進行中的賽事（MSI / Worlds）。
時間以 KST（UTC+9）標示，轉換為台灣時間（UTC+8）。
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

# Candidate URLs in priority order; first one that has upcoming matches wins
_CANDIDATE_URLS = [
    "https://liquipedia.net/leagueoflegends/Mid-Season_Invitational/2026",
    "https://liquipedia.net/leagueoflegends/World_Championship/2026",
]

_TIME_RE = re.compile(
    r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*\s+(\d{1,2})\s*-\s*(\d{2}:\d{2})\s*KST",
    re.IGNORECASE,
)
_MONTH_MAP = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
}


def _parse_page(url: str, target_date: datetime.date) -> list[dict]:
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
    except Exception as e:
        print(f"[lol_intl] 無法取得 {url}: {e}")
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

        # LOL teams use 2-5 char abbreviations or full names
        # Try abbreviations first, fall back to full link text
        teams = re.findall(r"\[([A-Z][A-Za-z0-9]{1,7})\]", block[:500])
        teams = [t for t in teams if not t.startswith("http") and len(t) <= 8]
        if len(teams) < 2:
            continue

        # Extract round/note
        note_m = re.search(r"(Round \d+|Group Stage|Play.In|Upper|Lower|Grand Final)", block[:300])
        note = note_m.group(0) if note_m else ""

        results.append({
            "time": dt_twn.strftime("%H:%M"),
            "team1": teams[0],
            "team2": teams[1],
            "note": note,
        })

    return results


def get_matches(target_date: datetime.date) -> list[dict]:
    for url in _CANDIDATE_URLS:
        matches = _parse_page(url, target_date)
        if matches:
            return matches
    return []
