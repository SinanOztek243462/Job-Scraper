import scraper
import time

def run_scraper_test():
    print("--- 1. Testing get_job_links (Network robustness) ---")
    start_time = time.time()
    # Query something niche to get a small number of results, limiting to 5
    links = scraper.get_job_links(keywords="python django rest", location="Turkey", limit=5, delay=1.0)
    elapsed = time.time() - start_time
    print(f"Fetched {len(links)} links in {elapsed:.2f}s.")
    
    if len(links) > 0:
        print("\n--- 2. Testing get_job_description (Single Detail) ---")
        title, company, loc, url = links[0]
        print(f"Testing URL: {url}")
        desc = scraper.get_job_description(url)
        print(f"Extracted description length: {len(desc)} characters")
        assert len(desc) > 0, "Description should not be empty if the job is valid."
    else:
        print("No links found for the test query. Skipping description test.")

    print("\n--- 3. Testing scrape_linkedin_jobs (Full Flow) ---")
    jobs = scraper.scrape_linkedin_jobs(keywords="data junior", location="Europe", limit=2, delay=1.0)
    print(f"Full flow returned {len(jobs)} jobs.")
    for j in jobs:
        print(f"- {j['title']} at {j['company']} ({j['location']})")

if __name__ == "__main__":
    run_scraper_test()
