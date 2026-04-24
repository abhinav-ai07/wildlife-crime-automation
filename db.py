import sqlite3
import os

DB_FILE = "wildlife.db"


def get_connection():
    """Return a new SQLite connection to the wildlife database."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def create_database():
    """Create the database and crimes table if they don't already exist."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS crimes (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                title         TEXT,
                link          TEXT UNIQUE,
                published     TEXT,
                crime_type    TEXT,
                species       TEXT,
                location      TEXT,
                accused_count TEXT
            )
        """)
        conn.commit()
        print(f"[DB] Database ready: {os.path.abspath(DB_FILE)}")
    except Exception as e:
        print(f"[DB] Error creating database: {e}")
    finally:
        conn.close()


def check_duplicate(link):
    """Return True if a row with the given link already exists in crimes."""
    if not link:
        return False
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM crimes WHERE link = ?", (link,))
        return cursor.fetchone() is not None
    except Exception as e:
        print(f"[DB] Error checking duplicate: {e}")
        return False
    finally:
        conn.close()


def insert_into_db(row):
    """
    Insert a single extracted row into the crimes table.
    Skips if the link already exists (UNIQUE constraint).
    Returns True if inserted, False if skipped or error.
    """
    link = row.get("link", "").strip()

    if check_duplicate(link):
        print(f"  [DB] Skipped duplicate: {link[:80]}")
        return False

    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO crimes (title, link, published, crime_type, species, location, accused_count)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            row.get("title", "").strip(),
            link,
            row.get("published", "").strip(),
            row.get("crime_type", "").strip(),
            row.get("species", "").strip(),
            row.get("location", "").strip(),
            str(row.get("accused_count", "")).strip(),
        ))
        conn.commit()
        print(f"  [DB] Inserted into DB: {row.get('title', link)[:80]}")
        return True
    except sqlite3.IntegrityError:
        # Race condition: already inserted between check and insert
        print(f"  [DB] Skipped duplicate (integrity): {link[:80]}")
        return False
    except Exception as e:
        print(f"  [DB] Insert error: {e}")
        return False
    finally:
        conn.close()


def fetch_all():
    """Return all rows from the crimes table."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM crimes ORDER BY id")
        return [dict(r) for r in cursor.fetchall()]
    except Exception as e:
        print(f"[DB] Error fetching records: {e}")
        return []
    finally:
        conn.close()


if __name__ == "__main__":
    create_database()
    records = fetch_all()
    print(f"\n[DB] Total records in crimes table: {len(records)}")
    for r in records:
        print(f"  id={r['id']} | {r['title'][:50]} | {r['crime_type']} | {r['location']}")