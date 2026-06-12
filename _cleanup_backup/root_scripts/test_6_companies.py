#!/usr/bin/env python3
"""
Test extraction of 6 work experiences to verify the fix.
"""

import sys
sys.path.insert(0, 'ai-service')

from parsers.experience_extractor import extract_experience

# Resume with 6 companies
resume_text = """
PROFESSIONAL EXPERIENCE

Senior Software Engineer
Google Inc
Mountain View, CA
January 2023 to Present
Responsibilities:
- Led development of cloud infrastructure
- Managed team of 5 engineers

Software Engineer
Amazon Web Services
Seattle, WA
June 2021 to December 2022
Responsibilities:
- Developed microservices architecture
- Implemented CI/CD pipelines

Full Stack Developer
Microsoft Corporation
Redmond, WA
March 2020 to May 2021
Responsibilities:
- Built web applications using React and Node.js
- Integrated Azure services

Backend Developer
Meta Platforms
Menlo Park, CA
August 2018 to February 2020
Responsibilities:
- Developed REST APIs
- Optimized database queries

Junior Developer
Apple Inc
Cupertino, CA
January 2017 to July 2018
Responsibilities:
- Maintained iOS applications
- Fixed bugs and implemented features

Software Intern
Tesla Inc
Palo Alto, CA
June 2016 to December 2016
Responsibilities:
- Assisted in software development
- Wrote unit tests
"""

print("=" * 80)
print("TESTING 6-COMPANY RESUME EXTRACTION")
print("=" * 80)

# Extract experiences
experiences = extract_experience(resume_text)

print(f"\n✅ Extracted {len(experiences)} work experiences:\n")

for i, exp in enumerate(experiences, 1):
    print(f"{i}. {exp.get('title', 'N/A')} at {exp.get('company', 'N/A')}")
    print(f"   Dates: {exp.get('start_date', 'N/A')} to {exp.get('end_date') or 'Present'}")
    print(f"   Current: {exp.get('is_current', False)}")
    print()

print("=" * 80)
print(f"EXPECTED: 6 experiences")
print(f"ACTUAL: {len(experiences)} experiences")
if len(experiences) == 6:
    print("✅ SUCCESS: All 6 experiences extracted!")
else:
    print(f"❌ FAILED: Only {len(experiences)} experiences extracted")
print("=" * 80)
