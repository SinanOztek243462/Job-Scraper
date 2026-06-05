import sys
import os

# Ensure we can import from the project
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from scraper import scrape_linkedin_jobs
from utils.scrape_runner import build_query_string
from utils.scrape_runner import run_scrape_for_profile
import database as db

db.init_db()
print("Running scrape for kimyabahar profile...")
saved = run_scrape_for_profile("kimyabahar", show_ui=False)
print(f"Jobs saved: {saved}")
