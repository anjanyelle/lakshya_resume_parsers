#!/usr/bin/env python3
"""
Visual debugging tool to understand text extraction quality issues.
Shows exactly what text is extracted vs what's missing.
"""

import sys
sys.path.insert(0, '.')
import glob
import os
from pathlib import Path

# Find resume files
resume_files = glob.glob('../resumes/*.pdf') + glob.glob('../resumes/*.docx')
if not resume_files:
    print("ERROR: No resume files found in ../resumes/")
    sys.exit(1)

print("Available resumes:")
for i, file in enumerate(resume_files, 1):
    print(f"{i}. {os.path.basename(file)}")

# Use first file or let user choose
test_file = resume_files[0]
print(f"\n{'='*80}")
print(f"Testing with: {os.path.basename(test_file)}")
print(f"File size: {os.path.getsize(test_file):,} bytes")
print(f"{'='*80}\n")

from parsers.text_extractor import TextExtractor

# Extract text
extractor = TextExtractor()
result = extractor.extract(test_file)
extracted_text = result['text']

print("### EXTRACTION RESULTS ###\n")
print(f"Total characters: {len(extracted_text):,}")
print(f"Total words: {len(extracted_text.split()):,}")
print(f"Total lines: {len(extracted_text.splitlines()):,}")
print(f"Quality score: {result.get('quality_score', 'N/A')}")
print(f"Extraction method: {result.get('extraction_method', 'N/A')}")

print(f"\n{'='*80}")
print("### FIRST 1000 CHARACTERS ###")
print(f"{'='*80}\n")
print(extracted_text[:1000])

print(f"\n{'='*80}")
print("### FIRST 20 LINES ###")
print(f"{'='*80}\n")
for i, line in enumerate(extracted_text.splitlines()[:20], 1):
    print(f"{i:2d}: {line}")

print(f"\n{'='*80}")
print("### SECTION DETECTION ###")
print(f"{'='*80}\n")

from parsers.section_splitter import SectionSplitter
splitter = SectionSplitter()
sections = splitter.split(extracted_text)

for section_name, section_text in sections.items():
    print(f"\n{section_name.upper()}: {len(section_text)} chars")
    print(f"Preview: {section_text[:200]}...")

print(f"\n{'='*80}")
print("### FIELD EXTRACTION TEST ###")
print(f"{'='*80}\n")

from parsers.rule_parser import RuleBasedParser
parser = RuleBasedParser()

# Test individual field extraction
print("Name candidates:", parser.extract_name_candidates(extracted_text))
print("Final name:", parser.extract_name(extracted_text))
print("Email:", parser.extract_email(extracted_text))
print("Phone:", parser.extract_phone(extracted_text))
print("LinkedIn:", parser.extract_linkedin(extracted_text))

# Skills
skills_section = sections.get('skills', extracted_text[:2000])
skills = parser.extract_skills(skills_section)
print(f"Skills found: {len(skills)}")
print(f"First 10 skills: {skills[:10]}")

print(f"\n{'='*80}")
print("### FULL PARSING TEST ###")
print(f"{'='*80}\n")

from parsers.master_parser import MasterParser
master_parser = MasterParser()

# Parse the resume
parse_result = master_parser.parse(test_file)
parsed_data = parse_result.get('parsed_data', {})

print(f"Name: {parsed_data.get('name')}")
print(f"Email: {parsed_data.get('email')}")
print(f"Phone: {parsed_data.get('phone')}")
print(f"LinkedIn: {parsed_data.get('linkedin')}")
print(f"Skills count: {len(parsed_data.get('skills', []))}")
print(f"Experience count: {len(parsed_data.get('work_experience', []))}")
print(f"Education count: {len(parsed_data.get('education', []))}")

# Confidence scores
confidence = parsed_data.get('confidence', {})
if confidence:
    print(f"\nOverall confidence: {confidence.get('overall', 'N/A')}")
    print(f"Quality level: {confidence.get('quality_level', 'N/A')}")
    print(f"Needs review: {confidence.get('needs_review', 'N/A')}")
    
    field_scores = confidence.get('fields', {})
    if field_scores:
        print("\nField confidence scores:")
        for field, score in field_scores.items():
            status = "✅" if score >= 0.7 else "⚠️" if score >= 0.4 else "❌"
            print(f"  {status} {field}: {score:.2f}")

# Processing metrics
metadata = parse_result.get('metadata', {})
if metadata:
    print(f"\nProcessing time: {metadata.get('processing_time_ms', 'N/A')}ms")
    print(f"Sources used: {metadata.get('sources_used', [])}")

print(f"\n{'='*80}")
print("### EXTRACTION QUALITY ANALYSIS ###")
print(f"{'='*80}\n")

# Check if quality analysis exists
if 'extraction_quality' in parsed_data:
    quality = parsed_data['extraction_quality']
    print(f"Extraction quality: {quality.get('extraction_quality_percentage', 'N/A')}%")
    print(f"Text similarity: {quality.get('text_similarity_percentage', 'N/A')}%")
    print(f"Text loss: {quality.get('text_loss_percentage', 'N/A')}%")
    print(f"\nRecommendation: {quality.get('recommendation', 'N/A')}")
    
    if quality.get('missing_sections'):
        print(f"\nMissing sections: {quality['missing_sections']}")
    
    if quality.get('structure_loss'):
        print(f"\nStructure loss:")
        for loss in quality['structure_loss']:
            print(f"  - {loss}")
    
    if quality.get('metrics'):
        metrics = quality['metrics']
        print(f"\nDetailed metrics:")
        print(f"  Original text: {metrics.get('original_text_length', 'N/A')} chars")
        print(f"  Extracted text: {metrics.get('reconstructed_text_length', 'N/A')} chars")
        print(f"  Original words: {metrics.get('original_word_count', 'N/A')}")
        print(f"  Extracted words: {metrics.get('reconstructed_word_count', 'N/A')}")
        print(f"  Missing words: {metrics.get('missing_word_count', 'N/A')}")

print(f"\n{'='*80}")
print("### SUMMARY ###")
print(f"{'='*80}\n")

print("✅ Working correctly:")
if parsed_data.get('name'):
    print(f"  - Name extraction: {parsed_data['name']}")
if parsed_data.get('email'):
    print(f"  - Email extraction: {parsed_data['email']}")
if parsed_data.get('phone'):
    print(f"  - Phone extraction: {parsed_data['phone']}")
if len(parsed_data.get('skills', [])) > 0:
    print(f"  - Skills extraction: {len(parsed_data['skills'])} skills found")

print("\n❌ Issues found:")
if not parsed_data.get('name'):
    print("  - Name not extracted")
if not parsed_data.get('email'):
    print("  - Email not extracted")
if not parsed_data.get('phone'):
    print("  - Phone not extracted")
if len(parsed_data.get('work_experience', [])) == 0:
    print("  - Work experience not extracted (may need LLM API key)")
if len(parsed_data.get('education', [])) == 0:
    print("  - Education not extracted")

if 'extraction_quality' in parsed_data:
    text_loss = parsed_data['extraction_quality'].get('text_loss_percentage', 0)
    if text_loss > 50:
        print(f"  - High text loss: {text_loss:.1f}% (CRITICAL)")
    elif text_loss > 20:
        print(f"  - Moderate text loss: {text_loss:.1f}%")

print("\n💡 Recommendations:")
if len(parsed_data.get('work_experience', [])) == 0:
    print("  1. Add GEMINI_API_KEY to backend/.env for experience extraction")
if 'extraction_quality' in parsed_data and parsed_data['extraction_quality'].get('text_loss_percentage', 0) > 50:
    print("  2. Check if resume uses tables/text boxes (DOCX issue)")
    print("  3. Try converting DOCX to PDF and re-upload")
if not parsed_data.get('name'):
    print("  4. Check if name is in header/footer (may be skipped)")

print(f"\n{'='*80}")
print("Debug complete!")
print(f"{'='*80}\n")
