#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app.services.enhanced_pipeline_final import EnhancedResumePipelineFinal

def test_direct_mapping():
    """Test the frontend mapping directly with enhanced parser output"""
    
    print("🧪 Testing Direct Frontend Mapping...")
    
    # Create sample enhanced parser output (what our enhanced parser should produce)
    sample_enhanced_output = {
        "basics": {
            "name": "## PROFESSIONAL SUMMARY",
            "email": "d.thorne.revenue@growth-nexus.com",
            "phone": "+916155550144",
            "location": "Nashville TN",
            "urls": {
                "linkedin": "https://linkedin.com/in/dominic-thorne",
                "github": "https://github.com/dominic-thorne"
            }
        },
        "work": [
            {
                "company": "Amazon Web Services",
                "title": "Senior Software Engineer",
                "location": "Seattle, WA",
                "date_range": "June 2020 - Present",
                "start_date": "June 2020",
                "end_date": "",
                "is_current": True,
                "description": "Led development of cloud infrastructure",
                "bullet_points": [
                    "Led development of cloud infrastructure",
                    "Managed team of 5 engineers"
                ]
            },
            {
                "company": "Microsoft",
                "title": "Software Engineer",
                "location": "Redmond, WA",
                "date_range": "January 2018 - May 2020",
                "start_date": "January 2018",
                "end_date": "May 2020",
                "is_current": False,
                "description": "Developed Azure services",
                "bullet_points": [
                    "Developed Azure services",
                    "Improved system performance by 40%"
                ]
            }
        ],
        "education": [
            {
                "institution": "University of Washington",
                "degree": "Bachelor of Science in Computer Science",
                "field": "Computer Science",
                "location": "Seattle, WA",
                "date_range": "2014 - 2018",
                "start_date": "2014",
                "end_date": "2018",
                "confidence": 0.7
            }
        ],
        "skills": [
            {
                "name": "Python",
                "category": "Programming Languages",
                "confidence": 0.85,
                "proficiency": "Intermediate"
            },
            {
                "name": "Java",
                "category": "Programming Languages",
                "confidence": 0.85,
                "proficiency": "Intermediate"
            },
            {
                "name": "AWS",
                "category": "Cloud Platforms",
                "confidence": 0.85,
                "proficiency": "Intermediate"
            },
            {
                "name": "Docker",
                "category": "DevOps",
                "confidence": 0.85,
                "proficiency": "Intermediate"
            }
        ],
        "certifications": [
            {
                "name": "AWS Certified Solutions Architect",
                "issuer": "Amazon Web Services",
                "date": "2021",
                "credential_id": "AWS-CSA-2021",
                "status": "Active",
                "description": "AWS Solutions Architect certification",
                "url": "https://aws.amazon.com/certification/",
                "confidence": 0.6
            },
            {
                "name": "Microsoft Certified: Azure Developer Associate",
                "issuer": "Microsoft",
                "date": "2019",
                "credential_id": "AZ-400-2019",
                "status": "Active",
                "description": "Azure Developer certification",
                "url": "https://docs.microsoft.com/en-us/learn/certifications/azure-developer/",
                "confidence": 0.6
            }
        ],
        "summary": {
            "content": "High-impact Revenue Executive with 12+ years of experience engineering hyper-growth for global technology leaders and high-valuation startups. Expert in the orchestration of integrated Sales, Marketing, and Customer Success ecosystems, specializing in transitioning organizations from transactional models to high-velocity, solution-based Enterprise engines.",
            "method": "markdown_heading",
            "confidence": 0.85,
            "evidence_heading": "PROFESSIONAL SUMMARY"
        },
        "metadata": {
            "parsing_confidence": 0.73,
            "data_quality": 90,
            "parsing_timestamp": "2026-03-17T15:37:47.612826",
            "sections_found": ["basics", "work", "education", "skills", "certifications", "summary"]
        }
    }
    
    # Initialize parser
    parser = EnhancedResumePipelineFinal()
    
    # Test the mapping directly
    frontend_result = parser._map_to_frontend_format(sample_enhanced_output)
    
    print("\n📋 ENHANCED PARSER OUTPUT (Backend):")
    print("=" * 60)
    import json
    print(json.dumps(sample_enhanced_output, indent=2))
    
    print("\n🎯 FRONTEND FORMAT (UI Expected):")
    print("=" * 60)
    print(json.dumps(frontend_result, indent=2))
    
    print("\n✅ MAPPING VERIFICATION:")
    print("=" * 60)
    print(f"  - Candidate Name: {frontend_result['candidate']['full_name']}")
    print(f"  - Email: {frontend_result['candidate']['email']}")
    print(f"  - Phone: {frontend_result['candidate']['phone']}")
    print(f"  - Location: {frontend_result['candidate']['location']}")
    print(f"  - LinkedIn: {frontend_result['candidate']['linkedin_url']}")
    print(f"  - GitHub: {frontend_result['candidate']['github_url']}")
    print(f"  - Summary: {len(frontend_result['candidate']['summary'])} chars")
    print(f"  - Work History: {len(frontend_result['candidate']['work_history'])} entries")
    print(f"  - Education: {len(frontend_result['candidate']['education'])} entries")
    print(f"  - Skills: {len(frontend_result['candidate']['skills'])} entries")
    print(f"  - Candidate Skills: {len(frontend_result['candidate']['candidate_skills'])} entries")
    print(f"  - Status: {frontend_result['candidate']['status']}")
    print(f"  - Confidence Score: {frontend_result['candidate']['confidence_score']}")
    
    print("\n🔍 WORK HISTORY DETAILS:")
    for i, work in enumerate(frontend_result['candidate']['work_history']):
        print(f"  {i+1}. {work['title']} at {work['company']}")
        print(f"     Location: {work['location']}")
        print(f"     Dates: {work['start_date']} - {work['end_date']}")
        print(f"     Current: {work['is_current']}")
        print(f"     Bullet Points: {len(work['bullet_points'])}")
    
    print("\n🔍 EDUCATION DETAILS:")
    for i, edu in enumerate(frontend_result['candidate']['education']):
        print(f"  {i+1}. {edu['degree']} at {edu['institution']}")
        print(f"     Field: {edu['field_of_study']}")
        print(f"     Dates: {edu['start_date']} - {edu['end_date']}")
    
    print("\n🔍 SKILLS DETAILS:")
    for i, skill in enumerate(frontend_result['candidate']['skills']):
        print(f"  {i+1}. {skill['skill']['name']} ({skill['skill']['category']})")
    
    return frontend_result

if __name__ == "__main__":
    test_direct_mapping()
