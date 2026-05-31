import os
import re
import requests

USERNAME = os.getenv("USERNAME")
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

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

url = f"https://x.com/{USERNAME}"

response = requests.get(url, headers=HEADERS, timeout=15)
html = response.text

title_match = re.search(r"<title>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)

title = title_match.group(1).strip() if title_match else "NO TITLE"

notify(
    f"STATUS: {response.status_code}\n"
    f"TITLE: {title}\n"
    f"HTML SAMPLE:\n{html[:500]}"
)
