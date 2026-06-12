#!/usr/bin/env python3
"""Test Rohan's resume to see what's being extracted."""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from parsers.text_extractor import TextExtractor
from parsers.work_experience_structured_parser import StructuredWorkExperienceParser

# Rohan's resume path
pdf_path = "/Users/anjanyelle/Desktop/untitled folder 3/Lakshya-LLM-Resume-Parser/backend/src/uploads/164d0638-e69b-4e64-ade5-316745f93d94_Untitled_document__2_.docx"

print("🔍 DEBUGGING ROHAN'S RESUME")
print("=" * 70)

# Extract text
extractor = TextExtractor()
result = extractor.extract(pdf_path)
text = result.get('text', '')

print(f"\n📝 EXTRACTED TEXT ({len(text)} chars):")
print("-" * 70)
print(text)
print("-" * 70)

# Find work experience section
lines = text.split('\n')
work_start = -1
work_end = -1

for i, line in enumerate(lines):
    if 'work experience' in line.lower():
        work_start = i
    elif work_start != -1 and ('education' in line.lower() or i == len(lines) - 1):
        work_end = i
        break

if work_start != -1:
    if work_end == -1:
        work_end = len(lines)
    
    work_text = '\n'.join(lines[work_start:work_end])
    print(f"\n📊 WORK EXPERIENCE SECTION:")
    print("-" * 70)
    print(work_text)
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
        print(f"  Current: {exp.get('is_current')}")
        print(f"  Clients: {len(exp.get('clients', []))}")
        for client in exp.get('clients', []):
            print(f"    - {client.get('client_name')}: {len(client.get('descriptions', []))} descriptions")
else:
    print("\n❌ No work experience section found")
