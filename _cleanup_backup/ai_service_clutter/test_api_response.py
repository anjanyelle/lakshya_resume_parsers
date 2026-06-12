#!/usr/bin/env python3
"""
Test the actual API response to verify work_history field is included
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from parsers.master_parser import MasterParser

def test_api_response():
    """Test that the parser response includes both work_experience and work_history"""
    
    print("Testing API response field mapping...")
    print("=" * 60)
    
    # Initialize master parser
    parser = MasterParser()
    
    # Sample text to parse
    sample_text = """
    John Doe
    Email: john.doe@example.com
    Phone: (555) 123-4567
    
    WORK EXPERIENCE
    Senior Software Engineer
    Google, Mountain View, CA
    January 2020 - Present
    
    - Led development of cloud-native applications
    - Managed team of 5 engineers
    - Improved system performance by 40%
    
    Software Engineer
    Microsoft, Redmond, WA
    June 2018 - December 2019
    
    - Developed REST APIs
    - Worked on Azure cloud services
    - Optimized database queries
    
    EDUCATION
    Bachelor of Science in Computer Science
    Stanford University
    2014 - 2018
    
    SKILLS
    Python, Java, AWS, Docker, Kubernetes, React
    """
    
    # Parse the text
    print("Parsing sample resume text...")
    result = parser.parse_text(sample_text, "test-candidate-123")
    
    # Check response structure
    print(f"\n✅ Status: {result.get('status')}")
    print(f"✅ Name: {result.get('name')}")
    print(f"✅ Email: {result.get('email')}")
    
    # Check work_experience field
    work_exp = result.get('work_experience', [])
    print(f"\n📋 work_experience: {len(work_exp)} entries")
    for i, exp in enumerate(work_exp, 1):
        print(f"   {i}. {exp.get('job_title', 'N/A')} at {exp.get('company_name', 'N/A')}")
    
    # Check work_history field (backend compatibility)
    work_hist = result.get('work_history', [])
    print(f"\n📋 work_history: {len(work_hist)} entries")
    for i, exp in enumerate(work_hist, 1):
        print(f"   {i}. {exp.get('job_title', 'N/A')} at {exp.get('company_name', 'N/A')}")
    
    # Verify they match
    if work_exp and work_hist:
        match = work_exp == work_hist
        print(f"\n✅ Fields match: {match}")
        
        if match:
            print("✅ Backend compatibility issue RESOLVED!")
            print("✅ The API now returns both 'work_experience' and 'work_history'")
        else:
            print("❌ Fields don't match - need to investigate")
    else:
        print(f"⚠️  No work experience data found")
    
    # Check other fields
    skills = result.get('skills', [])
    education = result.get('education', [])
    print(f"\n📚 Skills: {len(skills)} items")
    print(f"🎓 Education: {len(education)} items")
    
    print("\n" + "=" * 60)
    print("API Response Test Complete!")
    
    return result

if __name__ == "__main__":
    test_api_response()
