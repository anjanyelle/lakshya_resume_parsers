#!/usr/bin/env python3
"""
Debug Work Experience Parsing - Test with Vaishnavi's resume
"""

import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

def debug_work_parsing():
    """Debug work experience parsing issues"""
    
    print("🔍 DEBUGGING WORK EXPERIENCE PARSING")
    print("=" * 50)
    
    from app.services.parser.work_experience_parser import WorkExperienceParser
    
    # Test company extraction from Vaishnavi's resume
    test_lines = [
        "Cardinal Health                                                                                                                                   Location: Dublin, OH",
        "Huntington:                                                                                                                                          Location: Columbus, OH",
        "Allstate:                                                                                                                                              Location: Northbrook,IL",
        "Equifax:                                                                                                                                                 Location: Atlanta, GA",
        "Inno Minds:                                                                                                                                                  Location: Pune, India"
    ]
    
    print("1. Testing company extraction...")
    parser = WorkExperienceParser()
    
    for line in test_lines:
        company, title = parser._parse_company_title(line)
        print(f"   Input: '{line[:50]}...'")
        print(f"   Result: company='{company}', title='{title}'")
        print()
    
    print("2. Testing COMPANY_LOCATION_RE regex...")
    import re
    COMPANY_LOCATION_RE = re.compile(
        r"^(?P<company>[^:]+):\s*(?:Location:)?\s*(?P<location>.+)$",
        re.IGNORECASE
    )
    
    for line in test_lines:
        match = COMPANY_LOCATION_RE.search(line.strip())
        if match:
            company = match.group("company").strip()
            location = match.group("location").strip()
            print(f"   Input: '{line[:50]}...'")
            print(f"   Match: company='{company}', location='{location}'")
        else:
            print(f"   Input: '{line[:50]}...'")
            print(f"   Match: None")
        print()
    
    print("3. Testing full work experience parsing...")
    # Sample work experience text
    work_text = """
PROFESSIONAL EXPERIENCE
Cardinal Health                                                                                                                                   Location: Dublin, OH
DevOps Engineer                                                                                                                               October 2022 – Current
Responsibilities:
•	Led enterprise-wide migration from Apigee Edge to Apigee Hybrid...

Huntington:                                                                                                                                          Location: Columbus, OH
DevOps Engineer    								     December 2019 - September 2022
Responsibilities:
•	Led technical implementation and management of Apigee Hybrid...
"""
    
    jobs = parser.extract_individual_jobs(work_text)
    print(f"   Found {len(jobs)} jobs")
    
    for i, job in enumerate(jobs[:3]):  # Show first 3
        print(f"     Job {i+1}:")
        if isinstance(job, str):
            print(f"       Raw: {job[:100]}...")
        else:
            print(f"       Company: {getattr(job, 'company', 'N/A')}")
            print(f"       Title: {getattr(job, 'title', 'N/A')}")
            print(f"       Location: {getattr(job, 'location', 'N/A')}")
            print(f"       Dates: {getattr(job, 'start_date', 'N/A')} - {getattr(job, 'end_date', 'N/A')}")
        print()
    
    return True

if __name__ == "__main__":
    debug_work_parsing()
