#!/usr/bin/env python3

import json
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app.services.enhanced_pipeline_final import EnhancedResumePipelineFinal

def map_parser_to_frontend_format(parser_output: dict) -> dict:
    """
    Map our enhanced parser output to frontend expected format
    """
    
    frontend_format = {
        "candidate": {
            "full_name": parser_output.get("basics", {}).get("name", "").replace("## ", "").strip(),
            "email": parser_output.get("basics", {}).get("email", ""),
            "phone": parser_output.get("basics", {}).get("phone", ""),
            "ssn": None,
            "location": parser_output.get("basics", {}).get("location", ""),
            "linkedin_url": parser_output.get("basics", {}).get("urls", {}).get("linkedin", ""),
            "github_url": parser_output.get("basics", {}).get("urls", {}).get("github", ""),
            "summary": parser_output.get("summary", {}).get("content", ""),
            "years_experience": None,
            "years_experience_confidence": None,
            "current_title": None,
            "current_company": None,
            "status": "success",
            "consent_given": False,
            "consent_date": None,
            "id": parser_output.get("metadata", {}).get("parsing_timestamp", ""),
            "created_at": parser_output.get("metadata", {}).get("parsing_timestamp", ""),
            "updated_at": parser_output.get("metadata", {}).get("parsing_timestamp", ""),
            "review_status": "pending",
            "review_assigned_to": None,
            "review_notes": None,
            "review_confidence": None,
            "work_history": [],
            "education": [],
            "skills": [],
            "candidate_skills": []
        }
    }
    
    # Map work experience
    work_history = []
    for work in parser_output.get("work", []):
        frontend_work = {
            "company": work.get("company", ""),
            "title": work.get("title", ""),
            "location": work.get("location", ""),
            "start_date": work.get("start_date", ""),
            "end_date": work.get("end_date", ""),
            "is_current": work.get("is_current", False),
            "description": work.get("description", ""),
            "bullet_points": work.get("bullet_points", [])
        }
        work_history.append(frontend_work)
    
    frontend_format["candidate"]["work_history"] = work_history
    
    # Map education
    education_list = []
    for edu in parser_output.get("education", []):
        frontend_edu = {
            "institution": edu.get("institution", ""),
            "degree": edu.get("degree", ""),
            "field_of_study": edu.get("field", ""),
            "start_date": edu.get("start_date", ""),
            "end_date": edu.get("end_date", ""),
            "gpa": edu.get("gpa", ""),
            "description": edu.get("description", ""),
            "id": str(edu.get("confidence", 0.7)).replace(".", "")
        }
        education_list.append(frontend_edu)
    
    frontend_format["candidate"]["education"] = education_list
    
    # Map skills
    skills_list = []
    for skill in parser_output.get("skills", []):
        frontend_skill = {
            "skill": {
                "name": skill.get("name", ""),
                "category": skill.get("category", ""),
                "normalized_name": skill.get("name", "").lower().replace(" ", ""),
                "source": None,
                "id": str(skill.get("confidence", 0.85)).replace(".", "")
            },
            "proficiency_level": None,
            "years_experience": None
        }
        skills_list.append(frontend_skill)
    
    frontend_format["candidate"]["skills"] = skills_list
    
    # Map candidate_skills (duplicate of skills for frontend)
    candidate_skills = []
    for skill in parser_output.get("skills", []):
        candidate_skill = {
            "skill_id": str(skill.get("confidence", 0.85)).replace(".", ""),
            "proficiency_level": None,
            "years_experience": None,
            "skill": {
                "name": skill.get("name", ""),
                "category": skill.get("category", ""),
                "normalized_name": skill.get("name", "").lower().replace(" ", ""),
                "source": None,
                "id": str(skill.get("confidence", 0.85)).replace(".", "")
            }
        }
        candidate_skills.append(candidate_skill)
    
    frontend_format["candidate"]["candidate_skills"] = candidate_skills
    
    # Add metadata from parser
    if "metadata" in parser_output:
        frontend_format["candidate"]["id"] = parser_output["metadata"].get("parsing_timestamp", "")
        frontend_format["candidate"]["created_at"] = parser_output["metadata"].get("parsing_timestamp", "")
        frontend_format["candidate"]["updated_at"] = parser_output["metadata"].get("parsing_timestamp", "")
        frontend_format["candidate"]["confidence_score"] = parser_output["metadata"].get("parsing_confidence", 0)
    
    return frontend_format

def test_mapping():
    """Test the mapping with sample parser output"""
    
    # Sample parser output (simulating our enhanced parser)
    sample_parser_output = {
        "basics": {
            "name": "Dominic R. Thorne",
            "email": "d.thorne.revenue@growth-nexus.com",
            "phone": "+916155550144",
            "location": "Nashville TN"
        },
        "work": [
            {
                "company": "Omni Stream Global",
                "title": "Chief Revenue Officer",
                "location": "Nashville",
                "date_range": "January 2021 - Current",
                "description": "Strategic leadership and executive oversight...",
                "bullet_points": ["Revenue Transformation", "Pipeline Acceleration"]
            }
        ],
        "education": [
            {
                "institution": "The University Of Chicago Booth School Of Business",
                "degree": "Master Of Business Administration (MBA)",
                "field": "Strategic Management & Marketing"
            }
        ],
        "skills": [
            {
                "name": "Communication",
                "category": "Soft Skills",
                "confidence": 0.85
            },
            {
                "name": "Leadership",
                "category": "Soft Skills", 
                "confidence": 0.85
            }
        ],
        "summary": {
            "content": "High-impact Revenue Executive with 12+ years of experience...",
            "confidence": 0.85
        },
        "metadata": {
            "parsing_confidence": 0.73,
            "parsing_timestamp": "2026-03-17T15:37:47.612826"
        }
    }
    
    # Map to frontend format
    frontend_result = map_parser_to_frontend_format(sample_parser_output)
    
    print("🔍 PARSER OUTPUT (Our Enhanced Parser):")
    print(json.dumps(sample_parser_output, indent=2))
    
    print("\n🎯 FRONTEND FORMAT (Expected by UI):")
    print(json.dumps(frontend_result, indent=2))
    
    print("\n✅ Mapping Status:")
    print(f"  - Candidate Name: {frontend_result['candidate']['full_name']}")
    print(f"  - Email: {frontend_result['candidate']['email']}")
    print(f"  - Work History: {len(frontend_result['candidate']['work_history'])} entries")
    print(f"  - Education: {len(frontend_result['candidate']['education'])} entries")
    print(f"  - Skills: {len(frontend_result['candidate']['skills'])} entries")
    print(f"  - Candidate Skills: {len(frontend_result['candidate']['candidate_skills'])} entries")

if __name__ == "__main__":
    test_mapping()
