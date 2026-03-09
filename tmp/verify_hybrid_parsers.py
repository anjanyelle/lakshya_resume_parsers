import sys
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).resolve().parents[1] / "backend"))

from app.services.parser.work_experience_parser import WorkExperienceParser
from app.services.parser.education_parser import EducationParser
from app.services.parser.skill_extractor import SkillExtractor
from app.services.parser.contact_extractor import ContactExtractor

def test_hybrid_parsers():
    print("=== Testing Hybrid Parser Integration ===\n")

    try:
        # 1. Test Work Experience Parser
        print("--- Work Experience ---")
        work_parser = WorkExperienceParser()
        sample_work = """
        Software Engineer at Google
        Jan 2021 - Present
        - Developed backend services using Python and Go.
        - Optimized database queries for high performance.
        """
        work_entries = work_parser.parse_experience_section(sample_work)
        for entry in work_entries:
            print(f"Company: {entry.company}")
            print(f"Title: {entry.title}")
            print(f"Start: {entry.start_date}")
            print(f"End: {entry.end_date if entry.end_date else 'Present'}")
            print("-" * 10)
    except Exception as e:
        print(f"Error in Work Experience testing: {e}")

    try:
        # 2. Test Education Parser
        print("\n--- Education ---")
        edu_parser = EducationParser()
        print(f"NER Loaded: {edu_parser._ner_nlp is not None}")
        print(f"Degrees Dict Loaded: {edu_parser._degrees_processor is not None}")
        
        from app.data.taxonomy.universities_top import TOP_UNIVERSITIES
        print(f"TOP_UNIVERSITIES count: {len(TOP_UNIVERSITIES)}")
        print(f"'iit delhi' in TOP_UNIVERSITIES: {'iit delhi' in [u.lower() for u in TOP_UNIVERSITIES]}")
        
        sample_edu = """
        B.Tech in Computer Science
        IIT Delhi
        2018 - 2022
        GPA: 9.5/10
        """
        edu_entries = edu_parser.parse(sample_edu)
        for entry in edu_entries:
            print(f"University: {entry.institution}")
            print(f"Degree: {entry.degree}")
            print(f"Year: {entry.end_date.year if entry.end_date else 'N/A'}")
            print("-" * 10)
    except Exception as e:
        print(f"Error in Education testing: {e}")

    try:
        # 3. Test Skill Extraction
        print("\n--- Skills ---")
        from app.services.parser.skill_extractor import SkillExtractor
        skill_extractor = SkillExtractor()
        sample_skills = "Python, Java, React, Docker, Kubernetes, File Management, Device Installation"
        skills = skill_extractor.extract_from_raw_text(sample_skills)
        skill_names = [s.normalized_name for s in skills]
        print(f"Extracted Skills: {', '.join(skill_names)}")
    except Exception as e:
        print(f"Error in Skills testing: {e}")

    try:
        # 5. Test HybridParserService
        print("\n--- HybridParserService ---")
        from app.services.parser.hybrid_parser_service import HybridParserService
        service = HybridParserService()
        sample_sections = {
            "contact": "John Doe\njohn.doe@example.com",
            "work_experience": "Software Engineer at Google\nJan 2021 - Present\nDeveloped backend services using Python and SQL. Handled file management and device installation.",
            "education": "B.Tech in Computer Science\nIIT Delhi\n2018 - 2022",
            "skills": "Python, Java, React, Docker, Spreadsheet Formulas, Computer Programming"
        }
        full_result = service.parse_resume(sample_sections)
        import json
        print(json.dumps(full_result, indent=2))
    except Exception as e:
        print(f"Error in HybridParserService testing: {e}")

if __name__ == "__main__":
    test_hybrid_parsers()
