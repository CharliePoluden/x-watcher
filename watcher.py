import os
import time
import requests
from playwright.sync_api import sync_playwright

USERNAME = os.getenv("USERNAME")
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

CHECK_INTERVAL = 30


def notify(message):
    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        json={
            "chat_id": CHAT_ID,
            "text": message
        },
        timeout=10
    )


def check_account():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto(f"https://x.com/{USERNAME}", wait_until="networkidle")

        content = page.content().lower()

        browser.close()

        suspended_markers = [
            "account suspended",
            "действие учетной записи приостановлено",
            "this account is suspended"
        ]

        for marker in suspended_markers:
            if marker in content:
                return False

        return True


current_state = check_account()

if current_state:
    notify(f"Watcher started\n@{USERNAME} СЕЙЧАС ДОСТУПЕН")
else:
    notify(f"Watcher started\n@{USERNAME} СЕЙЧАС ЗАБЛОКИРОВАН")

last_state = current_state

while True:
    try:
        current_state = check_account()

        if current_state != last_state:
            if current_state:
                notify(f"🚨 @{USERNAME} РАЗБЛОКИРОВАН")
            else:
                notify(f"⚠️ @{USERNAME} СНОВА ЗАБЛОКИРОВАН")

            last_state = current_state

    except Exception as e:
        notify(f"Ошибка: {e}")

    time.sleep(CHECK_INTERVAL)
