#!/usr/bin/env python3
"""
Trace entities through the entire pipeline
"""

from resume_parser_pipeline import SectionExtractor, ModelInference, PostProcessor, ResumeParser

# Read John's resume
with open('test_John.txt', 'r') as f:
    resume_text = f.read()

print("="*80)
print("🔍 TRACING ENTITIES THROUGH PIPELINE")
print("="*80)

# Step 1: Extract sections
sections = SectionExtractor.extract_sections(resume_text)
exp_text = sections.get('experience', '')

# Step 2: Extract entities
model = ModelInference("./models/resume-ner-deberta")
entities = model.extract_entities(exp_text)

print(f"\n📊 AFTER MODEL EXTRACTION: {len(entities)} entities")
companies_before = [e for e in entities if e['label'] == 'COMPANY']
print(f"   Companies: {len(companies_before)}")
for c in companies_before:
    print(f"     - {c['text']}")

# Step 3: Post-processing
cleaned = PostProcessor.clean_entities(entities)

print(f"\n🧹 AFTER POST-PROCESSING: {len(cleaned)} entities")
companies_after = [e for e in cleaned if e['label'] == 'COMPANY']
print(f"   Companies: {len(companies_after)}")
for c in companies_after:
    print(f"     - {c['text']}")

# Step 4: Full pipeline
print("\n" + "="*80)
print("🚀 FULL PIPELINE:")
print("="*80)

parser = ResumeParser("./models/resume-ner-deberta")
result = parser.parse(resume_text)

print(f"\n📊 FINAL OUTPUT:")
print(f"   Experience entries: {len(result['experience'])}")
for i, exp in enumerate(result['experience'], 1):
    print(f"   #{i}: Company='{exp['company']}', Role='{exp['role']}'")
