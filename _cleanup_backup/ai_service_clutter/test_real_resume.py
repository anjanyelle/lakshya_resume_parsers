#!/usr/bin/env python3
"""
Real end-to-end test with an actual resume file from the resumes/ folder.
"""

import sys
sys.path.insert(0, '.')
import glob
import os

# Find a sample resume
resume_files = glob.glob('../resumes/*.pdf') + glob.glob('../resumes/*.docx') + glob.glob('../resumes/*.txt')
if not resume_files:
    print("ERROR: No resume files found in ../resumes/")
    sys.exit(1)

test_file = resume_files[0]
print(f"Testing with: {test_file}")
print(f"File size: {os.path.getsize(test_file)} bytes")
print("=" * 80)

from parsers.master_parser import MasterParser

print("\nInitializing MasterParser...")
parser = MasterParser()
print("✅ MasterParser initialized\n")

print("Parsing resume...")
result = parser.parse(test_file)
print("✅ Parsing completed\n")

print("=" * 80)
print("=== PARSED DATA ===")
print("=" * 80)
pd = result.get('parsed_data', {})
print(f"Name: {pd.get('name') or pd.get('personal_info', {}).get('name')}")
print(f"Email: {pd.get('email') or pd.get('personal_info', {}).get('email')}")
print(f"Phone: {pd.get('phone') or pd.get('personal_info', {}).get('phone')}")
print(f"Skills count: {len(pd.get('skills', []))}")
print(f"Skills: {pd.get('skills', [])[:10]}")  # Show first 10 skills
print(f"Experience count: {len(pd.get('experience', []))}")
print(f"Education count: {len(pd.get('education', []))}")
print(f"Companies: {pd.get('companies', [])[:5]}")  # Show first 5 companies
print(f"Locations: {pd.get('locations', [])[:5]}")  # Show first 5 locations
print(f"Titles: {pd.get('titles', [])[:5]}")  # Show first 5 titles

print("\n" + "=" * 80)
print("=== CONFIDENCE SCORES ===")
print("=" * 80)
confidence = pd.get('confidence', {})
if confidence:
    print(f"Overall: {confidence.get('overall', 'N/A')}")
    print(f"Quality Level: {confidence.get('quality_level', 'N/A')}")
    print(f"Needs Review: {confidence.get('needs_review', 'N/A')}")
    field_scores = confidence.get('fields', {})
    if field_scores:
        print("\nField Scores:")
        for field, score in field_scores.items():
            print(f"  {field}: {score:.2f}")

print("\n" + "=" * 80)
print("=== METADATA ===")
print("=" * 80)
meta = result.get('metadata', {})
print(f"Text quality: {meta.get('text_quality')}")
print(f"Sections detected: {meta.get('sections_detected')}")
print(f"Validation warnings: {meta.get('validation_warnings')}")
print(f"Processing time: {meta.get('processing_time_ms')}ms")
print(f"Sources used: {meta.get('sources_used')}")

# Check for LLM conflict resolution
llm_conflict = meta.get('llm_conflict_resolution', {})
if llm_conflict:
    print("\n" + "=" * 80)
    print("=== LLM CONFLICT RESOLUTION ===")
    print("=" * 80)
    print(f"Conflicts detected: {llm_conflict.get('conflicts_detected', 0)}")
    print(f"Fields resolved: {llm_conflict.get('fields_resolved', [])}")
    print(f"LLM calls saved: {llm_conflict.get('llm_calls_saved', False)}")

print("\n" + "=" * 80)
print("=== PROCESSING METRICS ===")
print("=" * 80)
metrics = pd.get('processing_metrics', {})
if metrics:
    for key, value in metrics.items():
        print(f"{key}: {value:.2f}ms")

print("\n" + "=" * 80)
print("✅ END-TO-END TEST COMPLETED SUCCESSFULLY")
print("=" * 80)
