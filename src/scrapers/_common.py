"""
共用 Liquipedia scraper 邏輯：
- 兩個 wiki（Lab football / LoL）都使用 data-timestamp + .block-team 結構
"""
import datetime
import requests
from bs4 import BeautifulSoup
from zoneinfo import ZoneInfo

TARGET_TZ = ZoneInfo("Asia/Taipei")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; sports-notify/1.0; +https://github.com/sports-notify)",
    "Accept-Language": "en-US,en;q=0.9",
}


def fetch_matches(url: str, target_date: datetime.date) -> list[dict]:
    """
    從 Liquipedia 頁面抓取指定 TWN 日期的賽程。
    回傳 list[{time, team1, team2, note}]，失敗時回傳 []。
    """
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
    except Exception as e:
        print(f"[scraper] 無法取得 {url}: {e}")
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    results = []

    for timer in soup.select("span.timer-object[data-timestamp]"):
        ts = timer.get("data-timestamp", "")
        if not ts:
            continue
        try:
            dt_twn = datetime.datetime.fromtimestamp(int(ts), tz=TARGET_TZ)
        except (ValueError, OSError):
            continue

        if dt_twn.date() != target_date:
            continue

        # 往上 3 層找到 match-info 容器
        container = timer.parent.parent.parent
        if container is None:
            continue

        # 提取兩隊名稱（.block-team 中有文字的第一個 <a>）
        teams = []
        for bt in container.select(".block-team"):
            for a in bt.select("a"):
                txt = a.get_text(strip=True)
                if txt:
                    teams.append(txt)
                    break

        if len(teams) < 2:
            continue

        # 賽段標注（Round X / Group Stage / Play-In 等）
        stage_el = container.select_one(".match-info-stage, .match-countdown-block-note")
        note = stage_el.get_text(strip=True) if stage_el else ""
        # 去掉只有日期的 note（例如 "June 22"）
        if note and note.replace(" ", "").isalpha() is False and len(note) < 20:
            import re
            if re.match(r"^[A-Z][a-z]+ \d+$", note):
                note = ""

        results.append({
            "time": dt_twn.strftime("%H:%M"),
            "team1": teams[0],
            "team2": teams[1],
            "note": note,
        })

    return results
