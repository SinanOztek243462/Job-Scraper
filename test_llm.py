import database as db
from nlp_extractor import SkillExtractor

def main():
    settings = db.get_api_settings()
    print("API Settings:", settings)
    
    extractor = SkillExtractor()
    sample_text = """
    We are looking for a Chemical Engineer.
    Requirements:
    - Bachelor's degree in Chemical Engineering
    - 3+ years of experience with GMP and ISO 9001
    - Knowledge of AutoCAD and SolidWorks
    - Experience with HPLC and lab equipment
    - Strong communication and leadership skills
    """
    
    print("\nExtracting skills...")
    skills = extractor.extract_skills(sample_text)
    print("Extracted Skills:", skills)

if __name__ == "__main__":
    main()
