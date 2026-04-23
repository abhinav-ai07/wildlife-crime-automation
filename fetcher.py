import csv
import requests
import time
from bs4 import BeautifulSoup

CSV_FILE = "data/raw_articles.csv"
LIMIT = 3  # keep small


def get_real_url(google_url):
    try:
        response = requests.get(google_url, allow_redirects=True, timeout=10)
        return response.url
    except Exception as e:
        print(f"Error resolving URL: {e}")
        return None


def fetch_article_content(url):
    try:
        response = requests.get(url, timeout=10)

        if response.status_code != 200:
            return None

        soup = BeautifulSoup(response.text, "html.parser")
        paragraphs = soup.find_all("p")

        content = " ".join([p.get_text() for p in paragraphs])
        return content.strip()

    except Exception as e:
        print(f"Error fetching article: {e}")
        return None


def update_articles_with_content():
    updated_rows = []
    processed = 0

    with open(CSV_FILE, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        # Check if content column exists
        fieldnames = reader.fieldnames
        if "content" not in fieldnames:
            fieldnames.append("content")

        for row in reader:
            if row["status"] == "new" and processed < LIMIT:
                print(f"Processing: {row['title']}")

                real_url = get_real_url(row["link"])

                if real_url:
                    content = fetch_article_content(real_url)

                    if content:
                        row["content"] = content[:2000]  # limit size
                    else:
                        row["content"] = ""

                processed += 1
                time.sleep(1)

            updated_rows.append(row)

    # Write back
    with open(CSV_FILE, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(updated_rows)

    print(f"\n✅ Added content for {processed} articles")


def run_fetcher():
    print("🚀 Running Article Content Fetcher...")
    update_articles_with_content()
    print("✅ Content fetching completed")    


if __name__ == "__main__":
    run_fetcher()