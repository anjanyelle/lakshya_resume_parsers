#!/usr/bin/env python3
"""
Test script for the resume parsing pipeline
"""

import json
from resume_parser_pipeline import parse_resume


def test_pipeline():
    """Test the resume parsing pipeline with sample data"""
    
    print("="*80)
    print("🧪 TESTING RESUME PARSING PIPELINE")
    print("="*80)
    
    # Test Case 1: Well-structured resume with clear sections
    test_case_1 = """
    Anjan Yelle
    Software Developer
    
    WORK EXPERIENCE:
    
    Software Developer
    Lalataksha Consulting Services Pvt Ltd
    Jan 2023 - Present
    Bangalore, India
    - Developed web applications using React.js and Node.js
    - Built RESTful APIs and improved system performance
    
    Software Developer
    Gatnix Technologies Pvt Ltd
    Jun 2021 - Dec 2022
    Hyderabad, India
    - Worked on React applications and mobile apps
    - Developed timesheet and CRM systems
    
    EDUCATION:
    
    Bachelor of Technology in Computer Science
    JNTU Hyderabad
    2016 - 2020
    """
    
    print("\n📄 TEST CASE 1: Well-structured resume")
    print("-" * 80)
    result_1 = parse_resume(test_case_1)
    print(json.dumps(result_1, indent=2))
    
    # Test Case 2: Resume without clear section headers (fallback to chunking)
    test_case_2 = """
    John Smith
    
    Worked at Infosys as Senior Software Engineer from Jan 2021 to Mar 2023 in Bangalore.
    Developed enterprise applications and led a team of 5 developers.
    
    Previously at TCS as Junior Developer from 2019 to 2021 in Hyderabad.
    Worked on web applications using React and Node.js.
    
    Completed Bachelor of Technology in Computer Science from IIT Delhi in 2019.
    Graduated with honors and received academic excellence award.
    """
    
    print("\n" + "="*80)
    print("📄 TEST CASE 2: Resume without clear sections (chunking fallback)")
    print("-" * 80)
    result_2 = parse_resume(test_case_2)
    print(json.dumps(result_2, indent=2))
    
    # Test Case 3: Multiple education entries
    test_case_3 = """
    PROFESSIONAL EXPERIENCE:
    
    Senior Developer at Microsoft
    Role: Senior Software Engineer
    Duration: 2020 - Present
    Location: Seattle, USA
    
    Developer at Amazon
    Role: Software Developer
    Duration: 2018 - 2020
    Location: Seattle, USA
    
    ACADEMIC BACKGROUND:
    
    Master of Science in Computer Science
    Stanford University
    2016 - 2018
    
    Bachelor of Engineering in Information Technology
    MIT
    2012 - 2016
    """
    
    print("\n" + "="*80)
    print("📄 TEST CASE 3: Multiple entries")
    print("-" * 80)
    result_3 = parse_resume(test_case_3)
    print(json.dumps(result_3, indent=2))
    
    print("\n" + "="*80)
    print("✅ PIPELINE TESTING COMPLETE")
    print("="*80)


if __name__ == "__main__":
    test_pipeline()
