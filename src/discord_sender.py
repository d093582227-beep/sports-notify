import os
import requests


def send(content: str) -> bool:
    webhook_url = os.environ.get("DISCORD_WEBHOOK_URL", "")
    if not webhook_url:
        print("[discord] 缺少 DISCORD_WEBHOOK_URL 環境變數")
        return False

    try:
        resp = requests.post(webhook_url, json={"content": content}, timeout=10)
        if resp.status_code in (200, 204):
            print("[discord] 推送成功")
            return True
        print(f"[discord] 推送失敗 {resp.status_code}: {resp.text}")
        return False
    except Exception as e:
        print(f"[discord] 推送例外: {e}")
        return False
