import os
import time
import requests

USERNAME = os.getenv("USERNAME")
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

CHECK_INTERVAL = 30

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def notify(message):
    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        json={
            "chat_id": CHAT_ID,
            "text": message
        }
    )

def check_account():
    url = f"https://x.com/{USERNAME}"

    response = requests.get(url, headers=HEADERS, timeout=15)
    text = response.text.lower()

    return "account suspended" not in text

notify(f"Watcher started for @{USERNAME}")

last_state = check_account()

while True:
    current_state = check_account()

    if current_state != last_state:
        if current_state:
            notify(f"🚨 @{USERNAME} разблокирован")
        else:
            notify(f"@{USERNAME} снова заблокирован")

        last_state = current_state

    time.sleep(CHECK_INTERVAL)