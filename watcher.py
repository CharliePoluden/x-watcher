import requests
print(requests.get("https://cdn.syndication.twimg.com/widgets/followbutton/info.json?screen_names=pitch_erc").text)
