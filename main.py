import os
import sys
import time
import random
import requests
import re

USERNAME = os.environ.get("TWITTER_USERNAME")
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

STATE_FILE = "/data/last_status.txt"

MIN_DELAY = 60    # 1 минута
MAX_DELAY = 72    # 1.2 минуты

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

        # Проверка по внутренним данным (самый точный способ)
        if re.search(r'"screen_name"\s*:\s*"' + re.escape(username) + r'"', html):
            if "These Tweets are protected" in html:
                return "protected"
            return "active"

        error_pattern = r'"errors"\s*:\s*\{[^}]*"' + re.escape(username) + r'"\s*:\s*\{[^}]*"displayName"\s*:\s*"ApiError"'
        if re.search(error_pattern, html):
            return "suspended"

        fetch_fail = r'"fetchStatus"\s*:\s*\{[^}]*"' + re.escape(username.lower()) + r'"\s*:\s*"failed"'
        if re.search(fetch_fail, html):
            return "suspended"

        # Запасные проверки
        title_match = re.search(r"<title>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
        if title_match:
            title = title_match.group(1).strip().lower()
            if title == "account suspended":
                return "suspended"
            if "page not found" in title:
                return "not_found"

        if re.search(r"This account has been suspended", html, re.IGNORECASE):
            return "suspended"

        if "react-root" in html:
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
            return data if data else None
    except FileNotFoundError:
        return None

def write_last_status(status):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w") as f:
        f.write(status)

def get_status_with_retries(username, retries=3, delay=5):
    """Получить статус, повторяя попытки при 'unknown'."""
    for _ in range(retries):
        status = get_twitter_status(username)
        if status != "unknown":
            return status
        time.sleep(delay)
    return "unknown"

def main():
    if not all([USERNAME, BOT_TOKEN, CHAT_ID]):
        print("Missing required environment variables.")
        sys.exit(1)

    # Однократное стартовое уведомление (с повторными попытками)
    first_run = read_last_status() is None
    if first_run:
        current_status = get_status_with_retries(USERNAME)
        print(f"Initial status of @{USERNAME}: {current_status}")
        send_telegram_message(
            f"📡 Мониторинг аккаунта @{USERNAME} запущен.\n"
            f"Текущий статус: {current_status}"
        )
        # Сохраняем только если не unknown (иначе при следующем запуске снова попробуем)
        if current_status != "unknown":
            write_last_status(current_status)

    # Бесконечный цикл проверки
    while True:
        delay = random.uniform(MIN_DELAY, MAX_DELAY)
        print(f"Sleeping for {delay:.1f} seconds")
        time.sleep(delay)

        try:
            current_status = get_twitter_status(USERNAME)
            print(f"Status of @{USERNAME}: {current_status}")

            # Если статус unknown (капча/сбой), игнорируем, не обновляем состояние
            if current_status == "unknown":
                continue

            last_status = read_last_status()

            # Уведомление только при реальной разблокировке
            if last_status == "suspended" and current_status in ("active", "protected"):
                send_telegram_message(
                    f"🚀 Аккаунт @{USERNAME} разблокирован!\n"
                    f"Текущий статус: {current_status}"
                )

            # Обновляем сохранённый статус при любом изменении (кроме unknown)
            if last_status != current_status:
                write_last_status(current_status)

        except Exception as e:
            print(f"Error during check: {e}")
            # При ошибке продолжаем цикл

if __name__ == "__main__":
    main()
