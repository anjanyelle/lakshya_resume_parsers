#!/usr/bin/env python3
"""
Debug script to test section extraction on Krishnamurthy Sanjay resume
"""

import sys
import os

# Add ai-service to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ai-service'))

from parsers.text_extractor import TextExtractor
from parsers.section_splitter import SectionSplitter

def test_krishnamurthy_resume():
    """Test section extraction on Krishnamurthy Sanjay resume"""
    
    resume_path = "/Users/anjanyelle/Desktop/untitled folder 3/Lakshya-LLM-Resume-Parser/resumetestmodel/RESUMES_FILES 2/_Krishnamurthy_Sanjay.docx"
    
    print("\n" + "="*80)
    print("🧪 DEBUGGING KRISHNAMURTHY SANJAY RESUME")
    print("="*80)
    
    # Extract text
    extractor = TextExtractor()
    text = extractor.extract_from_docx(resume_path)
    
    print(f"\n📄 Raw text length: {len(text)} chars")
    
    # Find the TECHNICAL SKILLS and PROFESSIONAL EXPERIENCE headers
    skills_idx = text.find("TECHNICAL SKILLS")
    exp_idx = text.find("PROFESSIONAL EXPERIENCE")
    
    print(f"\n📍 Header positions:")
    print(f"   TECHNICAL SKILLS at: {skills_idx}")
    print(f"   PROFESSIONAL EXPERIENCE at: {exp_idx}")
    
    if skills_idx != -1 and exp_idx != -1:
        skills_section = text[skills_idx:exp_idx]
        print(f"\n📊 Content between headers: {len(skills_section)} chars")
        print(f"\n📝 First 500 chars of skills section:")
        print(skills_section[:500])
    
    # Split into sections
    splitter = SectionSplitter()
    sections = splitter.split_sections(text)
    
    print(f"\n\n{'='*80}")
    print("📊 SECTION EXTRACTION RESULTS")
    print(f"{'='*80}\n")
    
    for section_name, content in sections.items():
        if content and content.strip():
            print(f"📌 {section_name.upper()}: {len(content)} chars")
            print(f"   First 200 chars: {content[:200]}")
            print()

if __name__ == "__main__":
    test_krishnamurthy_resume()
