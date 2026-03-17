#!/usr/bin/env python3
"""Test header detection line by line."""

from parsers.text_extractor import TextExtractor
from parsers.section_splitter import SectionSplitter

file_path = "/Users/anjanyelle/Desktop/untitled folder 3/Lakshya-LLM-Resume-Parser/backend/src/uploads/a3475d4b-c664-4fcc-aa95-3ae277c305da_RAGHAVENDRA_PRASAD_VEMURI___9_pages__Devops.docx"

# Extract text
extractor = TextExtractor()
result = extractor.extract(file_path)
text = result['text']

# Test header detection
splitter = SectionSplitter()

lines = text.split('\n')
print("Testing header detection on each line:\n")

for i, line in enumerate(lines[:100]):  # First 100 lines
    stripped = line.strip()
    if len(stripped) > 3:
        detected = splitter.detect_section_header(stripped)
        if detected:
            print(f"Line {i}: '{stripped[:80]}' → DETECTED AS: {detected}")
        elif any(keyword in stripped.lower() for keyword in ['skills', 'experience', 'education', 'summary', 'competencies']):
            print(f"Line {i}: '{stripped[:80]}' → NOT DETECTED (contains keyword)")
