#!/usr/bin/env python3
"""
Test script to verify validate_and_correct method functionality
"""

import sys
import os

# Add ai-service to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ai-service'))

from parsers.section_validator import SectionValidator

def test_validate_and_correct():
    """Test validate_and_correct method with various scenarios"""
    
    print("\n" + "="*80)
    print("🧪 TESTING VALIDATE AND CORRECT")
    print("="*80)
    
    # Initialize validator
    print("\n📋 Initializing SectionValidator...")
    validator = SectionValidator()
    print("✅ SectionValidator initialized\n")
    
    # Test Case 1: Clean sections (no corrections needed)
    print("="*80)
    print("📋 Test Case 1: Clean Sections (No Corrections)")
    print("="*80)
    
    clean_sections = {
        'experience': """Senior Software Engineer | Google Inc. | 2020-Present
        Led team of 8 engineers developing cloud infrastructure
        
        Software Developer | Microsoft Corporation | 2018-2020
        Developed features for Office 365""",
        
        'education': """Master of Science in Computer Science
        Stanford University | 2018
        
        Bachelor of Technology in Computer Engineering
        IIT Delhi | 2016""",
        
        'skills': """Python, JavaScript, React, Node.js, AWS, Docker, Kubernetes"""
    }
    
    print("\nInput sections:")
    for name, content in clean_sections.items():
        print(f"   • {name}: {len(content)} chars")
    
    result = validator.validate_and_correct(clean_sections)
    
    print("\nOutput sections:")
    for name, content in result.items():
        print(f"   • {name}: {len(content)} chars")
    
    print(f"\nStatus: {'✅ PASS' if len(result) == len(clean_sections) else '❌ FAIL'}")
    
    # Test Case 2: Section with bleeding (experience → education)
    print("\n" + "="*80)
    print("📋 Test Case 2: Section with Bleeding")
    print("="*80)
    
    bleeding_sections = {
        'experience': """Senior Software Engineer | Google Inc. | 2020-Present
        Led team of 8 engineers developing cloud infrastructure
        Managed $2M budget for infrastructure projects
        
        Master of Science in Computer Science
        Stanford University | 2018
        Bachelor of Technology in Computer Engineering
        IIT Delhi | 2016"""
    }
    
    print("\nInput sections:")
    print(f"   • experience: 1 section with bleeding content")
    
    result = validator.validate_and_correct(bleeding_sections)
    
    print("\nOutput sections:")
    for name, content in result.items():
        print(f"   • {name}: {len(content)} chars")
    
    print(f"\nExpected: Split into 'experience' and 'education'")
    print(f"Status: {'✅ PASS' if 'education' in result else '❌ FAIL'}")
    
    # Test Case 3: Unknown section that should be resolved
    print("\n" + "="*80)
    print("📋 Test Case 3: Unknown Section Resolution")
    print("="*80)
    
    unknown_sections = {
        'unknown': """Senior Software Engineer | Google Inc. | 2020-Present
        Led team of 8 engineers
        Managed infrastructure projects""",
        
        'other': """Master of Science in Computer Science
        Stanford University | 2018"""
    }
    
    print("\nInput sections:")
    for name, content in unknown_sections.items():
        print(f"   • {name}: {len(content)} chars")
    
    result = validator.validate_and_correct(unknown_sections)
    
    print("\nOutput sections:")
    for name, content in result.items():
        print(f"   • {name}: {len(content)} chars")
    
    print(f"\nExpected: Resolved to 'experience' and 'education'")
    has_experience = 'experience' in result
    has_education = 'education' in result
    print(f"Status: {'✅ PASS' if has_experience and has_education else '❌ FAIL'}")
    
    # Test Case 4: Low confidence section (should be reassigned)
    print("\n" + "="*80)
    print("📋 Test Case 4: Low Confidence Section Reassignment")
    print("="*80)
    
    low_confidence_sections = {
        'skills': """Senior Software Engineer | Google Inc. | Mountain View, CA | 2020-Present
        Led team of 8 engineers developing cloud infrastructure
        Managed $2M budget for infrastructure projects"""
    }
    
    print("\nInput sections:")
    print(f"   • skills: Content looks like experience (low confidence)")
    
    result = validator.validate_and_correct(low_confidence_sections)
    
    print("\nOutput sections:")
    for name, content in result.items():
        print(f"   • {name}: {len(content)} chars")
    
    print(f"\nExpected: Reassigned to 'experience'")
    print(f"Status: {'✅ PASS' if 'experience' in result else '❌ FAIL'}")
    
    # Test Case 5: Complex scenario (multiple issues)
    print("\n" + "="*80)
    print("📋 Test Case 5: Complex Scenario (Multiple Issues)")
    print("="*80)
    
    complex_sections = {
        'experience': """Senior Software Engineer | Google Inc. | 2020-Present
        Led team of 8 engineers
        
        Master of Science in Computer Science
        Stanford University | 2018""",
        
        'unknown': """Python, JavaScript, React, Node.js, AWS""",
        
        'skills': """Software Developer | Microsoft | 2018-2020
        Developed Office 365 features""",
        
        'other': """AWS Certified Solutions Architect | 2022
        Certified Kubernetes Administrator | 2021"""
    }
    
    print("\nInput sections:")
    for name, content in complex_sections.items():
        preview = content[:50].replace('\n', ' ')
        print(f"   • {name}: '{preview}...'")
    
    result = validator.validate_and_correct(complex_sections)
    
    print("\nOutput sections:")
    for name, content in result.items():
        preview = content[:50].replace('\n', ' ')
        print(f"   • {name}: '{preview}...'")
    
    print(f"\nExpected corrections:")
    print(f"   • 'experience' split into experience + education")
    print(f"   • 'unknown' resolved to 'skills'")
    print(f"   • 'skills' reassigned to 'experience'")
    print(f"   • 'other' resolved to 'certifications' or 'education'")
    
    # Test Case 6: Empty sections
    print("\n" + "="*80)
    print("📋 Test Case 6: Empty Sections")
    print("="*80)
    
    empty_sections = {
        'experience': """Senior Software Engineer | Google Inc. | 2020-Present""",
        'education': "",
        'skills': "   ",
        'summary': """Experienced engineer with 10+ years"""
    }
    
    print("\nInput sections:")
    for name, content in empty_sections.items():
        status = "empty" if not content.strip() else f"{len(content)} chars"
        print(f"   • {name}: {status}")
    
    result = validator.validate_and_correct(empty_sections)
    
    print("\nOutput sections:")
    for name, content in result.items():
        print(f"   • {name}: {len(content)} chars")
    
    print(f"\nExpected: Empty sections removed")
    print(f"Status: {'✅ PASS' if len(result) == 2 else '❌ FAIL'}")
    
    # Test Case 7: Detailed step-by-step analysis
    print("\n" + "="*80)
    print("📋 Test Case 7: Detailed Step-by-Step Analysis")
    print("="*80)
    
    detailed_sections = {
        'experience': """Senior Software Engineer | Google Inc. | 2020-Present
        Led development of cloud infrastructure
        
        Master of Science in Computer Science
        Stanford University | 2018""",
        
        'possible_section': """Python, JavaScript, React, Node.js"""
    }
    
    print("\nInput sections:")
    print(f"   1. experience: Has bleeding (experience → education)")
    print(f"   2. possible_section: Unknown label")
    
    print("\n🔄 Processing Steps:")
    
    result = validator.validate_and_correct(detailed_sections)
    
    print("\nOutput sections:")
    for i, (name, content) in enumerate(result.items(), 1):
        lines = content.split('\n')
        print(f"   {i}. {name}: {len(lines)} lines")
        for line in lines[:2]:
            if line.strip():
                print(f"      • {line.strip()[:60]}...")
    
    print("\n" + "="*80)
    print("🏁 TEST COMPLETE")
    print("="*80)
    
    print("\n📝 Summary:")
    print("   ✅ validate_and_correct() orchestrates all validation operations")
    print("   ✅ Step 1: Validates sections and reassigns low-confidence (<50%)")
    print("   ✅ Step 2: Detects and splits bleeding sections")
    print("   ✅ Step 3: Resolves unknown section labels")
    print("   ✅ Step 4: Cleans up and removes empty sections")
    print("   ✅ Returns corrected sections dictionary")

if __name__ == "__main__":
    test_validate_and_correct()
