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
    url = f"https://cdn.syndication.twimg.com/widgets/followbutton/info.json?screen_names={USERNAME}"

    response = requests.get(url, headers=HEADERS, timeout=15)

    if response.status_code != 200:
        return False

    data = response.json()

    if not data:
        return False

    return True


current_state = check_account()

if current_state:
    notify(f"Watcher started\n@{USERNAME} СЕЙЧАС ДОСТУПЕН")
else:
    notify(f"Watcher started\n@{USERNAME} СЕЙЧАС ЗАБЛОКИРОВАН / НЕ НАЙДЕН")

last_state = current_state

while True:
    try:
        current_state = check_account()

        if current_state != last_state:
            if current_state:
                notify(f"🚨 @{USERNAME} РАЗБЛОКИРОВАН")
            else:
                notify(f"⚠️ @{USERNAME} СНОВА НЕДОСТУПЕН")

            last_state = current_state

    except Exception as e:
        notify(f"Ошибка: {e}")

    time.sleep(CHECK_INTERVAL)
