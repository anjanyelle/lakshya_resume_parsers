#!/usr/bin/env python3
"""
Integration of existing comprehensive parsers with Enhanced JSON format
"""

import sys
sys.path.append('app')

from datetime import datetime
from typing import Dict, List, Any

class IntegratedResumeParser:
    """Uses existing comprehensive parsers but outputs Enhanced JSON format"""
    
    def __init__(self):
        print("🔧 Integrated Resume Parser - Using Existing Comprehensive System")
        
    def parse_resume_complete(self, resume_text: str, use_ml: bool = True) -> Dict[str, Any]:
        """Parse resume using existing parsers but return Enhanced JSON format"""
        
        # Import existing parsers
        try:
            from app.services.parser.work_experience_parser import WorkExperienceParser
            from app.services.parser.education_parser import EducationParser  
            from app.services.parser.skill_extractor import SkillExtractor
            from app.services.parser.certification_parser import CertificationParser
            from app.services.parser.contact_extractor import ContactExtractor
            
            print("✅ All existing parsers loaded successfully")
            
        except ImportError as e:
            print(f"❌ Import error: {e}")
            return self._fallback_json(resume_text)
        
        # Initialize parsers
        work_parser = WorkExperienceParser()
        edu_parser = EducationParser()
        skill_extractor = SkillExtractor()
        cert_parser = CertificationParser()
        contact_extractor = ContactExtractor()
        
        # Parse using existing comprehensive system
        print("🔍 Parsing with existing comprehensive system...")
        
        # Work Experience
        work_entries_raw = work_parser.parse_experience_section(resume_text)
        work_entries = self._convert_work_to_enhanced(work_entries_raw)
        
        # Education  
        education_entries_raw = edu_parser.parse_education_section(resume_text)
        education_entries = self._convert_education_to_enhanced(education_entries_raw)
        
        # Skills
        skills_raw = skill_extractor.extract_skills(resume_text)
        skills_entries = self._convert_skills_to_enhanced(skills_raw)
        
        # Certifications
        cert_raw = cert_parser.parse_certifications(resume_text)
        cert_entries = self._convert_certifications_to_enhanced(cert_raw)
        
        # Contact/Basic Info
        contact_raw = contact_extractor.extract_contact(resume_text)
        basics = self._convert_contact_to_enhanced(contact_raw)
        
        # Return Enhanced JSON format
        return {
            "basics": basics,
            "work": work_entries,
            "education": education_entries,
            "skills": skills_entries,
            "certifications": cert_entries,
            "projects": [],
            "achievements": [],
            "volunteer": [],
            "publications": [],
            "languages": [],
            "references": [],
            "texts": {
                "additional_text": resume_text
            }
        }
    
    def _convert_work_to_enhanced(self, work_entries_raw) -> List[Dict[str, Any]]:
        """Convert JobEntry objects to Enhanced JSON format"""
        enhanced_work = []
        
        for entry in work_entries_raw:
            if hasattr(entry, 'company') and entry.company:
                # Create date_range from start_date/end_date
                date_range = ""
                if hasattr(entry, 'start_date') and entry.start_date:
                    start_str = entry.start_date.strftime("%B %Y") if entry.start_date else ""
                    end_str = "Current" if (hasattr(entry, 'is_current') and entry.is_current) else ""
                    if hasattr(entry, 'end_date') and entry.end_date:
                        end_str = entry.end_date.strftime("%B %Y")
                    date_range = f"{start_str} - {end_str}" if start_str and end_str else start_str
                
                # Create description from bullets and description
                description = ""
                if hasattr(entry, 'description') and entry.description:
                    description = entry.description
                if hasattr(entry, 'bullets') and entry.bullets:
                    bullet_text = " ".join([f"• {bullet}" for bullet in entry.bullets])
                    description = f"{description} {bullet_text}".strip()
                
                enhanced_work.append({
                    "title": getattr(entry, 'title', '') or '',
                    "company": getattr(entry, 'company', '') or '',
                    "date_range": date_range,
                    "location": getattr(entry, 'location', '') or '',
                    "description": description
                })
        
        return enhanced_work
    
    def _convert_education_to_enhanced(self, education_entries_raw) -> List[Dict[str, Any]]:
        """Convert education objects to Enhanced JSON format"""
        enhanced_edu = []
        
        for entry in education_entries_raw:
            if hasattr(entry, 'institution') and entry.institution:
                enhanced_edu.append({
                    "degree": getattr(entry, 'degree', '') or '',
                    "university": getattr(entry, 'institution', '') or '',
                    "location": getattr(entry, 'location', '') or '',
                    "date": getattr(entry, 'graduation_year', '') or '',
                    "confidence": getattr(entry, 'confidence', 0.8)
                })
        
        return enhanced_edu
    
    def _convert_skills_to_enhanced(self, skills_raw) -> List[Dict[str, Any]]:
        """Convert skills to Enhanced JSON format"""
        enhanced_skills = []
        
        if isinstance(skills_raw, list):
            for skill in skills_raw:
                if isinstance(skill, dict):
                    enhanced_skills.append({
                        "skill": skill.get('name', skill.get('skill', '')),
                        "proficiency": skill.get('proficiency', 'Intermediate'),
                        "confidence": skill.get('confidence', 0.8)
                    })
                elif isinstance(skill, str):
                    enhanced_skills.append({
                        "skill": skill,
                        "proficiency": "Intermediate", 
                        "confidence": 0.8
                    })
        
        return enhanced_skills
    
    def _convert_certifications_to_enhanced(self, cert_raw) -> List[Dict[str, Any]]:
        """Convert certifications to Enhanced JSON format"""
        enhanced_certs = []
        
        if isinstance(cert_raw, list):
            for cert in cert_raw:
                if hasattr(cert, 'name') and cert.name:
                    enhanced_certs.append({
                        "name": getattr(cert, 'name', ''),
                        "issuer": getattr(cert, 'issuer', ''),
                        "date": getattr(cert, 'date', ''),
                        "credentialId": getattr(cert, 'credential_id', ''),
                        "confidence": getattr(cert, 'confidence', 0.8)
                    })
        
        return enhanced_certs
    
    def _convert_contact_to_enhanced(self, contact_raw) -> Dict[str, Any]:
        """Convert contact to Enhanced JSON format"""
        basics = {
            "name": "",
            "email": "",
            "phone": "",
            "location": ""
        }
        
        if hasattr(contact_raw, 'name') and contact_raw.name:
            basics["name"] = contact_raw.name
        if hasattr(contact_raw, 'email') and contact_raw.email:
            basics["email"] = contact_raw.email
        if hasattr(contact_raw, 'phone') and contact_raw.phone:
            basics["phone"] = contact_raw.phone
        if hasattr(contact_raw, 'location') and contact_raw.location:
            basics["location"] = contact_raw.location
            
        return basics
    
    def _fallback_json(self, resume_text: str) -> Dict[str, Any]:
        """Fallback if parsers fail to load"""
        return {
            "basics": {"name": "", "email": "", "phone": "", "location": ""},
            "work": [],
            "education": [],
            "skills": [],
            "certifications": [],
            "projects": [],
            "achievements": [],
            "volunteer": [],
            "publications": [],
            "languages": [],
            "references": [],
            "texts": {"additional_text": resume_text}
        }

if __name__ == "__main__":
    # Test the integrated parser
    parser = IntegratedResumeParser()
    
    # Test with Arjun's resume
    test_resume = """
ARJUN KRISHNAMURTHY
Senior Java Developer
LinkedIn: www.linkedin.com/in/arjun-krishnamurthy  |  Phone: +1 (512)-867-3090  |  arjun.krishnamurthy@gmail.com  |  Austin, TX
PROFESSIONAL EXPERIENCE
Aetna (CVS Health): September 2023 – Current (Location: Hartford, CT (Remote))
Role: Senior Java Developer
Responsibilities:
•	Architected and developed HIPAA-compliant Spring Boot microservices...
"""
    
    result = parser.parse_resume_complete(test_resume)
    print(f"✅ Integrated parser result:")
    print(f"📊 Work entries: {len(result['work'])}")
    print(f"🎓 Education entries: {len(result['education'])}")
    print(f"🔧 Skills entries: {len(result['skills'])}")
    print(f"🏆 Certifications: {len(result['certifications'])}")
