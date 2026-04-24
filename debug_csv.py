import csv

with open('data/raw_articles.csv', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    rows = list(reader)
    print("Fieldnames:", reader.fieldnames)
    print("Total rows:", len(rows))
    for i, row in enumerate(rows[:10]):
        print(f"Row {i+1}: status={repr(row.get('status'))}, content_len={len(row.get('content', ''))}")
