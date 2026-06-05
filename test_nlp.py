import time
from analyzer import extract_experience
from nlp_extractor import SkillExtractor

def run_nlp_test():
    print("--- 1. Testing NLP Extractor Initialization ---")
    start = time.time()
    extractor = SkillExtractor()
    print(f"OK: SkillExtractor initialized in {time.time()-start:.2f}s")

    print("\n--- 2. Testing NLP Skill Extraction ---")
    dummy_text = """
    We are looking for a backend developer with 3+ years of experience in Python and Django.
    You should be familiar with SQL databases like PostgreSQL or MySQL.
    Knowledge of Docker and Kubernetes is a big plus. Experience with AWS is required.
    """
    start = time.time()
    skills = extractor.extract_skills(dummy_text)
    print(f"Extracted {len(skills)} skills in {time.time()-start:.2f}s: {skills}")
    assert "python" in skills, "Failed to extract Python"
    assert "django" in skills, "Failed to extract Django"
    assert "sql" in skills, "Failed to extract SQL"

    print("\n--- 3. Testing Analyzer (Experience Level) ---")
    title = "Senior Data Engineer"
    desc = "Must have 5 years of data engineering experience."
    seniority, years = extract_experience(title, desc)
    print(f"Title: {title} -> Seniority: {seniority}, Min Years: {years}")
    assert seniority == "Senior", "Seniority extraction failed"
    assert years == 5, "Years extraction failed"

    title2 = "Junior Web Developer"
    desc2 = "1-2 years of experience required."
    seniority2, years2 = extract_experience(title2, desc2)
    print(f"Title: {title2} -> Seniority: {seniority2}, Min Years: {years2}")
    assert seniority2 == "Junior", "Seniority extraction failed"
    
    print("\nOK: All NLP and Analyzer tests passed.")

if __name__ == "__main__":
    run_nlp_test()
