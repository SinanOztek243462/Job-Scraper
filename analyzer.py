from collections import Counter
import itertools
from nlp_extractor import get_category_for_skill
import re

def analyze_skills(job_skills_list):
    """
    Analyzes a list of skill lists (one list per job).
    Returns frequencies and co-occurrences.
    """
    # Calculate frequencies
    all_skills = list(itertools.chain.from_iterable(job_skills_list))
    frequencies = Counter(all_skills)
    
    # Calculate co-occurrences
    co_occurrences = Counter()
    for skills in job_skills_list:
        # Sort to ensure (A, B) is treated same as (B, A)
        sorted_skills = sorted(skills)
        for pair in itertools.combinations(sorted_skills, 2):
            co_occurrences[pair] += 1
            
    return frequencies, co_occurrences

def analyze_categories(freqs):
    """
    Groups skills by category and returns their total frequencies.
    """
    cat_freq = Counter()
    for skill, count in freqs.items():
        cat = get_category_for_skill(skill)
        cat_freq[cat] += count
    return cat_freq

def extract_experience(title, description):
    """
    Extracts seniority level from title and minimum experience years from description.
    """
    # 1. Seniority Level from Title
    title_lower = title.lower()
    seniority = "Mid-Level" # Default
    
    junior_keywords = ['intern', 'trainee', 'new grad', 'junior', 'jr', 'stajyer', 'yeni mezun', 'entry level', 'student']
    senior_keywords = ['senior', 'sr', 'lead', 'principal', 'staff', 'manager', 'uzman', 'kıdemli', 'architect']
    
    if any(k in title_lower for k in junior_keywords):
        seniority = "Junior"
    elif any(k in title_lower for k in senior_keywords):
        seniority = "Senior"
        
    # 2. Experience Years from Text
    desc_lower = description.lower()
    min_years = None
    
    patterns = [
        r'(\d+)\+?\s*(?:years?|yrs?|y/o)\s*(?:of)?\s*.{0,30}experience',
        r'minimum\s*(?:of)?\s*(\d+)\s*years?(?:\s*of\s*.{0,30}experience)?',
        r'(\d+)\s*-\s*\d+\s*years?\s*(?:of)?\s*.{0,30}experience',
        r'en\s*az\s*(\d+)\s*yıl\s*(?:deneyim|tecrübe)',
        r'(\d+)\+?\s*yıl\s*(?:deneyim|tecrübe)',
        r'minimum\s*(\d+)\s*yıllık\s*(?:deneyim|tecrübe)'
    ]
    
    found_years = []
    for pattern in patterns:
        matches = re.findall(pattern, desc_lower)
        for match in matches:
            try:
                num = int(match)
                if 0 <= num <= 20: # Sanity check
                    found_years.append(num)
            except ValueError:
                pass
                
    if found_years:
        min_years = max(found_years)
        
    return seniority, min_years
