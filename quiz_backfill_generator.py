import requests
import logging
from datetime import datetime, timedelta
import web_generator

# Setup logging to console for visibility
logging.basicConfig(level=logging.INFO, format='%(message)s')

# GitLab Raw Data Base URL
BASE_GITLAB = "https://gitlab.com/Mahadi07/rtejhs/-/raw/main/EdData/data"

def fetch_json(url):
    """Helper to fetch JSON data from GitLab."""
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        return response.json()
    except Exception:
        return None

def backfill_quizzes(start_date_str, end_date_str):
    """Iterates through dates and generates quiz pages for both BN and HN."""
    start_dt = datetime.strptime(start_date_str, "%d-%m-%Y")
    end_dt = datetime.strptime(end_date_str, "%d-%m-%Y")
    
    current_dt = start_dt
    while current_dt <= end_dt:
        date_str = current_dt.strftime("%d-%m-%Y")
        print(f"🚀 Processing Quiz Backfill: {date_str}")
        
        # Configs for Bengali and Hindi quiz sources
        configs = [
            {"lang": "bn", "folder": "DayOfTheQuizEnToBn"},
            {"lang": "hn", "folder": "DayOfTheQuizEnToHn"}
        ]
        
        for cfg in configs:
            url = f"{BASE_GITLAB}/{cfg['folder']}/{date_str}.json"
            quiz_data = fetch_json(url)
            
            if quiz_data and quiz_data.get("questions"):
                web_generator.generate_quiz_page(cfg['lang'], quiz_data, date_str)
                print(f"  ✅ Generated {cfg['lang']} quiz page")
        
        current_dt += timedelta(days=1)

    # Re-build sitemap and indexes to include all new pages
    web_generator.regenerate_static_pages()
    print("\n✨ Quiz backfill complete. Site indexes and sitemap updated.")

if __name__ == "__main__":
    # Run the backfill for the requested range
    backfill_quizzes("20-05-2026", "12-06-2026")