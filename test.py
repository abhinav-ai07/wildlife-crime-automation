"""
The c-wiz tag is missing — Google changes structure. Let's search for data-p anywhere.
Also look at the session storage / AF_initDataCallback which often has article info.
"""
import requests, re

url = "https://news.google.com/articles/CBMiggFBVV95cUxOT3MwV3FFakE1cV83QmtlaXJqb3BCS2NKVjNjaUVWT3ZPS0NzQml2VjlkV1RGZldocUhjQzBldjAwT0t5TG0wYkVqY3diOWxaOUE3MDk3ZVJndmNIX2ZSb2d1eEE2R0dqWU5KbVV1bXZZMzRzTGV4cUlCaDd3ZnJyYTh3"

r = requests.get(url, headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}, timeout=10)

html = r.text

# Look for AF_initDataCallback
af_data = re.findall(r'AF_initDataCallback\((.+?)\);', html, re.DOTALL)
print(f"AF_initDataCallback blocks: {len(af_data)}")
for i, block in enumerate(af_data[:3]):
    print(f"\nBlock {i}:", block[:300])

# Look for any data-p attribute
dp = re.findall(r'data-p="([^"]+)"', html)
print(f"\ndata-p attributes: {len(dp)}")
for d in dp[:3]:
    print(d[:400])
