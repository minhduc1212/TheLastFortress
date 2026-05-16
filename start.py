import os
import threading
import time
import subprocess
import uvicorn
from backend.app import app

def run_crawler():
    # Set data path for crawler
    data_dir = "/opt/render/project/src/data"
    data_file = "fmhy_all_data.json"
    
    # If on Render, move to the data directory
    if os.path.exists(data_dir):
        os.chdir(data_dir)

    # Get absolute path to crawler.py before changing directory
    crawler_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "crawler.py")

    while True:
        print("Starting crawler process...")
        try:
            # Run crawler.py as a separate process
            subprocess.run(["python", crawler_path], check=True)
            print("Crawler finished successfully. Waiting 12 hours...")
        except Exception as e:
            print(f"Crawler error: {e}. Retrying in 1 hour...")
            time.sleep(3600)
            continue
        
        time.sleep(12 * 60 * 60)

if __name__ == "__main__":
    # Start the crawler in a background thread
    crawler_thread = threading.Thread(target=run_crawler, daemon=True)
    crawler_thread.start()

    # Start the FastAPI server
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
