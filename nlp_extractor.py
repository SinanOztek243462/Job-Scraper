import spacy
from spacy.matcher import PhraseMatcher
import streamlit as st
import json
import database as db

# Legacy Fallback Categories for Spacy
SKILL_CATEGORIES = {
    "Yazılım Dilleri": ["python", "java", "javascript", "c++", "c#", "go", "rust", "ruby", "typescript", "r", "scala", "kotlin", "swift"],
    "Veritabanı & Veri Depolama": ["sql", "nosql", "mongodb", "postgresql", "mysql", "oracle", "redis", "elasticsearch", "snowflake", "bigquery", "redshift"],
    "Bulut & DevOps": ["docker", "kubernetes", "aws", "azure", "gcp", "google cloud", "ci/cd", "jenkins", "gitlab", "github actions", "linux", "bash", "shell", "terraform", "ansible", "git"],
    "Veri & Yapay Zeka": ["machine learning", "deep learning", "ai", "nlp", "data science", "data engineering", "spark", "hadoop", "kafka", "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch"],
    "Web & Çatı (Framework)": ["react", "node.js", "vue", "angular", "django", "flask", "spring", "spring boot", "html", "css", "flutter", "react native", "graphql", "rest api", "soap", "microservices", "fastapi"],
    "Veri Görselleştirme": ["tableau", "power bi", "looker", "excel", "d3.js", "chart.js"]
}

TECH_SKILLS = []
for skills in SKILL_CATEGORIES.values():
    TECH_SKILLS.extend(skills)

def get_category_for_skill(skill):
    for category, skills in SKILL_CATEGORIES.items():
        if skill.lower() in skills:
            return category
    return "Diğer"

@st.cache_resource
def get_nlp_model():
    return spacy.load("en_core_web_sm")

def extract_with_llm(text, provider, api_key, model_name):
    prompt = f"""You are a professional technical recruiter. Read the following job description and extract ONLY the technical skills, tools, and methodologies required or mentioned. Do not include soft skills like "communication" or "leadership".
Output the result ONLY as a JSON list of strings, with no other text, markdown formatting, or explanation.
Example Output: ["Python", "AWS", "SQL", "AutoCAD", "GMP", "ISO 9001"]

Job Description:
{text}
"""
    try:
        if provider == "ollama":
            from openai import OpenAI
            client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
            model = model_name if model_name else "llama3"
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0
            )
            content = response.choices[0].message.content
        elif provider == "openai":
            from openai import OpenAI
            client = OpenAI(api_key=api_key)
            model = model_name if model_name else "gpt-3.5-turbo"
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0
            )
            content = response.choices[0].message.content
        elif provider == "google-genai":
            from google import genai
            client = genai.Client(api_key=api_key)
            model = model_name if model_name else "gemini-2.5-flash"
            response = client.models.generate_content(
                model=model,
                contents=prompt,
            )
            content = response.text
        else:
            return None

        # Try to parse JSON from the LLM output
        content = content.strip()
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        
        parsed = json.loads(content.strip())
        if isinstance(parsed, list):
            return [str(item).lower() for item in parsed]
        return None
    except Exception as e:
        print(f"LLM Extraction Error ({provider}): {e}")
        return None

class SkillExtractor:
    def __init__(self):
        # Spacy fallback init
        self.nlp = get_nlp_model()
        self.matcher = PhraseMatcher(self.nlp.vocab, attr="LOWER")
        patterns = [self.nlp.make_doc(text) for text in TECH_SKILLS]
        self.matcher.add("SKILLS", patterns)

    def extract_skills(self, text):
        api_settings = db.get_api_settings()
        provider = api_settings.get("provider", "spacy")
        
        if provider != "spacy":
            api_key = api_settings.get("api_key", "")
            model_name = api_settings.get("model_name", "")
            if provider == "ollama" or api_key:
                llm_skills = extract_with_llm(text, provider, api_key, model_name)
                if llm_skills is not None:
                    return list(set(llm_skills))

        # Fallback to Spacy
        doc = self.nlp(text)
        matches = self.matcher(doc)
        
        found_skills = set()
        for match_id, start, end in matches:
            span = doc[start:end]
            found_skills.add(span.text.lower())
            
        return list(found_skills)

if __name__ == "__main__":
    extractor = SkillExtractor()
    sample_text = "We are looking for a Chemical Engineer with experience in AutoCAD, ISO 9001, and GMP."
    print(f"Extracted skills: {extractor.extract_skills(sample_text)}")

