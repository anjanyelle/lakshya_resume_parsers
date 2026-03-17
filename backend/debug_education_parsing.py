# -*- coding: utf-8 -*-
"""
Debug education parsing
"""

import re

def debug_education_parsing():
    print("🔍 DEBUGGING EDUCATION PARSING")
    print("=" * 50)
    
    # Test with Rahul's education section
    rahul_edu_text = """
Bachelor of Technology in Computer Science & Engineering – Osmania University, Hyderabad, India, 2009-2013
"""
    
    print("📄 Original Education Text:")
    print(rahul_edu_text.strip())
    
    # Test patterns
    edu_patterns = [
        # Super simple pattern - just split by dash and commas
        r'([A-Za-z\s]+(?:Bachelor|Master|PhD|Associate)[A-Za-z\s]*)\s*[–-]\s*([A-Za-z\s]+(?:University|College|Institute|Technology))\s*,\s*([A-Za-z\s,]+)\s*,\s*(\d{4}[–-]\d{4})',
        # Even more flexible
        r'(.+?)\s*[–-]\s*(.+?)\s*,\s*(.+?)\s*,\s*(\d{4}[–-]\d{4})',
        # Match everything
        r'(.+?)\s*[–-]\s*(.+?)\s*,\s*(.+?)\s*,\s*(\d{4}[–-]\d{4})'
    ]
    
    print(f"\n🔍 Testing {len(edu_patterns)} patterns:")
    
    for i, pattern in enumerate(edu_patterns):
        print(f"\n  Pattern {i+1}: {pattern}")
        matches = re.findall(pattern, rahul_edu_text)
        print(f"  Matches: {len(matches)}")
        for match in matches:
            print(f"    - {match}")
            if len(match) == 4:
                degree, university, location, date = match
                print(f"      Degree: {degree.strip()}")
                print(f"      University: {university.strip()}")
                print(f"      Location: {location.strip()}")
                print(f"      Date: {date.strip()}")
    
    # Test with full resume
    print(f"\n🔍 Testing with full resume text:")
    full_resume = """
## EDUCATION
Bachelor of Technology in Computer Science & Engineering – Osmania University, Hyderabad, India, 2009-2013
"""
    
    edu_section_match = re.search(r'## EDUCATION\s*\n*(.*?)(?=\n##|\Z)', full_resume, re.IGNORECASE | re.DOTALL)
    
    if edu_section_match:
        edu_text = edu_section_match.group(1).strip()
        print(f"✅ Found education section: {edu_text}")
        
        for i, pattern in enumerate(edu_patterns):
            matches = re.findall(pattern, edu_text)
            print(f"  Pattern {i+1}: {len(matches)} matches")
            for match in matches:
                print(f"    - {match}")
    else:
        print("❌ No education section found!")

if __name__ == "__main__":
    debug_education_parsing()
