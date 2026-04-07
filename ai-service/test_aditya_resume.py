#!/usr/bin/env python3
"""Test Aditya's resume to see what format it uses."""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from parsers.text_extractor import TextExtractor
from parsers.work_experience_structured_parser import StructuredWorkExperienceParser

pdf_path = "/Users/anjanyelle/Desktop/untitled folder 3/Lakshya-LLM-Resume-Parser/backend/src/uploads/22869285-11ca-4982-8b7c-36342e851ccb_Untitled_document__6_.docx"

print("🔍 DEBUGGING ADITYA'S RESUME")
print("=" * 70)

# Extract text
extractor = TextExtractor()
result = extractor.extract(pdf_path)
text = result.get('text', '')

print(f"\n📝 FULL TEXT ({len(text)} chars):")
print("-" * 70)
print(text[:2000])  # First 2000 chars
print("-" * 70)

# Find work experience section
lines = text.split('\n')
work_start = -1
work_end = -1

for i, line in enumerate(lines):
    if 'professional experience' in line.lower() or 'work experience' in line.lower():
        work_start = i
        print(f"\n✅ Found work experience header at line {i}: {line}")
    elif work_start != -1 and ('education' in line.lower() or 'ai & data projects' in line.lower() or 'system design' in line.lower()):
        work_end = i
        print(f"✅ Found end marker at line {i}: {line}")
        break

if work_start != -1:
    if work_end == -1:
        work_end = len(lines)
    
    work_text = '\n'.join(lines[work_start:work_end])
    print(f"\n📊 WORK EXPERIENCE SECTION ({len(work_text)} chars):")
    print("-" * 70)
    print(work_text[:1500])  # First 1500 chars
    print("-" * 70)
    
    # Test structured parser
    parser = StructuredWorkExperienceParser()
    experiences = parser.parse_work_section(work_text)
    
    print(f"\n✅ PARSED {len(experiences)} EXPERIENCES:")
    print("-" * 70)
    for i, exp in enumerate(experiences, 1):
        print(f"\nExperience {i}:")
        print(f"  Job Title: {exp.get('job_title')}")
        print(f"  Company: {exp.get('company_name')}")
        print(f"  Location: {exp.get('location')}")
        print(f"  Start: {exp.get('start_date')}")
        print(f"  End: {exp.get('end_date')}")
        print(f"  Clients: {len(exp.get('clients', []))}")
else:
    print("\n❌ No work experience section found")
