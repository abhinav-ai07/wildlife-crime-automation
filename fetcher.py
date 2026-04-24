import csv
import os
import time
import requests
from bs4 import BeautifulSoup
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

CSV_FILE = 'data/raw_articles.csv'
FIELDNAMES = ['title', 'link', 'published', 'status', 'content']
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
}
LIMIT = 3


def decode_google_news_url(google_url):
    """
    Attempts to get the real article URL from a Google News link using googlenewsdecoder.
    """
    try:
        from googlenewsdecoder import new_decoderv1
        res = new_decoderv1(google_url)
        if res.get('status') and res.get('decoded_url'):
            candidate = res['decoded_url']
            if 'news.google.com' not in candidate and candidate.startswith('http'):
                return candidate
            else:
                print(f"  [skip] Decoded URL still contains news.google.com or is invalid: {candidate}")
    except ImportError:
        print("  [-] googlenewsdecoder not installed. Please run: pip install googlenewsdecoder")
    except Exception as e:
        print(f"  [-] Decode failed: {e}")

    print(f"  [-] Could not resolve URL, still google: {google_url[:80]}")
    return None


def fetch_content(url):
    """Fetches article HTML and extracts paragraph text."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10, verify=False, allow_redirects=True)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, 'html.parser')

        # Remove script/style noise
        for tag in soup(['script', 'style', 'nav', 'footer', 'header']):
            tag.decompose()

        paragraphs = soup.find_all('p')
        text = '\n'.join(p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 30)
        return text
    except requests.exceptions.Timeout:
        print("  [-] Timeout fetching content.")
        return None
    except Exception as e:
        print(f"  [-] Fetch/extract error: {e}")
        return None


def process_articles():
    if not os.path.exists(CSV_FILE):
        print(f"[!] {CSV_FILE} not found.")
        return

    articles = []
    with open(CSV_FILE, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames) if reader.fieldnames else FIELDNAMES[:]
        for row in reader:
            articles.append(row)

    # Ensure columns exist
    for col in ['status', 'content']:
        if col not in fieldnames:
            fieldnames.append(col)

    processed_count = 0

    for i, row in enumerate(articles):
        if processed_count >= LIMIT:
            print(f"\n[+] Limit of {LIMIT} articles reached. Stopping.")
            break

        current_status = row.get('status', '').strip()
        current_content = row.get('content', '').strip()

        # Skip already processed rows: status must be "new" and content must be empty
        if current_status != 'new' or current_content:
            print(f"[skip] Row {i+1}: Skipping already processed row (status={current_status})")
            continue

        google_link = row.get('link', '').strip()
        if not google_link:
            print(f"[skip] Row {i+1}: no link")
            continue

        print(f"\n[*] Row {i+1}: Processing new row...")
        print(f"    Source: {google_link[:80]}")

        real_url = decode_google_news_url(google_link)
        if not real_url:
            row['status'] = 'failed_resolve'
            print(f"  [skip] Marked as failed_resolve - skip reason: unable to resolve true URL")
            continue

        if 'news.google.com' in real_url:
            row['status'] = 'failed_resolve'
            print(f"  [skip] Marked as failed_resolve - skip reason: resolved URL still contains news.google.com")
            continue

        print(f"  [+] Real URL: {real_url}")
        content = fetch_content(real_url)

        if content and len(content) > 100:
            row['content'] = content
            row['status'] = 'content_fetched'
            processed_count += 1
            print(f"  [+] Content saved: {len(content)} chars")
        elif content:
            row['status'] = 'content_too_short'
            print(f"  [skip] Content too short ({len(content)} chars) - skip reason: below 100 chars")
        else:
            row['status'] = 'failed_extract'
            print(f"  [skip] No content extracted - skip reason: failed to extract usable text from <p> tags")

        time.sleep(1.5)

    # Write back
    for row in articles:
        row.setdefault('status', '')
        row.setdefault('content', '')

    with open(CSV_FILE, mode='w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(articles)

    print(f"\n[+] CSV updated. Content fetched for {processed_count} article(s).")


if __name__ == '__main__':
    process_articles()
