#!/usr/bin/env python3
"""Trace section detection step by step."""

from parsers.text_extractor import TextExtractor
from parsers.section_splitter import SectionSplitter

file_path = "/Users/anjanyelle/Desktop/untitled folder 3/Lakshya-LLM-Resume-Parser/backend/src/uploads/a3475d4b-c664-4fcc-aa95-3ae277c305da_RAGHAVENDRA_PRASAD_VEMURI___9_pages__Devops.docx"

# Extract text
extractor = TextExtractor()
result = extractor.extract(file_path)
text = result['text']

# Manually trace section splitting
splitter = SectionSplitter()
text = splitter._clean_pdf_artifacts(text)

sections = {}
current_section = 'other'
current_content = []

lines = text.split('\n')

print("TRACING SECTION DETECTION:\n")

for i, line in enumerate(lines[:100]):  # First 100 lines
    stripped_line = line.strip()
    
    # Check if this line is a section header
    section_name = splitter.detect_section_header(stripped_line)
    
    if section_name:
        # Save previous section content
        if current_content:
            content_preview = '\n'.join(current_content)[:100]
            print(f"\n[Line {i}] SAVING section '{current_section}': {len(current_content)} lines")
            print(f"  Preview: {content_preview}...")
        
        # Start new section
        print(f"\n[Line {i}] NEW SECTION DETECTED: '{section_name}'")
        print(f"  Header line: '{stripped_line}'")
        current_section = section_name
        current_content = []
    else:
        # Add line to current section content
        if stripped_line or current_content:
            current_content.append(line)
            if i < 50 and stripped_line:  # Show first 50 non-empty lines
                print(f"[Line {i}] → {current_section}: {stripped_line[:80]}")

print(f"\n\nFINAL SECTION: {current_section} with {len(current_content)} lines")
