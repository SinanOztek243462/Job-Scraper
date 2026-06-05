import spacy
from spacy.matcher import PhraseMatcher
import streamlit as st
import json
import database as db

def get_category_for_skill(skill):
    # Fallback function if DB is empty and LLM is off. 
    # Just return "Diğer" instead of forcing into IT categories.
    return "Diğer"

@st.cache_resource
def get_nlp_model():
    return spacy.load("en_core_web_sm")

import time

def extract_with_llm(text, provider, api_key, model_name):
    prompt = f"""You are an expert technical recruiter and HR data analyst.
Analyze the following job description. Your task is to locate the exact sections that list candidate requirements (look for headers like "GENEL NİTELİKLER VE İŞ TANIMI", "Pozisyona başvuran adayda olması beklenen özellikler", "Qualifications", "What We Look For?", "Minimum Requirements", "Senden Neler Bekliyoruz?", "Requirements").

1. Extract the raw text block of these requirements for training purposes.
2. Extract the specific hard technical skills/tools from this text.

RULES:
- DO NOT extract technologies mentioned merely as part of the company description.
- DO NOT include soft skills (e.g. "communication", "leadership").
- Output the final result strictly as a raw JSON object with two keys: "skills" (list of strings) and "qualifications_text" (string containing the exact raw text block).
- DO NOT add markdown formatting, code blocks, or any other explanations.

Example Valid Output:
{{
  "skills": ["AutoCAD", "SAP", "B2B Sales", "SEO"],
  "qualifications_text": "Üniversitelerin ilgili bölümlerinden mezun, B2B Sales deneyimi olan, AutoCAD ve SAP programlarına hakim..."
}}

Job Description:
{text}
"""
    # API isteğini 429 hatalarına karşı tekrar deneyen (retry) döngü
    max_retries = 3
    for attempt in range(max_retries):
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
            if isinstance(parsed, dict) and "skills" in parsed and "qualifications_text" in parsed:
                parsed["skills"] = [str(item).lower() for item in parsed["skills"]]
                return parsed
            elif isinstance(parsed, list):
                return {"skills": [str(item).lower() for item in parsed], "qualifications_text": ""}
            return None
            
        except Exception as api_err:
            err_str = str(api_err).lower()
            if "429" in err_str or "exhausted" in err_str or "quota" in err_str:
                if attempt < max_retries - 1:
                    import time
                    print(f"API Quota hit (429). Waiting 65 seconds before retry {attempt+1}/{max_retries}...")
                    time.sleep(65) # Free tier is 15 RPM. Wait >60s to reset quota.
                    continue
            print(f"LLM Extraction Error ({provider}): {api_err}")
            return None

def categorize_skills_bulk(skills: list) -> dict:
    """Takes a list of unknown skills, asks LLM to categorize them, and saves to DB."""
    if not skills:
        return {}
        
    api_settings = db.get_api_settings()
    provider = api_settings.get("provider", "spacy")
    api_key = api_settings.get("api_key", "")
    model_name = api_settings.get("model_name", "")
    
    if provider == "spacy" or (provider != "ollama" and not api_key):
        # Fallback if no LLM
        result = {}
        for s in skills:
            cat = get_category_for_skill(s)
            result[s] = cat
            db.save_skill_category(s, cat)
        return result

    prompt = f"""You are an expert HR data analyst. Group the following technical skills into dynamic, logical, profession-appropriate categories based on the actual skills provided.

Do NOT force them into software/IT categories if they are not software skills. For example, if you see chemistry or manufacturing skills, create categories like "Laboratuvar & Kimya", "Kalite & Standartlar", "Üretim", etc. If you see business skills, create "Satış & Pazarlama", "Finans", etc. Create at most 6 distinct categories.

Output ONLY a raw JSON dictionary mapping each skill to its category string. Do NOT add markdown, code blocks, or explanations.
Example Output:
{{"python": "Yazılım Dilleri", "autocad": "Tasarım & Çizim", "gmp": "Kalite & Yönetim", "hplc": "Laboratuvar"}}

Skills to categorize:
{json.dumps(skills)}
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
            raise ValueError("Invalid provider")

        content = content.strip()
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
            
        parsed = json.loads(content.strip())
        result = {}
        for k, v in parsed.items():
            result[k.lower()] = v
            db.save_skill_category(k.lower(), v)
            
        # Any missing skills default to Diğer
        for s in skills:
            if s.lower() not in result:
                result[s.lower()] = "Diğer"
                db.save_skill_category(s.lower(), "Diğer")
                
        return result
    except Exception as e:
        print(f"LLM Categorization Error: {e}")
        result = {}
        for s in skills:
            cat = get_category_for_skill(s)
            result[s] = cat
            db.save_skill_category(s, cat)
        return result


class SkillExtractor:
    def __init__(self):
        # Sadece basit NLP işlemleri (gerekirse diye) tutuluyor.
        # Artık Spacy PhraseMatcher (sabit kelime listesi) kullanmıyoruz.
        self.nlp = get_nlp_model()

    def extract_skills(self, text):
        api_settings = db.get_api_settings()
        provider = api_settings.get("provider", "spacy")
        
        if provider != "spacy":
            api_key = api_settings.get("api_key", "")
            model_name = api_settings.get("model_name", "")
            if provider == "ollama" or api_key:
                llm_result = extract_with_llm(text, provider, api_key, model_name)
                if llm_result is not None:
                    # Return dict directly
                    llm_result["skills"] = list(set(llm_result.get("skills", [])))
                    return llm_result

        # Yapay Zeka kapalıysa veya hata verirse, sisteme zorla IT kelimeleri
        # enjekte etmemek için boş dönüyoruz.
        return {"skills": [], "qualifications_text": ""}

if __name__ == "__main__":
    extractor = SkillExtractor()
    sample_text = "We are looking for a Chemical Engineer with experience in AutoCAD, ISO 9001, and GMP."
    print(f"Extracted skills: {extractor.extract_skills(sample_text)}")

