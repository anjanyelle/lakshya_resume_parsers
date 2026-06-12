#!/usr/bin/env python3
"""
Debug script to test section extraction on AMAN KUMAR UJJAIN resume
"""

import sys
import os

# Add ai-service to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ai-service'))

from parsers.text_extractor import TextExtractor
from parsers.section_splitter import SectionSplitter

def test_aman_resume():
    """Test section extraction on AMAN KUMAR UJJAIN resume"""
    
    # Find the resume file
    test_dir = "/Users/anjanyelle/Desktop/untitled folder 3/Lakshya-LLM-Resume-Parser/resumetestmodel/RESUMES_FILES 2"
    
    import glob
    resume_files = glob.glob(os.path.join(test_dir, "*AMAN*.pdf"))
    
    if not resume_files:
        print("❌ AMAN resume not found")
        return
    
    resume_path = resume_files[0]
    
    print("\n" + "="*80)
    print("🧪 DEBUGGING AMAN KUMAR UJJAIN RESUME")
    print("="*80)
    print(f"📄 File: {os.path.basename(resume_path)}")
    
    # Extract text
    extractor = TextExtractor()
    text, _ = extractor.extract_with_font_metadata(resume_path)
    
    print(f"\n📊 Raw text length: {len(text)} chars")
    
    # Find key section headers
    headers = [
        "PROFESSIONAL SUMMARY",
        "TECHNICAL SKILLS",
        "PROFESSIONAL EXPERIENCE",
        "PROJECTS",
        "EDUCATION",
        "SOFT SKILLS",
        "CERTIFICATIONS"
    ]
    
    print(f"\n📍 Header positions:")
    for header in headers:
        idx = text.find(header)
        if idx != -1:
            print(f"   ✅ {header}: position {idx}")
            # Show context around header
            start = max(0, idx - 50)
            end = min(len(text), idx + len(header) + 50)
            context = text[start:end].replace('\n', '\\n')
            print(f"      Context: ...{context}...")
        else:
            print(f"   ❌ {header}: NOT FOUND")
    
    # Split into sections
    print(f"\n\n{'='*80}")
    print("📊 SECTION EXTRACTION RESULTS")
    print(f"{'='*80}\n")
    
    splitter = SectionSplitter()
    sections = splitter.split_sections(text)
    
    for section_name, content in sections.items():
        if content and content.strip():
            print(f"📌 {section_name.upper()}: {len(content)} chars")
            print(f"   First 150 chars: {content[:150].replace(chr(10), ' ')}")
            print()

if __name__ == "__main__":
    test_aman_resume()
