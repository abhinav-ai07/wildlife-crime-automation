import csv
import os
import time
import requests
from bs4 import BeautifulSoup
import urllib3

# Suppress insecure request warnings if any
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

CSV_FILE = 'data/raw_articles.csv'
FIELDNAMES = ['title', 'link', 'published', 'status', 'content']
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
}

def resolve_google_news_url(google_url):
    """Resolves the real article URL from a Google News RSS link."""
    try:
        response = requests.get(google_url, headers=HEADERS, allow_redirects=True, timeout=5)
        response.raise_for_status()
        url = response.url
        if 'news.google.com' in url:
            print(f"[-] URL still points to Google News, skipping: {url}")
            return None
        return url
    except requests.exceptions.Timeout:
        print("[-] Timeout resolving URL.")
        return None
    except Exception as e:
        print(f"[-] Failed to resolve URL: {e}")
        return None

def fetch_and_extract_content(article_url):
    """Fetches the HTML of the article and extracts text from <p> tags."""
    try:
        response = requests.get(article_url, headers=HEADERS, timeout=5, verify=False)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        paragraphs = soup.find_all('p')
        
        # Join all paragraph text, stripping extra whitespace
        text_content = '\n'.join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])
        return text_content
    except requests.exceptions.Timeout:
        print("[-] Timeout fetching content.")
        return None
    except Exception as e:
        print(f"[-] Failed to fetch/extract content: {e}")
        return None

def process_articles():
    if not os.path.exists(CSV_FILE):
        print(f"[!] {CSV_FILE} not found. Please ensure the file exists.")
        return

    # Read existing articles
    articles = []
    with open(CSV_FILE, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        actual_fieldnames = list(reader.fieldnames) if reader.fieldnames else FIELDNAMES
        for row in reader:
            articles.append(row)

    if 'status' not in actual_fieldnames:
        actual_fieldnames.append('status')
    if 'content' not in actual_fieldnames:
        actual_fieldnames.append('content')

    # Process each article
    processed_count = 0
    updated = False
    
    for i, row in enumerate(articles):
        # 1. Process ONLY 3 articles per run
        if processed_count >= 3:
            print("[+] Limit of 3 valid articles reached. Stopping.")
            break
            
        # Avoid reprocessing
        if row.get('status') == 'content_fetched' and row.get('content') and len(row.get('content')) > 100:
            continue
            
        google_link = row.get('link')
        if not google_link:
            continue

        print(f"\n[*] Processing row {i+1}...")
        
        # 2. Convert Google News RSS links into real URLs
        real_url = resolve_google_news_url(google_link)
        if not real_url:
            row['status'] = 'failed_resolve'
            continue
            
        print(f"[+] Real URL: {real_url}")
        
        # 3 & 4. Fetch HTML and extract text
        content = fetch_and_extract_content(real_url)
        
        if content:
            content_length = len(content)
            print(f"[+] Content length: {content_length}")
            
            # 5. Ensure extracted content is NOT empty (length > 100)
            if content_length > 100:
                row['content'] = content
                row['status'] = 'content_fetched'
                updated = True
                processed_count += 1
            else:
                row['status'] = 'content_too_short'
                print("[-] Content too short, rejecting.")
        else:
            row['status'] = 'failed_extract'
        
        # Delay to prevent rate-limiting
        time.sleep(1)

    # Update CSV correctly
    if updated or len(articles) > 0:
        # Ensure 'status' and 'content' keys exist for DictWriter consistency
        for row in articles:
            row.setdefault('status', '')
            row.setdefault('content', '')

        with open(CSV_FILE, mode='w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=actual_fieldnames)
            writer.writeheader()
            writer.writerows(articles)
        print("\n[+] CSV updated successfully.")

if __name__ == '__main__':
    process_articles()
