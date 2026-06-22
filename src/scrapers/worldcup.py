import datetime
import re
import requests
from bs4 import BeautifulSoup
from zoneinfo import ZoneInfo

URL = "https://liquipedia.net/lab/Football/FIFA/World_Cup/2026"
SOURCE_TZ = ZoneInfo("America/New_York")  # EDT/EST
TARGET_TZ = ZoneInfo("Asia/Taipei")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; sports-notify/1.0; +https://github.com/sports-notify)",
    "Accept-Language": "en-US,en;q=0.9",
}

# Regex: "Jun 22 - 13:00 EDT" or "Jun 22 - 13:00 EST"
_TIME_RE = re.compile(
    r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*\s+(\d{1,2})\s*-\s*(\d{2}:\d{2})\s*E[DS]T",
    re.IGNORECASE,
)
_MONTH_MAP = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
}


def _parse_team_name(text: str) -> str:
    """Extract team name/code from a markdown-style link text like [ARG] or [France]."""
    text = text.strip()
    # Strip surrounding brackets if present
    m = re.match(r"^\[([^\]]+)\]", text)
    return m.group(1) if m else text


def get_matches(target_date: datetime.date) -> list[dict]:
    try:
        resp = requests.get(URL, headers=HEADERS, timeout=15)
        resp.raise_for_status()
    except Exception as e:
        print(f"[worldcup] 無法取得頁面: {e}")
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    text = soup.get_text(" ", strip=True)

    results = []
    # Split text on time markers to get match blocks
    parts = _TIME_RE.split(text)

    # parts: [pre, month, day, time, post, month, day, time, post, ...]
    # Every 4 elements after the first is: month, day, time, text_block
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

        # Build a naive datetime in source TZ, then convert to TWN
        year = target_date.year
        try:
            dt_source = datetime.datetime(year, month, day, hour, minute, tzinfo=SOURCE_TZ)
        except ValueError:
            continue
        dt_twn = dt_source.astimezone(TARGET_TZ)

        if dt_twn.date() != target_date:
            continue

        # Extract team codes/names: 2-5 uppercase letters in brackets
        teams = re.findall(r"\[([A-Z]{2,5})\]", block[:500])
        if len(teams) < 2:
            continue

        results.append({
            "time": dt_twn.strftime("%H:%M"),
            "team1": teams[0],
            "team2": teams[1],
            "note": "",
        })

    return results
