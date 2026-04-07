#!/usr/bin/env python3
"""Debug _parse_experience_block to see why Accenture is failing."""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from parsers.work_experience_structured_parser import StructuredWorkExperienceParser

work_text = """Accenture
Senior Software Engineer
June 2016 – Dec 2019
Developed enterprise web applications using Angular and React.js
Built fraud detection systems using machine learning algorithms

Tata Consultancy Services (TCS)
Software Engineer"""

parser = StructuredWorkExperienceParser()
lines = work_text.split('\n')

print("🔍 TESTING ACCENTURE BLOCK PARSING")
print("=" * 70)

print("\n📝 Lines:")
for i, line in enumerate(lines):
    print(f"{i}: {line}")

print("\n🧪 Parsing from index 0 (Accenture):")
exp = parser._parse_experience_block(lines, 0)

if exp:
    print(f"\n✅ SUCCESS!")
    print(f"  Job Title: {exp.get('job_title')}")
    print(f"  Company: {exp.get('company_name')}")
    print(f"  Start: {exp.get('start_date')}")
    print(f"  End: {exp.get('end_date')}")
    print(f"  Next Index: {exp.get('_next_index')}")
else:
    print(f"\n❌ FAILED - returned None")

print("\n" + "=" * 70)
print("🧪 Full parse:")
experiences = parser.parse_work_section(work_text)
print(f"Found {len(experiences)} experiences")
for exp in experiences:
    print(f"  - {exp.get('job_title')} at {exp.get('company_name')}")
