#!/usr/bin/env python3
"""Test experience extraction."""

from parsers.text_extractor import TextExtractor
from parsers.section_splitter import SectionSplitter
from parsers.experience_extractor import ExperienceExtractor

file_path = "/Users/anjanyelle/Desktop/untitled folder 3/Lakshya-LLM-Resume-Parser/backend/src/uploads/a3475d4b-c664-4fcc-aa95-3ae277c305da_RAGHAVENDRA_PRASAD_VEMURI___9_pages__Devops.docx"

# Extract and split
extractor = TextExtractor()
result = extractor.extract(file_path)
text = result['text']

splitter = SectionSplitter()
sections = splitter.split_sections(text)

print(f"Sections found: {list(sections.keys())}\n")

# Check experience section
if 'experience' in sections:
    exp_text = sections['experience']
    print(f"EXPERIENCE SECTION ({len(exp_text)} chars):")
    print("="*80)
    print(exp_text[:1000])
    print("="*80)
    
    # Test experience extraction
    exp_extractor = ExperienceExtractor()
    result = exp_extractor.extract_work_experience(exp_text)
    
    print(f"\nEXTRACTED {len(result['work_experience'])} JOBS:\n")
    for i, job in enumerate(result['work_experience'], 1):
        print(f"Job {i}:")
        print(f"  Title: {job.get('job_title', 'N/A')}")
        print(f"  Company: {job.get('company_name', 'N/A')}")
        print(f"  Dates: {job.get('start_date', 'N/A')} - {job.get('end_date', 'N/A')}")
        print(f"  Location: {job.get('location', 'N/A')}")
        print(f"  Description preview: {job.get('description', '')[:100]}...")
        print()
else:
    print("❌ No experience section found!")
    print(f"Available sections: {list(sections.keys())}")
