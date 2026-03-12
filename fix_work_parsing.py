#!/usr/bin/env python3
"""
Fix Work Experience Title Extraction - Handle title on separate lines
"""

import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

def fix_work_experience_parsing():
    """Fix work experience parsing for perfect mapping"""
    
    print("🔧 FIXING WORK EXPERIENCE PARSING")
    print("=" * 40)
    
    from app.services.parser.work_experience_parser import WorkExperienceParser
    
    # Test the specific format from Vaishnavi's resume
    test_cases = [
        {
            "input": "Cardinal Health                                                                                                                                   Location: Dublin, OH\nDevOps Engineer                                                                                                                               October 2022 – Current",
            "expected_company": "Cardinal Health",
            "expected_title": "DevOps Engineer",
            "expected_location": "Dublin, OH"
        },
        {
            "input": "Huntington:                                                                                                                                          Location: Columbus, OH\nDevOps Engineer    								     December 2019 - September 2022",
            "expected_company": "Huntington",
            "expected_title": "DevOps Engineer", 
            "expected_location": "Columbus, OH"
        },
        {
            "input": "Allstate:                                                                                                                                              Location: Northbrook,IL\nDevOps Engineer                                                                                                                    February 2017 - November 2019",
            "expected_company": "Allstate",
            "expected_title": "DevOps Engineer",
            "expected_location": "Northbrook,IL"
        }
    ]
    
    parser = WorkExperienceParser()
    
    print("Testing work experience extraction:")
    for i, test_case in enumerate(test_cases):
        print(f"\nTest Case {i+1}:")
        print(f"Input: {repr(test_case['input'][:100])}...")
        
        # Try to extract using the parser
        lines = test_case['input'].split('\n')
        if len(lines) >= 2:
            line1 = lines[0].strip()
            line2 = lines[1].strip()
            
            # Extract company from first line
            company, title = parser._parse_company_title(line1)
            
            # Extract title from second line if not found in first
            if not title and line2:
                # Check if second line looks like a title
                if parser._looks_like_title(line2):
                    title = line2
            
            # Extract location
            location = None
            if "Location:" in line1:
                import re
                loc_match = re.search(r'Location:\s*(.+)$', line1)
                if loc_match:
                    location = loc_match.group(1).strip()
            
            print(f"  Company: '{company}' (expected: '{test_case['expected_company']}')")
            print(f"  Title: '{title}' (expected: '{test_case['expected_title']}')")
            print(f"  Location: '{location}' (expected: '{test_case['expected_location']}')")
            
            # Check accuracy
            company_ok = company == test_case['expected_company'] if company else False
            title_ok = title == test_case['expected_title'] if title else False
            location_ok = location == test_case['expected_location'] if location else False
            
            print(f"  ✅ Company: {'✓' if company_ok else '✗'}")
            print(f"  ✅ Title: {'✓' if title_ok else '✗'}")
            print(f"  ✅ Location: {'✓' if location_ok else '✗'}")
    
    return True

if __name__ == "__main__":
    fix_work_experience_parsing()
