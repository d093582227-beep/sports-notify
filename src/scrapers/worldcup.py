import datetime
from ._common import fetch_matches

URL = "https://liquipedia.net/lab/Football/FIFA/World_Cup/2026"


def get_matches(target_date: datetime.date) -> list[dict]:
    return fetch_matches(URL, target_date)
