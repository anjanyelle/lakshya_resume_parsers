#!/usr/bin/env python3
"""Debug name extraction to see what's happening."""

import sys
sys.path.insert(0, '.')
import glob

# Find a sample resume
resume_files = glob.glob('../resumes/*.pdf')
if not resume_files:
    print("ERROR: No resume files found")
    sys.exit(1)

test_file = resume_files[0]
print(f"Testing with: {test_file}\n")

from parsers.text_extractor import TextExtractor
from parsers.rule_parser import RuleBasedParser

# Extract text
extractor = TextExtractor()
result = extractor.extract(test_file)
text = result['text']

print("=" * 80)
print("FIRST 30 LINES OF EXTRACTED TEXT:")
print("=" * 80)
lines = text.splitlines()
for i, line in enumerate(lines[:30], 1):
    print(f"{i:2d}: {line}")

print("\n" + "=" * 80)
print("NAME EXTRACTION TEST:")
print("=" * 80)

parser = RuleBasedParser()

# Test name candidates
candidates = parser.extract_name_candidates(text)
print(f"\nName candidates found: {candidates}")

# Test final name extraction
name = parser.extract_name(text)
print(f"\nFinal extracted name: {name}")

# Also check what AI parser would extract
print("\n" + "=" * 80)
print("AI NER PARSER TEST:")
print("=" * 80)
from parsers.ai_ner_parser import AINamedEntityParser
ai_parser = AINamedEntityParser()
entities = ai_parser.extract_entities(text[:2000])  # First 2000 chars
print(f"AI extracted names: {entities.get('names', [])}")
