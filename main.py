from collector import fetch_news, save_to_csv
from filter import update_relevance
from fetcher import process_articles
from extractor import process_extractions

print("\n🚀 STEP 1: Collecting news...")
news = fetch_news()
save_to_csv(news)

print("\n🚀 STEP 2: Filtering relevance...")
update_relevance()

print("\n🚀 STEP 3: Fetching article content...")
process_articles()

print("\n🚀 STEP 4: Extracting structured data...")
process_extractions()

print("\n✅ PIPELINE COMPLETED")