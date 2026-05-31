import requests
import time

print("STARTED", flush=True)

url = "https://cdn.syndication.twimg.com/widgets/followbutton/info.json?screen_names=pitch_erc"

try:
    r = requests.get(url, timeout=15)
    print("STATUS:", r.status_code, flush=True)
    print("TEXT:", r.text[:1000], flush=True)
except Exception as e:
    print("ERROR:", e, flush=True)

while True:
    print("alive...", flush=True)
    time.sleep(60)
