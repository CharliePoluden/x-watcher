import os
import sys
import requests
import re

# ─── Конфигурация из переменных окружения ─────────────────────────────
USERNAME = os.environ.get("TWITTER_USERNAME")
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

STATE_FILE = "/data/last_status.txt"

# ─── Функции ─────────────────────────────────────────────────────────
def get_twitter_status(username):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
    }
    url = f"https://x.com/{username}"
    try:
        resp = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
        if resp.status_code == 404:
            return "not_found"
        if resp.status_code != 200:
            return "unknown"

        html = resp.text
        if re.search(r'(?:Account suspended|This account has been suspended|Suspended)', html, re.IGNORECASE):
            return "suspended"
        if "These Tweets are protected" in html:
            return "protected"
        if "react-root" in html and ("tweet" in html.lower() or "ProfileTweet" in html):
            return "active"
        return "unknown"
    except requests.RequestException:
        return "unknown"

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text}
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Failed to send Telegram message: {e}")

def read_last_status():
    try:
        with open(STATE_FILE, "r") as f:
            data = f.read().strip()
            return data if data else None   # пустой файл считаем отсутствием статуса
    except FileNotFoundError:
        return None

def write_last_status(status):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w") as f:
        f.write(status)

# ─── Основная логика ─────────────────────────────────────────────────
def main():
    if not all([USERNAME, BOT_TOKEN, CHAT_ID]):
        print("Missing required environment variables. Set TWITTER_USERNAME, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID.")
        sys.exit(1)

    current_status = get_twitter_status(USERNAME)
    print(f"Status of @{USERNAME}: {current_status}")

    last_status = read_last_status()

    # Первый запуск (или состояние потеряно) — сразу шлём информационное сообщение
    if last_status is None:
        send_telegram_message(
            f"📡 Мониторинг аккаунта @{USERNAME} запущен.\n"
            f"Текущий статус: {current_status}"
        )
        write_last_status(current_status)
        print("Initial status notification sent. Monitoring will continue from next run.")
        return   # на этом первый запуск завершён

    # Если аккаунт был заблокирован и теперь статус изменился (разблокировка)
    if last_status == "suspended" and current_status != "suspended":
        send_telegram_message(
            f"🚀 Аккаунт @{USERNAME} разблокирован!\n"
            f"Текущий статус: {current_status}"
        )
    # Обновляем сохранённый статус, если он изменился (в любом случае)
    if last_status != current_status:
        write_last_status(current_status)

if __name__ == "__main__":
    main()
