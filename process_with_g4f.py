import database as db
import json
import time
from g4f.client import Client

client = Client()

def extract_skills_g4f(text):
    prompt = f"""You are an expert technical recruiter AI. Extract the required skills, tools, and programming languages from the following job description.

Analyze the text and extract ONLY:
- Hard skills (e.g. Python, SQL, AWS, AutoCAD, GMP)
- Programming languages (e.g. Java, C++)
- Frameworks and libraries (e.g. React, Spring)
- Tools and platforms (e.g. Docker, Git, Jira)

Do NOT extract:
- Soft skills (e.g. communication, teamwork, leadership)
- Languages spoken (e.g. English, Turkish)
- General qualifications (e.g. Bachelor's degree, 3 years experience)

Provide your response ONLY as a valid JSON object with the following structure:
{{
    "skills": ["Skill1", "Skill2", "Skill3"],
    "qualifications_text": "A brief summary of the key requirements (max 3 sentences)"
}}

Job Description:
{text[:2000]}
"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
        )
        content = response.choices[0].message.content.strip()
        
        # Clean markdown
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
            
        parsed = json.loads(content.strip())
        if isinstance(parsed, dict) and "skills" in parsed:
            return parsed
    except Exception as e:
        print(f"Error extracting: {e}")
    return None

import sqlite3
conn = sqlite3.connect('jobs.db')
c = conn.cursor()
c.execute('SELECT * FROM jobs')
columns = [column[0] for column in c.description]
jobs = [dict(zip(columns, row)) for row in c.fetchall()]
for j in jobs:
    if j.get("extracted_skills") and isinstance(j["extracted_skills"], str) and j["extracted_skills"].strip():
        try:
            j["extracted_skills"] = json.loads(j["extracted_skills"])
        except:
            j["extracted_skills"] = []
    else:
        j["extracted_skills"] = []
unprocessed = [j for j in jobs if not j.get('extracted_skills')]

print(f"Toplam islenmemis ilan: {len(unprocessed)}")

for i, job in enumerate(unprocessed):
    print(f"[{i+1}/{len(unprocessed)}] Isleniyor: {job['title']}...", end=" ")
    
    desc = job.get('description', '')
    if not desc:
        print("Atlandi (Aciklama yok)")
        continue
        
    result = extract_skills_g4f(desc)
    
    if result and "skills" in result:
        job["extracted_skills"] = list(set(result["skills"]))
        job["qualifications_text"] = result.get("qualifications_text", "")
        db.save_job(job, job['profile_name'])
        print(f"BASARILI ({len(result['skills'])} yetenek)")
    else:
        print("BASARISIZ")
    
    time.sleep(2) # Kisa bir bekleme (spam algilanmamasi icin)

print("ISLEM TAMAMLANDI!")
