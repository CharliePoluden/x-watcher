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
        },
        timeout=10
    )


def check_account():
    response = requests.get(
        f"https://x.com/{USERNAME}",
        headers=HEADERS,
        timeout=15
    )

    html = response.text.lower()

    # если есть этот маркер — аккаунт suspended
    if "account suspended" in html:
        return False

    return True


try:
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
            notify(f"Loop error: {e}")

        time.sleep(CHECK_INTERVAL)

except Exception as e:
    notify(f"Startup error: {e}")
