import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from scraper import scrape_linkedin_jobs

print("Testing exact quotes...")
jobs = scrape_linkedin_jobs(keywords='"Kimya Mühendisi"', location='Turkey', limit=5)
print([j['title'] for j in jobs])
