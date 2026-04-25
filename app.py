import os
import time
import threading
from flask import Flask, jsonify, send_from_directory
from run_pipeline import run_pipeline, LOCK_FILE
from db import fetch_recent

app = Flask(__name__)

@app.route('/')
def index():
    """Serve the frontend index.html."""
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def static_files(path):
    """Serve other static files (css, js, images)."""
    return send_from_directory('.', path)

def is_pipeline_running():
    """Check if the pipeline is currently running by looking for the lock file."""
    if os.path.exists(LOCK_FILE):
        # Check if stale (older than 10 minutes)
        file_age_seconds = time.time() - os.path.getmtime(LOCK_FILE)
        if file_age_seconds > 600:
            print(f"[API] Found stale lock file ({int(file_age_seconds)}s old). Removing it.")
            try:
                os.remove(LOCK_FILE)
                return False
            except Exception as e:
                print(f"[API] Error removing stale lock: {e}")
                return True  # Assume still locked if we can't remove it
        return True
    return False

@app.route('/run-pipeline', methods=['GET'])
def trigger_pipeline():
    """Endpoint to trigger the wildlife crime data pipeline."""
    print(f"[{time.strftime('%H:%M:%S')}] 📡 API: GET /run-pipeline hit")
    
    if is_pipeline_running():
        print(f"[{time.strftime('%H:%M:%S')}] ⚠️ API: Pipeline already running. Skipping trigger.")
        return jsonify({"status": "already_running"}), 200
    
    # Trigger in background thread to avoid blocking the API response
    print(f"[{time.strftime('%H:%M:%S')}] 🚀 API: Triggering pipeline automation...")
    try:
        thread = threading.Thread(target=run_pipeline)
        thread.daemon = True
        thread.start()
        return jsonify({"status": "started"}), 200
    except Exception as e:
        print(f"[{time.strftime('%H:%M:%S')}] ❌ API: Error starting pipeline: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/data', methods=['GET'])
def get_data():
    """Endpoint to fetch the latest 20 rows of processed wildlife crime data."""
    print(f"[{time.strftime('%H:%M:%S')}] 📡 API: GET /data hit")
    try:
        records = fetch_recent(20)
        return jsonify(records), 200
    except Exception as e:
        print(f"[{time.strftime('%H:%M:%S')}] ❌ API: Error fetching data: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    """Endpoint to check the health status of the API service."""
    print(f"[{time.strftime('%H:%M:%S')}] 📡 API: GET /health hit")
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    print("\n" + "="*50)
    print("🌟 WILDLIFE CRIME BACKEND API SERVICE")
    print("="*50)
    print(f"Running at: http://127.0.0.1:5000")
    print("\nEndpoints:")
    print("  🔗 GET /run-pipeline -> Triggers system")
    print("  🔗 GET /data         -> Returns latest 20 results")
    print("  🔗 GET /health       -> Returns system status")
    print("="*50 + "\n")
    
    # host='0.0.0.0' allows external access if needed
    app.run(host='0.0.0.0', port=5000, debug=False)
