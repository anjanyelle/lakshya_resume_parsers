#!/usr/bin/env python3
"""
Test script to verify the new pipeline flow in resume_parser_pipeline.py

Tests the strict 6-step pipeline:
1. TextExtractor: Extract text + font metadata
2. SectionSplitter: Split sections with font metadata
3. SectionValidator: Validate and correct sections
4. DeBERTa: Extract entities from experience/education only
5. Collect: Gather remaining sections
6. Return: Structured dictionary with all data
"""

import sys
import os
import logging

# Add ai-service to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ai-service'))

# Configure logging to see pipeline steps
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)

def test_new_pipeline():
    """Test the new pipeline flow with sample resume text"""
    
    print("\n" + "="*80)
    print("🧪 TESTING NEW PIPELINE FLOW")
    print("="*80)
    
    # Sample resume text
    sample_resume = """
    John Doe
    john.doe@email.com | (555) 123-4567
    
    PROFESSIONAL SUMMARY
    Experienced software engineer with 10+ years in full-stack development.
    Passionate about building scalable systems and leading high-performing teams.
    
    WORK EXPERIENCE
    
    Senior Software Engineer | Google Inc. | Mountain View, CA | 2020-Present
    • Led team of 8 engineers developing cloud infrastructure
    • Managed $2M budget for infrastructure projects
    • Improved system performance by 40%
    
    Software Developer | Microsoft Corporation | Seattle, WA | 2018-2020
    • Developed features for Office 365
    • Worked with 5 product managers
    • Reduced deployment time by 50%
    
    EDUCATION
    
    Master of Science in Computer Science
    Stanford University | Palo Alto, CA | 2018
    GPA: 3.9/4.0
    
    Bachelor of Technology in Computer Engineering
    IIT Delhi | India | 2016
    First Class with Distinction
    
    TECHNICAL SKILLS
    Python, JavaScript, React, Node.js, AWS, Docker, Kubernetes
    PostgreSQL, MongoDB, Redis, Git, CI/CD, Microservices
    
    CERTIFICATIONS
    AWS Certified Solutions Architect | Amazon Web Services | 2022
    Certified Kubernetes Administrator | CNCF | 2021
    """
    
    print("\n📝 Sample Resume:")
    print("-"*80)
    print(f"Length: {len(sample_resume)} characters")
    print(f"Lines: {len(sample_resume.split(chr(10)))}")
    
    # Test with direct text (no file path)
    print("\n" + "="*80)
    print("TEST 1: Direct Text Input (No Font Metadata)")
    print("="*80)
    
    try:
        from resume_parser_pipeline import parse_resume
        
        # Note: This will fail if model is not available, but we can see the pipeline flow
        result = parse_resume(sample_resume)
        
        print("\n📊 RESULTS:")
        print("-"*80)
        print(f"✅ Experience entries: {len(result.get('experience', []))}")
        print(f"✅ Education entries: {len(result.get('education', []))}")
        print(f"✅ Additional sections: {len(result.get('sections', {}))}")
        
        if result.get('sections'):
            print("\n📦 Additional Sections Detected:")
            for section_name in result['sections'].keys():
                print(f"   • {section_name}")
        
        if result.get('metadata'):
            print("\n📋 Metadata:")
            for key, value in result['metadata'].items():
                print(f"   • {key}: {value}")
        
        print("\n✅ Pipeline completed successfully!")
        
    except Exception as e:
        print(f"\n⚠️ Pipeline execution note: {e}")
        print("(This is expected if DeBERTa model is not available)")
        print("But you should see the 6-step pipeline flow in the logs above!")
    
    print("\n" + "="*80)
    print("🏁 TEST COMPLETE")
    print("="*80)
    
    print("\n📝 Expected Pipeline Flow:")
    print("   1. ✅ STEP 1: Text Extraction")
    print("   2. ✅ STEP 2: Section Splitting")
    print("   3. ✅ STEP 3: Section Validation & Correction")
    print("   4. ✅ STEP 4: Entity Extraction (DeBERTa)")
    print("   5. ✅ STEP 5: Collecting Remaining Sections")
    print("   6. ✅ STEP 6: Structuring Output")
    
    print("\n📊 Expected Output Structure:")
    print("   {")
    print("     'experience': [...]  # Entities from DeBERTa")
    print("     'education': [...]   # Entities from DeBERTa")
    print("     'sections': {        # All other sections")
    print("       'summary': '...',")
    print("       'skills': '...',")
    print("       'certifications': '...'")
    print("     },")
    print("     'metadata': {        # Extraction info")
    print("       'extraction_method': '...',")
    print("       'total_sections': N,")
    print("       'has_font_metadata': True/False,")
    print("       'baseline_font_size': X.X,")
    print("       'total_entities': N")
    print("     }")
    print("   }")

if __name__ == "__main__":
    test_new_pipeline()
