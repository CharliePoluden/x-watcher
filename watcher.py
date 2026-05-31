import os
import requests

USERNAME = os.getenv("USERNAME")
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def notify(message):
    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        json={
            "chat_id": CHAT_ID,
            "text": message[:3500]
        }
    )

response = requests.get(
    f"https://x.com/{USERNAME}",
    headers={"User-Agent": "Mozilla/5.0"},
    timeout=15
)

html = response.text.lower()

has_marker = "account suspended" in html

notify(
    f"status={response.status_code}\n"
    f"marker={has_marker}\n\n"
    f"{html[:2500]}"
)
