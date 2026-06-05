import spacy
from spacy.matcher import PhraseMatcher
import streamlit as st

# Categorized technical skills
SKILL_CATEGORIES = {
    "Yazılım Dilleri": ["python", "java", "javascript", "c++", "c#", "go", "rust", "ruby", "typescript", "r", "scala", "kotlin", "swift"],
    "Veritabanı & Veri Depolama": ["sql", "nosql", "mongodb", "postgresql", "mysql", "oracle", "redis", "elasticsearch", "snowflake", "bigquery", "redshift"],
    "Bulut & DevOps": ["docker", "kubernetes", "aws", "azure", "gcp", "google cloud", "ci/cd", "jenkins", "gitlab", "github actions", "linux", "bash", "shell", "terraform", "ansible", "git"],
    "Veri & Yapay Zeka": ["machine learning", "deep learning", "ai", "nlp", "data science", "data engineering", "spark", "hadoop", "kafka", "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch"],
    "Web & Çatı (Framework)": ["react", "node.js", "vue", "angular", "django", "flask", "spring", "spring boot", "html", "css", "flutter", "react native", "graphql", "rest api", "soap", "microservices", "fastapi"],
    "Veri Görselleştirme": ["tableau", "power bi", "looker", "excel", "d3.js", "chart.js"]
}

# Flatten the categories for the matcher
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

class SkillExtractor:
    def __init__(self):
        self.nlp = get_nlp_model()
        self.matcher = PhraseMatcher(self.nlp.vocab, attr="LOWER")
        patterns = [self.nlp.make_doc(text) for text in TECH_SKILLS]
        self.matcher.add("SKILLS", patterns)

    def extract_skills(self, text):
        doc = self.nlp(text)
        matches = self.matcher(doc)
        
        found_skills = set()
        for match_id, start, end in matches:
            span = doc[start:end]
            found_skills.add(span.text.lower())
            
        return list(found_skills)

if __name__ == "__main__":
    extractor = SkillExtractor()
    sample_text = "We are looking for a Data Engineer with experience in Python, AWS, Docker, and Kubernetes. Strong SQL skills are required."
    print(f"Extracted skills: {extractor.extract_skills(sample_text)}")
    for s in extractor.extract_skills(sample_text):
        print(f"{s} -> {get_category_for_skill(s)}")
