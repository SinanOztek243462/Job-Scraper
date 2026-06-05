import requests
from bs4 import BeautifulSoup
import time
import random

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 Edg/115.0.1901.188"
]

def get_random_header():
    return {"User-Agent": random.choice(USER_AGENTS)}

def get_job_links(keywords, location="Worldwide", limit=20, seen_urls=None, include_seen=False, delay=2.0):
    if seen_urls is None:
        seen_urls = set()
        
    job_urls = []
    start = 0
    max_pages = 5  # Maximum number of pages to check
    
    url = "https://www.linkedin.com/jobs/search"
    
    while len(job_urls) < limit and start < max_pages * 25:
        params = {
            "keywords": keywords,
            "location": location,
            "start": start
        }
        
        # Exponential backoff retry
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = requests.get(url, params=params, headers=get_random_header(), timeout=15)
                if response.status_code == 200:
                    break
                elif response.status_code == 429:
                    sleep_time = (2 ** attempt) * delay
                    print(f"Rate limited (429). Waiting {sleep_time}s...")
                    time.sleep(sleep_time)
                else:
                    print(f"HTTP {response.status_code} received.")
                    break
            except requests.exceptions.RequestException as e:
                print(f"Network error on attempt {attempt+1}: {e}")
                time.sleep((2 ** attempt) * delay)
        else:
            print("Max retries exceeded for job links.")
            break
                
        if response.status_code != 200:
            print(f"Failed to fetch jobs: {response.status_code}")
            break
            
        soup = BeautifulSoup(response.text, 'html.parser')
        jobs = soup.find_all('div', class_='base-card')
        
        if not jobs:
            break
            
        for job in jobs:
            if len(job_urls) >= limit:
                break
                
            link_tag = job.find('a', class_='base-card__full-link')
            title_tag = job.find('h3', class_='base-search-card__title')
            company_tag = job.find('h4', class_='base-search-card__subtitle')
            loc_tag = job.find('span', class_='job-search-card__location')
            
            if link_tag and 'href' in link_tag.attrs:
                raw_url = link_tag['href']
                # Clean url parameters only if it looks like a standard view URL
                if "/jobs/view/" in raw_url:
                    job_url = raw_url.split('?')[0]
                else:
                    job_url = raw_url
                
                # Check history filter
                if not include_seen and job_url in seen_urls:
                    continue
                    
                title = title_tag.get_text(strip=True) if title_tag else "Bilinmeyen İlan"
                company = company_tag.get_text(strip=True) if company_tag else "Bilinmeyen Şirket"
                loc = loc_tag.get_text(strip=True) if loc_tag else "Bilinmeyen Konum"
                
                # Ensure we don't add duplicates in the current run
                if not any(u == job_url for t, c, l, u in job_urls):
                    job_urls.append((title, company, loc, job_url))
                    
        start += 25
        time.sleep(delay) # Polite wait between pages
            
    return job_urls

def get_job_description(url):
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=get_random_header(), timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                description_div = soup.find('div', class_='description__text')
                
                if description_div:
                    return description_div.get_text(separator=' ', strip=True)
                return ""
            elif response.status_code == 429:
                sleep_time = (2 ** attempt) * 2.0
                time.sleep(sleep_time)
            else:
                return ""
        except Exception as e:
            if attempt == max_retries - 1:
                print(f"Error fetching {url}: {e}")
            time.sleep(2.0)
    return ""

def scrape_linkedin_jobs(keywords="developer data", location="Worldwide", limit=20, seen_urls=None, include_seen=False, delay=2.0):
    print(f"Searching for {keywords} in {location}...")
    jobs_info = get_job_links(keywords, location=location, limit=limit, seen_urls=seen_urls, include_seen=include_seen, delay=delay)
    valid_jobs = []
    
    for i, (title, company, loc, url) in enumerate(jobs_info):
        print(f"Fetching {i+1}/{len(jobs_info)}: {url}")
        desc = get_job_description(url)
        if desc:
            valid_jobs.append({
                'title': title,
                'company': company,
                'location': loc,
                'url': url,
                'description': desc
            })
        time.sleep(delay) # Polite scraping to avoid blocks
        
    return valid_jobs
