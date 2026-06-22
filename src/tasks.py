"""
進入點：python src/tasks.py morning|evening
"""
import sys
import datetime
from zoneinfo import ZoneInfo
from dotenv import load_dotenv

load_dotenv()

from scrapers import worldcup, lck, lol_international
from formatter import format_message
from discord_sender import send

TWN = ZoneInfo("Asia/Taipei")


def run(mode: str) -> None:
    now_twn = datetime.datetime.now(tz=TWN)

    if mode == "morning":
        target_date = now_twn.date()
        is_preview = False
    elif mode == "evening":
        target_date = (now_twn + datetime.timedelta(days=1)).date()
        is_preview = True
    else:
        print(f"未知模式：{mode}，請用 morning 或 evening")
        sys.exit(1)

    print(f"[tasks] 模式={mode}，查詢日期={target_date}")

    wc = worldcup.get_matches(target_date)
    lck_matches = lck.get_matches(target_date)
    intl = lol_international.get_matches(target_date)

    print(f"[tasks] 世界盃={len(wc)} 場，LCK={len(lck_matches)} 場，國際賽={len(intl)} 場")

    message = format_message(target_date, wc, lck_matches, intl, is_preview=is_preview)

    if message is None:
        print("[tasks] 今日三個賽事均無場次，略過推送")
        return

    success = send(message)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法：python src/tasks.py morning|evening")
        sys.exit(1)
    run(sys.argv[1])
