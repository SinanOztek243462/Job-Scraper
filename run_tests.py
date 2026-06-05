import os
import json
import sqlite3
from fpdf import FPDF
import pdfplumber

from scraper import scrape_linkedin_jobs
from nlp_extractor import SkillExtractor
from analyzer import analyze_skills, extract_experience
import database as db

# 1. Initialize clean database for tests (or just use existing)
db.init_db()

def create_mock_pdf(filename, text_content):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, txt=text_content)
    pdf.output(filename)

def run_scenario_1_frontend_db():
    print("\n--- TEST SCENARIO 1: Populating 'Frontend-TR' ---")
    query = "frontend OR react OR javascript"
    location = "Turkey"
    limit = 5  # Keep it small to avoid blocking during tests
    profile = "Frontend-TR"
    
    print(f"Scraping {limit} jobs for {query} in {location}...")
    raw_jobs = scrape_linkedin_jobs(query, location=location, limit=limit, seen_urls=set(), include_seen=True)
    
    extractor = SkillExtractor()
    saved_count = 0
    for job in raw_jobs:
        # Extractor
        skills = extractor.extract_skills(job['description'])
        job['extracted_skills'] = skills
        
        # Experience
        seniority, min_years = extract_experience(job['title'], job['description'])
        job['seniority_level'] = seniority
        job['experience_years'] = min_years
        
        # Save
        db.save_job(job, profile)
        saved_count += 1
        
    db_jobs = db.get_jobs_by_profile(profile)
    print(f"SUCCESS: {saved_count} jobs scraped. DB has {len(db_jobs)} jobs for {profile}.")
    if db_jobs:
        print(f"Sample Experience Data: {db_jobs[0]['title']} -> Seniority: {db_jobs[0]['seniority_level']}, Years: {db_jobs[0]['experience_years']}")

def run_scenario_2_data_db():
    print("\n--- TEST SCENARIO 2: Populating 'Data-US' ---")
    query = "data scientist OR machine learning"
    location = "United States"
    limit = 5
    profile = "Data-US"
    
    raw_jobs = scrape_linkedin_jobs(query, location=location, limit=limit, seen_urls=set(), include_seen=True)
    
    extractor = SkillExtractor()
    for job in raw_jobs:
        job['extracted_skills'] = extractor.extract_skills(job['description'])
        seniority, min_years = extract_experience(job['title'], job['description'])
        job['seniority_level'] = seniority
        job['experience_years'] = min_years
        db.save_job(job, profile)
        
    db_jobs = db.get_jobs_by_profile(profile)
    print(f"SUCCESS: DB has {len(db_jobs)} jobs for {profile}.")

def run_scenario_3_cv_match():
    print("\n--- TEST SCENARIO 3: CV Parsing & Matching ---")
    cv_text = "Experienced software engineer with 3 years of experience. Skilled in HTML, CSS, JavaScript, and React. Good at problem solving and Git."
    pdf_path = "test_frontend_cv.pdf"
    create_mock_pdf(pdf_path, cv_text)
    
    with pdfplumber.open(pdf_path) as pdf:
        extracted_text = " ".join([page.extract_text() for page in pdf.pages if page.extract_text()])
        
    extractor = SkillExtractor()
    cv_skills = extractor.extract_skills(extracted_text)
    print(f"CV Skills Extracted: {cv_skills}")
    
    # Match against Frontend-TR
    db_jobs = db.get_jobs_by_profile("Frontend-TR")
    if not db_jobs:
        print("FAIL: No jobs in Frontend-TR")
        return
        
    job_skills_list = [j['extracted_skills'] for j in db_jobs if j['extracted_skills']]
    freqs, co_occurrences = analyze_skills(job_skills_list)
    top_20 = [s for s, c in freqs.most_common(20)]
    
    cv_set = set(cv_skills)
    top_20_set = set(top_20)
    
    matched = cv_set.intersection(top_20_set)
    missing = top_20_set.difference(cv_set)
    
    print(f"Matched Skills (GREEN): {matched}")
    print(f"Missing Skills (RED): {missing}")
    
    # Recommendation logic test
    strongest_user_skills = sorted(list(matched), key=lambda x: freqs[x], reverse=True)
    if strongest_user_skills and missing:
        best_skill = strongest_user_skills[0]
        related = []
        for (s1, s2), co_count in co_occurrences.items():
            if s1 == best_skill: related.append((s2, co_count))
            elif s2 == best_skill: related.append((s1, co_count))
        related.sort(key=lambda x: x[1], reverse=True)
        for r_skill, r_count in related:
            if r_skill in missing:
                print(f"AI Recommendation: Because you have {best_skill}, you should learn {r_skill}!")
                break
                
def run_scenario_4_career_path():
    print("\n--- TEST SCENARIO 4: Career Path Cross-Matching ---")
    cv_text = "Data enthusiast skilled in Python, SQL, Pandas, and Machine Learning algorithms. Using Docker for deployment."
    pdf_path = "test_data_cv.pdf"
    create_mock_pdf(pdf_path, cv_text)
    
    with pdfplumber.open(pdf_path) as pdf:
        extracted_text = " ".join([page.extract_text() for page in pdf.pages if page.extract_text()])
        
    extractor = SkillExtractor()
    cv_skills = set(extractor.extract_skills(extracted_text))
    print(f"CV Skills: {cv_skills}")
    
    print("Pretending user selected 'Frontend-TR' as target...")
    all_profiles = db.get_all_profiles()
    
    for profile in all_profiles:
        other_jobs = db.get_jobs_by_profile(profile)
        other_skills_list = [j['extracted_skills'] for j in other_jobs if j['extracted_skills']]
        other_freqs, _ = analyze_skills(other_skills_list)
        other_top_20 = set([s for s, c in other_freqs.most_common(20)])
        
        if other_top_20:
            score = len(cv_skills.intersection(other_top_20)) / len(other_top_20) * 100
            print(f"Cross-Match Score for '{profile}': {score:.1f}%")

if __name__ == "__main__":
    run_scenario_1_frontend_db()
    run_scenario_2_data_db()
    run_scenario_3_cv_match()
    run_scenario_4_career_path()
