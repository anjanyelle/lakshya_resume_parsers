#!/usr/bin/env python3
"""Test extraction from Karthik's PDF to diagnose text loss."""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from parsers.text_extractor import TextExtractor

pdf_path = "/Users/anjanyelle/Desktop/untitled folder 3/Lakshya-LLM-Resume-Parser/backend/src/uploads/c7776cd9-4ecb-4a35-9b95-63a5af4c7994_Untitled_document-6.pdf"

print("🔍 Testing PDF Text Extraction")
print("=" * 70)

extractor = TextExtractor()
text = extractor.extract_from_pdf(pdf_path)

print(f"\n Character Count: {len(text)}")

print("\n📝 Extracted Text:")
print("=" * 70)
print(text)
print("=" * 70)

print(f"\n📏 Text Length: {len(text)} characters")
print(f"📝 Word Count: {len(text.split())}")

# Check for work experience keywords
work_keywords = ['experience', 'developer', 'engineer', 'company', 'project', 'client']
found_keywords = [kw for kw in work_keywords if kw.lower() in text.lower()]
print(f"\n🔍 Work Experience Keywords Found: {found_keywords}")

# Check if text contains structured sections
if 'experience' in text.lower():
    print("✅ Contains 'experience' keyword")
else:
    print("❌ Missing 'experience' keyword")

print("\n✅ Test complete")
