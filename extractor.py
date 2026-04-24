import csv
import os
import json
import time
import requests

CSV_FILE = "data/raw_articles.csv"
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
API_URL = "https://openrouter.ai/api/v1/chat/completions"

LIMIT = 3  # 🔥 process only 3 per run


# ✅ CLEAN JSON EXTRACTOR
def extract_json(text):
    try:
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1:
            return json.loads(text[start:end+1])
    except:
        return None
    return None


# ✅ AI CALL
def extract_entities(content):
    if not OPENROUTER_API_KEY:
        print("❌ API key missing")
        return None

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    prompt = f"""
Extract structured information from the article.

Return ONLY JSON:
{{
  "crime_type": "",
  "species": "",
  "location": "",
  "accused_count": ""
}}

Rules:
- If not found → ""
- No explanation

Article:
{content[:3000]}
"""

    data = {
        "model": "openai/gpt-oss-120b:free",
        "messages": [{"role": "user", "content": prompt}]
    }

    try:
        response = requests.post(API_URL, headers=headers, json=data, timeout=30)
        response.raise_for_status()

        raw = response.json()["choices"][0]["message"]["content"].strip()

        print("🔍 Raw AI Output:", raw[:200])

        parsed = extract_json(raw)

        if parsed:
            return parsed
        else:
            print("⚠️ JSON parsing failed")
            return None

    except Exception as e:
        print("⚠️ API Error:", e)
        return None


# ✅ MAIN PROCESS
def process_extractions():
    if not os.path.exists(CSV_FILE):
        print("❌ CSV not found")
        return

    articles = []

    with open(CSV_FILE, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames or [])

        for row in reader:
            articles.append(row)

    # Ensure columns exist
    new_cols = ["crime_type", "species", "location", "accused_count"]

    for col in new_cols:
        if col not in fieldnames:
            fieldnames.append(col)

    processed = 0
    updated = False

    for i, row in enumerate(articles):
        print(f"\nRow {i+1}")
        print("STATUS:", row.get("status"))
        print("CONTENT LENGTH:", len(row.get("content", "")))
    
        if row.get("content"):
          print("✅ HAS CONTENT")

    # Save back
    if updated:
        with open(CSV_FILE, mode="w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(articles)

        print("\n✅ CSV updated")

    print(f"\n📊 Processed: {processed}")


if __name__ == "__main__":
    print("🚀 Running extractor...")
    process_extractions()