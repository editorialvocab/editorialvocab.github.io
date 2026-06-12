import requests
import json
from datetime import datetime
from pathlib import Path
import web_generator
import logging

# Setup basic logging to see the output in the console
logging.basicConfig(level=logging.INFO, format='%(message)s')

# GitLab Raw Data Base URL
BASE_GITLAB = "https://gitlab.com/Mahadi07/rtejhs/-/raw/main/EdData/data"

def fetch_json(url):
    """Helper to fetch JSON data from GitLab."""
    try:
        # Using a clean URL without UI query parameters like ?and or ?ref_type
        clean_url = url.split('?')[0]
        response = requests.get(clean_url, timeout=15)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"  ❌ Error fetching {url}: {e}")
        return None

def backfill_date(target_date):
    """
    Generates WOTD and Vocab pages for a specific date.
    target_date: Format "DD-MM-YYYY" (e.g., "01-06-2026")
    """
    try:
        dt = datetime.strptime(target_date, "%d-%m-%Y")
    except ValueError:
        print("  ❌ Invalid date format. Please use DD-MM-YYYY (e.g., 01-06-2026).")
        return

    month_year = dt.strftime("%m-%Y")        # 06-2026
    month_name = dt.strftime("%B")           # June
    search_date_std = f"{dt.day} {month_name} {dt.year}"    # "1 June 2026"
    search_date_pad = f"{dt.day:02d} {month_name} {dt.year}" # "01 June 2026"

    print(f"\n🚀 Starting Backfill for: {target_date}")

    configs = [
        {
            "lang": "bn",
            "name": "Bengali",
            "wotd_url": f"{BASE_GITLAB}/WordOfTheDayEnToBn/{month_year}.json",
            "vocab_url": f"{BASE_GITLAB}/EnToBnWord/{target_date}.json"
        },
        {
            "lang": "hn",
            "name": "Hindi",
            "wotd_url": f"{BASE_GITLAB}/WordOfTheDayEnToHn/{month_year}.json",
            "vocab_url": f"{BASE_GITLAB}/EnToHnWord/{target_date}.json"
        }
    ]

    for cfg in configs:
        print(f"  --- Processing {cfg['name']} ---")
        wotd_data = fetch_json(cfg['wotd_url'])
        vocab_data = fetch_json(cfg['vocab_url'])

        if not wotd_data or not vocab_data:
            print(f"  ⚠️ Skipping {cfg['name']} due to missing data.")
            continue

        # Find the specific entry in the monthly WOTD list
        wotd_entry = next((item for item in wotd_data 
                           if item.get('date') in [search_date_std, search_date_pad]), None)
        vocab_list = vocab_data.get("wordMeaning", [])

        if wotd_entry:
            web_generator.generate_wotd_page(cfg['lang'], wotd_entry, vocab_list, target_date)
            web_generator.append_to_exam_archive(cfg['lang'], wotd_entry, target_date)
            print(f"  ✅ Successfully generated {cfg['name']} page.")
        else:
            print(f"  ❌ Word of the Day entry for {search_date_std} not found in {cfg['name']} monthly file.")

    # Refresh sitemap, words index, and .nojekyll
    web_generator.regenerate_static_pages()
    print(f"\n✨ Backfill complete for {target_date}. Static site indexes updated.")

if __name__ == "__main__":
    user_date = input("Enter the date you want to backfill (DD-MM-YYYY): ").strip()
    if user_date:
        backfill_date(user_date)