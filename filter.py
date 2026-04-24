import csv
import time
from openai import OpenAI
from config import OPENROUTER_API_KEY

CSV_FILE = "data/raw_articles.csv"

# 🔹 Limit API calls per run (VERY IMPORTANT)
LIMIT = 5

# ✅ AI Client
client = OpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1"
)


# ✅ Strict relevance check
def is_relevant(title):
    prompt = f"""
You are a strict classifier.

Return ONLY:
true → ONLY if the headline clearly describes wildlife crime such as poaching, trafficking, smuggling, illegal hunting, or animal killing.

false → if it is about conservation, tourism, government policy, awareness, or general news.

Do NOT guess. Be strict.

Headline: "{title}"
"""

    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b:free",
            messages=[{"role": "user", "content": prompt}]
        )

        answer = response.choices[0].message.content.strip().lower()
        return "true" in answer

    except Exception as e:
        print(f"⚠️ API Error: {e}")
        return None  # ✅ IMPORTANT FIX (don’t force True)


# ✅ Update CSV with AI results (BATCH MODE)
def update_relevance():
    updated_rows = []
    total = 0
    changed = 0
    processed = 0

    with open(CSV_FILE, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        # Safety check
        if reader.fieldnames is None:
            print("❌ CSV is empty or corrupted")
            return

        # Capture ALL fieldnames so we don't drop columns like 'content'
        all_fieldnames = list(reader.fieldnames)

        for row in reader:
            total += 1

            # Skip invalid rows safely
            if not row.get("status") or not row.get("title"):
                updated_rows.append(row)
                continue

            # 🔥 Process only LIMITED new rows
            if row["status"] == "new" and processed < LIMIT:
                title = row["title"]

                result = is_relevant(title)

                print(f"Checking: {title}")
                print(f"→ Relevant: {result}")
                print("-" * 50)

                # ✅ Only update if AI responded properly
                if result is False:
                    row["status"] = "irrelevant"
                    changed += 1

                processed += 1
                time.sleep(1)

            updated_rows.append(row)

    # ✅ Write updated data back — preserve ALL columns from original fieldnames
    with open(CSV_FILE, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=all_fieldnames,
            extrasaction='ignore'
        )

        writer.writeheader()
        writer.writerows(updated_rows)

    print("\n✅ Relevance filtering completed")
    print(f"📊 Total articles in file: {total}")
    print(f"⚙️ Processed this run: {processed}")
    print(f"❌ Marked irrelevant: {changed}")


# ✅ FINAL PIPELINE FUNCTION
def run_filter():
    print("🚀 Running Relevance Filter...")
    update_relevance()
    print("✅ Filter step completed")


# ✅ Main entry
if __name__ == "__main__":
    run_filter()