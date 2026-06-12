#!/usr/bin/env python3
"""Test Ganesh's resume to see why 0 experiences were extracted."""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from parsers.text_extractor import TextExtractor
from parsers.work_experience_structured_parser import StructuredWorkExperienceParser
from parsers.deberta_ner_parser import DeBERTaNerParser

pdf_path = "/Users/anjanyelle/Desktop/untitled folder 3/Lakshya-LLM-Resume-Parser/backend/src/uploads/9b55c331-30fd-42ca-beff-1e632034ef6e_Ganesh_Resume_Temp9__3_.docx"

print("🔍 DEBUGGING GANESH'S RESUME")
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
    line_lower = line.lower().strip()
    if 'professional experience' in line_lower or 'work experience' in line_lower or 'experience' in line_lower:
        if len(line_lower) < 30:  # Likely a header
            work_start = i
            print(f"\n✅ Found work experience header at line {i}: {line}")
            break

if work_start != -1:
    # Find end
    for i in range(work_start + 1, len(lines)):
        line_lower = lines[i].lower().strip()
        if 'education' in line_lower or 'certification' in line_lower or 'skills' in line_lower:
            if len(line_lower) < 30:
                work_end = i
                print(f"✅ Found end marker at line {i}: {lines[i]}")
                break
    
    if work_end == -1:
        work_end = min(work_start + 100, len(lines))
    
    work_text = '\n'.join(lines[work_start:work_end])
    print(f"\n📊 WORK EXPERIENCE SECTION ({len(work_text)} chars):")
    print("-" * 70)
    print(work_text[:1500])
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
else:
    print("\n❌ No work experience section found")
    print("\nSearching for company names in text...")
    companies = ['Visa', 'Target', 'Mobile', 'Southwest Airlines', 'T-Mobile']
    for company in companies:
        if company.lower() in text.lower():
            print(f"  ✅ Found '{company}' in text")
