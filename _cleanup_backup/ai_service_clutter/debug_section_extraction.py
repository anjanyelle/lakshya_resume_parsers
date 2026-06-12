#!/usr/bin/env python3
"""Debug section extraction to see what text is being passed to structured parser."""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from parsers.text_extractor import TextExtractor
from parsers.deberta_ner_parser import DeBERTaNerParser

pdf_path = "/Users/anjanyelle/Desktop/untitled folder 3/Lakshya-LLM-Resume-Parser/backend/src/uploads/164d0638-e69b-4e64-ade5-316745f93d94_Untitled_document__2_.docx"

print("🔍 DEBUGGING SECTION EXTRACTION")
print("=" * 70)

# Extract text
extractor = TextExtractor()
result = extractor.extract(pdf_path)
text = result.get('text', '')

# Extract sections using DeBERTa parser's method
parser = DeBERTaNerParser()
sections = parser.extract_target_sections(text)

print(f"\n📊 WORK EXPERIENCE SECTION ({len(sections['work_experience_text'])} chars):")
print("-" * 70)
print(sections['work_experience_text'])
print("-" * 70)

print(f"\n📊 EDUCATION SECTION ({len(sections['education_text'])} chars):")
print("-" * 70)
print(sections['education_text'])
print("-" * 70)

# Now parse with structured parser
if parser.structured_parser:
    experiences = parser.structured_parser.parse_work_section(sections['work_experience_text'])
    print(f"\n✅ Structured parser found {len(experiences)} experiences")
    for i, exp in enumerate(experiences, 1):
        print(f"\n{i}. {exp.get('job_title')} at {exp.get('company_name')}")
