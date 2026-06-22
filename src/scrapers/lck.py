"""
LCK scraper：依照目標日期選對應賽段頁面。
"""
import datetime
from ._common import fetch_matches

# LCK 2026 各賽段日期範圍與對應 URL
_ROUNDS = [
    (datetime.date(2026, 4, 1),  datetime.date(2026, 5, 31), "https://liquipedia.net/leagueoflegends/LCK/2026/Rounds_1-2"),
    (datetime.date(2026, 6, 1),  datetime.date(2026, 6, 20), "https://liquipedia.net/leagueoflegends/LCK/2026/Road_to_MSI"),
    (datetime.date(2026, 7, 15), datetime.date(2026, 9, 13), "https://liquipedia.net/leagueoflegends/LCK/2026/Rounds_3-4"),
]


def get_matches(target_date: datetime.date) -> list[dict]:
    for start, end, url in _ROUNDS:
        if start <= target_date <= end:
            return fetch_matches(url, target_date)
    return []
