"""
LOL 國際賽 scraper：自動嘗試當前賽事（MSI → Worlds）。
第一個有資料的賽事頁面優先。
"""
import datetime
from ._common import fetch_matches

_CANDIDATE_URLS = [
    "https://liquipedia.net/leagueoflegends/Mid-Season_Invitational/2026",
    "https://liquipedia.net/leagueoflegends/World_Championship/2026",
]


def get_matches(target_date: datetime.date) -> list[dict]:
    for url in _CANDIDATE_URLS:
        matches = fetch_matches(url, target_date)
        if matches:
            return matches
    return []
