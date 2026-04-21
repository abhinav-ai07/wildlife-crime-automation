import feedparser
import csv
import os

CSV_FILE = "data/raw_articles.csv"


def fetch_news():
    url = "https://news.google.com/rss/search?q=wildlife+crime+india"
    feed = feedparser.parse(url)

    articles = []

    for entry in feed.entries:
        article = {
            "title": entry.title,
            "link": entry.link,
            "published": entry.published,
            "status": "new"   # ✅ NEW FIELD ADDED
        }
        articles.append(article)

    return articles


def save_to_csv(articles):
    file_exists = os.path.isfile(CSV_FILE)
    existing_links = load_existing_links()

    new_articles = []

    for article in articles:
        if article["link"] not in existing_links:
            new_articles.append(article)

    with open(CSV_FILE, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=["title", "link", "published", "status"]  # ✅ UPDATED
        )

        if not file_exists:
            writer.writeheader()

        for article in new_articles:
            writer.writerow(article)

    print(f"Added {len(new_articles)} new articles (duplicates removed)")


def load_existing_links():
    if not os.path.isfile(CSV_FILE):
        return set()

    existing_links = set()

    with open(CSV_FILE, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        # If file is empty or corrupted
        if reader.fieldnames is None:
            print("⚠️ CSV file is empty or corrupted")
            return set()

        if "link" not in reader.fieldnames:
            print("⚠️ 'link' column missing")
            return set()

        for row in reader:
            if row.get("link"):
                existing_links.add(row["link"])

    return existing_links


def run_collector():
    print("🚀 Running News Collector...")

    news = fetch_news()
    save_to_csv(news)

    print(f"✅ Finished. Total fetched: {len(news)}")


if __name__ == "__main__":
    run_collector()