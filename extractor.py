import csv
import os
import sys
import json
import time
import requests
from config import OPENROUTER_API_KEY

# Fix Windows console encoding for emoji/unicode
try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass

CSV_FILE = "data/raw_articles.csv"
API_URL = "https://openrouter.ai/api/v1/chat/completions"
LIMIT = 3


def extract_json(text):
    """Robustly extract the first JSON object from a string."""
    try:
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            return json.loads(text[start:end + 1])
    except Exception as e:
        print(f"  [!] JSON parse error: {e}")
    return None


def extract_entities(content):
    """Call OpenRouter AI to extract structured crime data from article text."""
    if not OPENROUTER_API_KEY:
        print("❌ OPENROUTER_API_KEY missing. Check .env file.")
        return None

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://wildlife-crime-project",
        "X-Title": "Wildlife Crime Extractor",
    }

    prompt = f"""Extract structured information from the article below.

Return ONLY valid JSON, no explanation, no markdown:
{{
  "crime_type": "",
  "species": "",
  "location": "",
  "accused_count": ""
}}

Rules:
- Fill fields only if clearly mentioned in the article.
- If not found, leave as empty string "".
- accused_count should be a number or empty string.

Article:
{content[:3000]}
"""

    data = {
        "model": "openai/gpt-4o-mini",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0,
    }

    try:
        response = requests.post(API_URL, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        raw = response.json()["choices"][0]["message"]["content"].strip()
        print(f"  🔍 Raw AI output: {raw[:300]}")
        parsed = extract_json(raw)
        if parsed:
            return parsed
        else:
            print("  ⚠️ Could not parse JSON from AI response.")
            return None
    except requests.exceptions.HTTPError as e:
        print(f"  ⚠️ HTTP error from API: {e} — Response: {response.text[:200]}")
        return None
    except Exception as e:
        print(f"  ⚠️ API call failed: {e}")
        return None


def process_extractions():
    if not os.path.exists(CSV_FILE):
        print("❌ CSV not found:", CSV_FILE)
        return

    articles = []
    with open(CSV_FILE, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames or [])
        for row in reader:
            articles.append(row)

    if not articles:
        print("⚠️ CSV is empty.")
        return

    print(f"📂 Total rows in CSV: {len(articles)}")

    # Ensure extraction columns exist
    new_cols = ["crime_type", "species", "location", "accused_count"]
    for col in new_cols:
        if col not in fieldnames:
            fieldnames.append(col)

    # Debug: print state of all rows
    print("\n--- Row State ---")
    for i, row in enumerate(articles):
        status = row.get("status", "")
        content_len = len(row.get("content", ""))
        print(f"  Row {i+1}: status={repr(status)}, content_len={content_len}")
    print("-----------------\n")

    processed = 0
    updated = False

    for i, row in enumerate(articles):
        if processed >= LIMIT:
            print(f"[+] Limit of {LIMIT} API calls reached. Stopping.")
            break

        status = row.get("status", "").strip()
        content = row.get("content", "").strip()

        # Only process rows that have content and haven't been extracted yet
        if not content:
            print(f"[skip] Row {i+1}: no content (status={repr(status)})")
            continue

        if status == "extracted":
            print(f"[skip] Row {i+1}: already extracted")
            continue

        print(f"\n[*] Row {i+1}: Extracting entities (content={len(content)} chars)...")

        result = extract_entities(content)

        if result:
            row["crime_type"] = result.get("crime_type", "")
            row["species"] = result.get("species", "")
            row["location"] = result.get("location", "")
            row["accused_count"] = result.get("accused_count", "")
            row["status"] = "extracted"
            processed += 1
            updated = True
            print(f"  ✅ Extracted: {result}")
        else:
            print(f"  ❌ Extraction failed for row {i+1}")

        time.sleep(1)

    # Always write back to preserve all columns
    for row in articles:
        for col in new_cols:
            row.setdefault(col, "")

    with open(CSV_FILE, mode="w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(articles)

    if updated:
        print("\n✅ CSV updated with extracted data.")
    else:
        print("\n⚠️ No rows were updated (no content_fetched rows found).")

    print(f"\n📊 Processed: {processed}")


# Alias for main.py compatibility
run_extraction = process_extractions


if __name__ == "__main__":
    print("🚀 Running extractor...")
    process_extractions()