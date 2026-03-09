import logging
from typing import Any, Dict, List, Optional
from app.services.parser.work_experience_parser import WorkExperienceParser
from app.services.parser.education_parser import EducationParser
from app.services.parser.skill_extractor import SkillExtractor
from app.services.parser.contact_extractor import ContactExtractor

logger = logging.getLogger(__name__)

class HybridParserService:
    """
    Service that coordinates hybrid parsing (NER + Dictionary + Regex) 
    across different resume sections.
    """
    def __init__(self):
        self.work_parser = WorkExperienceParser()
        self.edu_parser = EducationParser()
        self.skill_extractor = SkillExtractor()
        self.contact_extractor = ContactExtractor()

    def parse_resume(self, sections: Dict[str, str]) -> Dict[str, Any]:
        """
        Parse resume sections into a structured JSON-compatible dictionary.
        
        Args:
            sections: Dictionary mapping section names (e.g., 'experience', 'education') to their raw text.
            
        Returns:
            Structured data including work experience, education, skills, and contact info.
        """
        results = {
            "name": None,
            "work_experience": [],
            "education": [],
            "skills": []
        }

        # 1. Contact Info (Name)
        contact_text = sections.get("contact") or sections.get("header")
        if contact_text:
            try:
                contact_result = self.contact_extractor.extract_all(contact_text)
                if contact_result and contact_result.name and contact_result.name.name:
                    # Isolate name if it's a multiline block
                    name = contact_result.name.name.split("\n")[0].strip()
                    results["name"] = name
            except Exception as e:
                logger.error(f"Error extracting name: {e}")

        # 2. Work Experience
        exp_text = sections.get("experience") or sections.get("work_experience") or sections.get("employment")
        if exp_text:
            try:
                jobs = self.work_parser.parse_experience_section(exp_text)
                results["work_experience"] = [
                    {
                        "company": job.company,
                        "title": job.title,
                        "location": job.location,
                        "start_date": job.start_date.isoformat() if job.start_date else None,
                        "end_date": job.end_date.isoformat() if job.end_date else None,
                        "is_current": job.is_current,
                        "description": job.description,
                    }
                    for job in jobs
                ]
            except Exception as e:
                logger.error(f"Error parsing work experience: {e}")

        # 3. Education
        edu_text = sections.get("education") or sections.get("academic")
        if edu_text:
            try:
                edu_entries = self.edu_parser.parse(edu_text)
                results["education"] = [
                    {
                        "university": entry.institution,
                        "degree": entry.degree,
                        "field_of_study": entry.field_of_study,
                        "start_date": entry.start_date.isoformat() if entry.start_date else None,
                        "end_date": entry.end_date.isoformat() if entry.end_date else None,
                        "gpa": entry.gpa,
                    }
                    for entry in edu_entries
                ]
            except Exception as e:
                logger.error(f"Error parsing education: {e}")

        # 4. Skills
        # Skills can be extracted from the specific skills section OR the whole document for better coverage.
        skills_text = sections.get("skills") or sections.get("technical_skills")
        all_text = "\n".join(sections.values())
        
        try:
            # We prefer extracting from raw text to catch skills mentioned in experience too
            matches = self.skill_extractor.extract_from_raw_text(all_text)
            # Deduplicate by normalized name
            seen = set()
            unique_skills = []
            for m in matches:
                if m.normalized_name not in seen:
                    unique_skills.append(m.normalized_name)
                    seen.add(m.normalized_name)
            results["skills"] = unique_skills
        except Exception as e:
            logger.error(f"Error extracting skills: {e}")

        return results
