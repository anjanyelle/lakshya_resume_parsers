#!/usr/bin/env python3
"""
Debug script to see what's happening with John's resume
"""

from resume_parser_pipeline import SectionExtractor, ModelInference, TextChunker

# Read John's resume
with open('test_John.txt', 'r') as f:
    resume_text = f.read()

print("="*80)
print("🔍 DEBUGGING JOHN'S RESUME")
print("="*80)

# Step 1: Section Extraction
print("\nSTEP 1: Section Extraction")
print("-"*80)
sections = SectionExtractor.extract_sections(resume_text)
exp_text = sections.get('experience', '')
edu_text = sections.get('education', '')

print(f"Experience section length: {len(exp_text)} chars")
print(f"Education section length: {len(edu_text)} chars")

# Step 2: Pre-processing
print("\nSTEP 2: Pre-processing")
print("-"*80)
print("BEFORE pre-processing:")
print(exp_text[:300])
print("\n" + "-"*80)

preprocessed = TextChunker.preprocess_text(exp_text)
print("AFTER pre-processing:")
print(preprocessed[:300])

# Step 3: Model Inference
print("\n" + "="*80)
print("STEP 3: Model Inference")
print("="*80)

model = ModelInference("./models/resume-ner-deberta")
entities = model.extract_entities(exp_text)

print(f"\nTotal entities extracted: {len(entities)}")
print("\nEntities by type:")
companies = [e for e in entities if e['label'] == 'COMPANY']
roles = [e for e in entities if e['label'] == 'ROLE']
dates = [e for e in entities if e['label'] in ['START_DATE', 'END_DATE']]

print(f"  COMPANY: {len(companies)}")
for c in companies:
    print(f"    - {c['text']}")

print(f"  ROLE: {len(roles)}")
for r in roles:
    print(f"    - {r['text']}")

print(f"  DATES: {len(dates)}")
for d in dates:
    print(f"    - {d['text']} ({d['label']})")
