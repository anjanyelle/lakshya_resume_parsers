#!/usr/bin/env python3
"""
Debug script to examine extracted text from resume files.
Shows first 2000 characters and section detection results.
"""

import sys
from parsers.text_extractor import TextExtractor
from parsers.section_splitter import SectionSplitter

def debug_extraction(file_path: str):
    """Debug text extraction and section detection."""
    print(f"\n{'='*80}")
    print(f"DEBUGGING: {file_path}")
    print(f"{'='*80}\n")
    
    # Extract text
    extractor = TextExtractor()
    result = extractor.extract(file_path)
    
    text = result.get('text', '')
    print(f"📄 EXTRACTION METHOD: {result.get('extraction_method', 'unknown')}")
    print(f"📊 TEXT LENGTH: {len(text)} characters")
    print(f"📊 WORD COUNT: {result.get('word_count', 0)}")
    print(f"📊 QUALITY SCORE: {result.get('quality_score', 0):.2f}")
    print(f"\n{'='*80}")
    print("📝 FIRST 2000 CHARACTERS OF EXTRACTED TEXT:")
    print(f"{'='*80}\n")
    print(text[:2000])
    print(f"\n{'='*80}")
    
    # Section detection
    splitter = SectionSplitter()
    sections = splitter.split_sections(text)
    
    print(f"\n{'='*80}")
    print(f"🔍 DETECTED SECTIONS: {len(sections)}")
    print(f"{'='*80}\n")
    
    for section_name, section_text in sections.items():
        preview = section_text[:200].replace('\n', ' ')
        print(f"  ✓ {section_name.upper()}: {len(section_text)} chars")
        print(f"    Preview: {preview}...")
        print()
    
    # Check for common issues
    print(f"\n{'='*80}")
    print("⚠️  POTENTIAL ISSUES:")
    print(f"{'='*80}\n")
    
    if not sections.get('experience'):
        print("  ❌ No 'experience' section detected")
    if not sections.get('skills'):
        print("  ❌ No 'skills' section detected")
    if not sections.get('education'):
        print("  ❌ No 'education' section detected")
    
    # Check for name in first 5 lines
    lines = text.split('\n')[:5]
    print(f"\n  First 5 lines (for name detection):")
    for i, line in enumerate(lines, 1):
        print(f"    {i}. '{line.strip()}'")
    
    # Check for email
    import re
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    emails = re.findall(email_pattern, text)
    if emails:
        print(f"\n  ✓ Found emails: {emails}")
    else:
        print(f"\n  ❌ No email found")
    
    print(f"\n{'='*80}\n")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python debug_extraction.py <resume_file_path>")
        sys.exit(1)
    
    debug_extraction(sys.argv[1])
