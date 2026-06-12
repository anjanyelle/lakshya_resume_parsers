#!/usr/bin/env python3
"""
Test to reproduce the job title/company swap bug
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ai-service'))

from parsers.experience_extractor import extract_experience

# Your actual resume text
resume_text = """
WORK EXPERIENCE

Software Engineer
TechNova Solutions Pvt Ltd
Jan 2022 - Present
- Developed responsive web applications using React.js
- Integrated REST APIs and improved performance by 30%

Frontend Developer
CodeCraft Technologies
Jun 2020 - Dec 2021
- Built reusable UI components using React and Redux
- Worked closely with backend team for API integration

Junior Developer
WebSpark Pvt Ltd
May 2019 - May 2020
- Assisted in developing web pages using HTML, CSS, JavaScript

EDUCATION

Bachelor of Technology (B.Tech) in Computer Science
JNTU Hyderabad
2015 - 2019

SKILLS
React.js, JavaScript, HTML, CSS, Redux
"""

print("=" * 80)
print("TESTING EXPERIENCE EXTRACTION")
print("=" * 80)

experiences = extract_experience(resume_text)

print(f"\n✅ Extracted {len(experiences)} experiences:\n")

for i, exp in enumerate(experiences, 1):
    print(f"{i}. Title: '{exp.get('title', 'N/A')}'")
    print(f"   Company: '{exp.get('company', 'N/A')}'")
    print(f"   Dates: {exp.get('start_date')} to {exp.get('end_date')}")
    print(f"   Description: {exp.get('description', '')[:100]}...")
    print()

print("=" * 80)
print("EXPECTED RESULTS:")
print("=" * 80)
print("1. Title: 'Software Engineer'")
print("   Company: 'TechNova Solutions Pvt Ltd'")
print()
print("2. Title: 'Frontend Developer'")
print("   Company: 'CodeCraft Technologies'")
print()
print("3. Title: 'Junior Developer'")
print("   Company: 'WebSpark Pvt Ltd'")
print()
print("SKILLS section should NOT be extracted as work experience")
