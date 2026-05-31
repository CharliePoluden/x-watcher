import os
import time
import requests
from playwright.sync_api import sync_playwright

USERNAME = os.getenv("USERNAME")
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

CHECK_INTERVAL = 30


def notify(msg):
    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        json={"chat_id": CHAT_ID, "text": msg},
        timeout=10
    )


def is_suspended():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto(f"https://x.com/{USERNAME}", wait_until="domcontentloaded")

        html = page.content().lower()

        browser.close()

        return "account suspended" in html


state = is_suspended()

notify(
    f"Watcher started\n@{USERNAME} "
    f"{'СЕЙЧАС ЗАБЛОКИРОВАН' if state else 'СЕЙЧАС ДОСТУПЕН'}"
)

last = state

while True:
    try:
        state = is_suspended()

        if state != last:
            if state:
                notify(f"⚠️ @{USERNAME} ЗАБЛОКИРОВАН")
            else:
                notify(f"🚨 @{USERNAME} РАЗБЛОКИРОВАН")

            last = state

    except Exception as e:
        notify(f"error: {e}")

    time.sleep(CHECK_INTERVAL)
