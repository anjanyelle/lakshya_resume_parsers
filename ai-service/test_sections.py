#!/usr/bin/env python3
"""Test section detection on the resume."""

from parsers.text_extractor import TextExtractor
from parsers.section_splitter import SectionSplitter

file_path = "/Users/anjanyelle/Desktop/untitled folder 3/Lakshya-LLM-Resume-Parser/backend/src/uploads/a3475d4b-c664-4fcc-aa95-3ae277c305da_RAGHAVENDRA_PRASAD_VEMURI___9_pages__Devops.docx"

# Extract text
extractor = TextExtractor()
result = extractor.extract(file_path)
text = result['text']

# Find TECHNICAL SKILLS MATRIX section manually
lines = text.split('\n')
for i, line in enumerate(lines):
    if 'TECHNICAL SKILLS' in line.upper():
        print(f"Line {i}: {line}")
        print(f"Next 10 lines:")
        for j in range(i+1, min(i+11, len(lines))):
            print(f"  {j}: {lines[j][:100]}")
        print()

# Now test section splitter
splitter = SectionSplitter()
sections = splitter.split_sections(text)

print(f"\n{'='*80}")
print(f"SECTIONS DETECTED: {len(sections)}")
print(f"{'='*80}\n")

for section_name, section_text in sections.items():
    print(f"\n{section_name.upper()}:")
    print(f"  Length: {len(section_text)} chars")
    print(f"  First 200 chars: {section_text[:200]}")
    print()
