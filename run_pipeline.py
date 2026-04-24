import os
import sys
import time
from datetime import datetime

# Import modules
try:
    from collector import run_collector
    from filter import run_filter
    from fetcher import process_articles
    from extractor import process_extractions
except ImportError as e:
    print(f"❌ Error importing modules: {e}")
    sys.exit(1)

LOCK_FILE = "pipeline.lock"

def run_pipeline():
    """
    Orchestrates the full wildlife crime data pipeline.
    """
    # 1. Safety: Prevent simultaneous runs
    if os.path.exists(LOCK_FILE):
        print(f"[{datetime.now()}] ⚠️ Pipeline already running (lock file found).")
        print("If you are sure it is not running, delete 'pipeline.lock' and try again.")
        return

    try:
        # Create lock file
        with open(LOCK_FILE, "w") as f:
            f.write(str(os.getpid()))

        start_time = datetime.now()
        print(f"\n{'='*60}")
        print(f"🚀 PIPELINE AUTOMATION STARTED: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}\n")

        # Step 1: News Collection
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 📂 STEP 1: Collecting news articles...")
        run_collector()

        # Step 2: Relevance Filtering
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 🔍 STEP 2: Filtering for relevant crimes...")
        run_filter()

        # Step 3: Content Fetching
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 🌐 STEP 3: Fetching full article content...")
        process_articles()

        # Step 4: Data Extraction
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 🧠 STEP 4: Extracting structured data to DB...")
        process_extractions()

        end_time = datetime.now()
        duration = end_time - start_time
        
        print(f"\n{'='*60}")
        print(f"✅ PIPELINE COMPLETED SUCCESSFULLY: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"⏱️ Total duration: {duration}")
        print(f"{'='*60}\n")

    except Exception as e:
        print(f"\n❌ PIPELINE CRITICAL FAILURE at {datetime.now().strftime('%H:%M:%S')}")
        print(f"Error details: {e}")
        # Re-raise to alert caller
        raise
    finally:
        # Always remove lock file
        if os.path.exists(LOCK_FILE):
            os.remove(LOCK_FILE)

if __name__ == "__main__":
    run_pipeline()
