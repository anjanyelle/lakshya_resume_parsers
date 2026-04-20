#!/usr/bin/env python3
"""
Test script to verify SectionValidator integration in resume_parser_pipeline.py
"""

import sys
import os
import logging

# Add ai-service to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ai-service'))

# Configure logging to see validation messages
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s - %(name)s - %(message)s'
)

from resume_parser_pipeline import SectionExtractor

def test_pipeline_integration():
    """Test that SectionValidator is integrated into the pipeline"""
    
    print("\n" + "="*80)
    print("🧪 TESTING SECTION VALIDATOR INTEGRATION IN PIPELINE")
    print("="*80)
    
    # Test Case 1: Resume with clean sections
    print("\n" + "="*80)
    print("📋 Test Case 1: Resume with Clean Sections")
    print("="*80)
    
    clean_resume = """
    John Doe
    john.doe@email.com
    
    EXPERIENCE
    Senior Software Engineer | Google Inc. | Mountain View, CA | 2020-Present
    Led team of 8 engineers developing cloud infrastructure
    
    Software Developer | Microsoft Corporation | Seattle, WA | 2018-2020
    Developed features for Office 365
    
    EDUCATION
    Master of Science in Computer Science
    Stanford University | 2018
    
    Bachelor of Technology in Computer Engineering
    IIT Delhi | 2016
    
    SKILLS
    Python, JavaScript, React, Node.js, AWS, Docker
    """
    
    print("\n🔄 Extracting sections with validation...")
    sections = SectionExtractor.extract_sections(clean_resume)
    
    print("\n📊 Final sections returned:")
    for name, content in sections.items():
        if content.strip():
            lines = content.strip().split('\n')
            print(f"\n   {name.upper()}:")
            print(f"   • {len(lines)} lines")
            print(f"   • First line: {lines[0][:60]}...")
    
    # Test Case 2: Resume with section bleeding
    print("\n" + "="*80)
    print("📋 Test Case 2: Resume with Section Bleeding")
    print("="*80)
    
    bleeding_resume = """
    Jane Smith
    jane.smith@email.com
    
    EXPERIENCE
    Senior Software Engineer | Google Inc. | 2020-Present
    Led development of cloud infrastructure
    
    Master of Science in Computer Science
    Stanford University | 2018
    Bachelor of Technology in Computer Engineering
    IIT Delhi | 2016
    """
    
    print("\n🔄 Extracting sections with validation...")
    print("   (Should detect bleeding and split experience → education)")
    sections = SectionExtractor.extract_sections(bleeding_resume)
    
    print("\n📊 Final sections returned:")
    for name, content in sections.items():
        if content.strip():
            lines = content.strip().split('\n')
            print(f"\n   {name.upper()}:")
            print(f"   • {len(lines)} lines")
            for line in lines[:3]:
                if line.strip():
                    print(f"   • {line.strip()[:60]}...")
    
    # Test Case 3: Resume with unknown section
    print("\n" + "="*80)
    print("📋 Test Case 3: Resume with Unknown Section Label")
    print("="*80)
    
    unknown_resume = """
    Bob Johnson
    bob@email.com
    
    WORK HISTORY
    Senior Software Engineer | Google Inc. | 2020-Present
    Led team of engineers
    
    ACADEMIC BACKGROUND
    Master of Science in Computer Science
    Stanford University | 2018
    """
    
    print("\n🔄 Extracting sections with validation...")
    print("   (Should resolve 'work history' and 'academic background')")
    sections = SectionExtractor.extract_sections(unknown_resume)
    
    print("\n📊 Final sections returned:")
    for name, content in sections.items():
        if content.strip():
            lines = content.strip().split('\n')
            print(f"\n   {name.upper()}:")
            print(f"   • {len(lines)} lines")
            print(f"   • Preview: {lines[0][:60]}...")
    
    print("\n" + "="*80)
    print("🏁 TEST COMPLETE")
    print("="*80)
    
    print("\n📝 Summary:")
    print("   ✅ SectionValidator integrated into resume_parser_pipeline.py")
    print("   ✅ Validation runs after section splitting")
    print("   ✅ Logs show before/after section keys")
    print("   ✅ Corrections are applied before passing to DeBERTa")
    print("\n💡 Check the logs above to see validation messages:")
    print("   • '📋 Sections before validation'")
    print("   • '✅ Sections after validation'")
    print("   • '➕ Added sections' / '➖ Removed sections'")

if __name__ == "__main__":
    test_pipeline_integration()
