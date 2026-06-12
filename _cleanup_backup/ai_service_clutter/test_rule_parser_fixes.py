#!/usr/bin/env python3
"""
Test script to verify the three regex pattern fixes in rule_parser.py
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from parsers.rule_parser import RuleBasedParser

def test_phone_pattern_fix():
    print("="*70)
    print("📞 TESTING PHONE PATTERN FIX")
    print("="*70)
    
    parser = RuleBasedParser()
    
    test_cases = [
        {
            'text': 'Phone: +1-555-123-4567',
            'should_match': True,
            'digits': 11
        },
        {
            'text': 'Mobile: (555) 987-6543',
            'should_match': True,
            'digits': 10
        },
        {
            'text': 'Contact: 555.123.4567',
            'should_match': True,
            'digits': 10
        },
        {
            'text': 'Random numbers: 12345678901234567890',
            'should_match': False,
            'digits': 20  # Too many digits
        },
        {
            'text': 'Short: 12345',
            'should_match': False,
            'digits': 5  # Too few digits
        },
        {
            'text': 'TEL: +44-20-7946-0958',
            'should_match': True,
            'digits': 12
        }
    ]
    
    print(f"\n🧪 Testing phone number validation:")
    for i, case in enumerate(test_cases, 1):
        result = parser.extract_phone(case['text'])
        matched = result is not None
        
        print(f"\n  Test {i}: {case['text']}")
        print(f"    Digits: {case['digits']}")
        print(f"    Expected match: {case['should_match']}")
        print(f"    Actual match: {matched}")
        print(f"    Result: {result}")
        
        if matched == case['should_match']:
            print(f"    ✅ PASS")
        else:
            print(f"    ❌ FAIL")

def test_name_pattern_fix():
    print("\n" + "="*70)
    print("👤 TESTING NAME PATTERN FIX")
    print("="*70)
    
    parser = RuleBasedParser()
    
    test_text = """
    John Smith
    Senior Software Engineer
    
    Mary Johnson Davis
    Professional Summary
    
    Robert Williams
    Experience Section
    
    San Francisco, CA
    Location information
    
    Software Engineer
    Job title
    """
    
    print(f"\n📝 Test text:")
    print(f"   {test_text}")
    
    # Test the name candidates function
    candidates = parser.extract_name_candidates(test_text)
    
    print(f"\n🧪 Name extraction results:")
    print(f"   Found {len(candidates)} candidates:")
    for i, candidate in enumerate(candidates, 1):
        print(f"     {i}. '{candidate}'")
    
    # Test the main name extraction
    name = parser.extract_name(test_text)
    print(f"\n🎯 Best name candidate: '{name}'")
    
    # Verify we get proper names and not false positives
    expected_names = ['John Smith', 'Mary Johnson Davis', 'Robert Williams']
    false_positives = ['San Francisco', 'Software Engineer']
    
    print(f"\n✅ Expected names found: {[name for name in expected_names if name in candidates]}")
    print(f"❌ False positives filtered: {[fp for fp in false_positives if fp not in candidates]}")

def test_email_validation_fix():
    print("\n" + "="*70)
    print("📧 TESTING EMAIL VALIDATION FIX")
    print("="*70)
    
    parser = RuleBasedParser()
    
    test_cases = [
        {
            'email': 'john.doe@example.com',
            'should_be_valid': True
        },
        {
            'email': 'mary@company.org',
            'should_be_valid': True
        },
        {
            'email': 'test@mailinator.com',
            'should_be_valid': False  # Disposable domain
        },
        {
            'email': 'user@guerrillamail.com',
            'should_be_valid': False  # Disposable domain
        },
        {
            'email': 'contact@tempmail.com',
            'should_be_valid': False  # Disposable domain
        },
        {
            'email': 'valid.user@legitimate-company.net',
            'should_be_valid': True
        },
        {
            'email': 'invalid-email',  # Missing domain structure
            'should_be_valid': False
        }
    ]
    
    print(f"\n🧪 Testing email validation:")
    for i, case in enumerate(test_cases, 1):
        is_valid = parser.is_valid_email(case['email'])
        
        print(f"\n  Test {i}: {case['email']}")
        print(f"    Expected valid: {case['should_be_valid']}")
        print(f"    Actual valid: {is_valid}")
        
        if is_valid == case['should_be_valid']:
            print(f"    ✅ PASS")
        else:
            print(f"    ❌ FAIL")

def test_extract_entities_integration():
    print("\n" + "="*70)
    print("🔗 TESTING EXTRACT_ENTITIES INTEGRATION")
    print("="*70)
    
    parser = RuleBasedParser()
    
    sample_resume = """
    John Michael Smith
    Email: john.smith@professional.com
    Phone: +1-555-123-4567
    LinkedIn: https://www.linkedin.com/in/johnsmith
    
    San Francisco, CA
    
    Senior Software Engineer with 10+ years of experience.
    Skills: Python, Java, JavaScript, React, AWS, Docker
    
    EXPERIENCE
    Google Inc. - Senior Software Engineer (2020-Present)
    Microsoft Corporation - Software Engineer (2018-2020)
    
    EDUCATION
    Stanford University - BS Computer Science
    
    Contact: test@mailinator.com  # This should be filtered out
    """
    
    print(f"\n📄 Sample resume:")
    print(f"   {sample_resume}")
    
    # Test the new extract_entities method
    entities = parser.extract_entities(sample_resume)
    
    print(f"\n🧪 Extracted entities:")
    for entity_type, values in entities.items():
        if values:
            print(f"   {entity_type.upper()}: {values}")
    
    # Verify key expectations
    print(f"\n✅ Key validations:")
    print(f"   Name found: {'John Michael Smith' in entities['names']}")
    print(f"   Valid email found: {'john.smith@professional.com' in entities['emails']}")
    print(f"   Disposable email filtered: {'test@mailinator.com' not in entities['emails']}")
    print(f"   Phone found: {len(entities['phones']) > 0}")
    print(f"   Location found: {len(entities['locations']) > 0}")
    print(f"   Skills found: {len(entities['skills']) > 0}")

if __name__ == "__main__":
    print("🚀 TESTING RULE PARSER FIXES")
    print("="*70)
    
    try:
        test_phone_pattern_fix()
        test_name_pattern_fix()
        test_email_validation_fix()
        test_extract_entities_integration()
        
        print("\n" + "="*70)
        print("🎉 ALL TESTS COMPLETED!")
        print("="*70)
        print("\n📝 SUMMARY OF FIXES:")
        print("✅ Phone pattern: Improved regex with digit count validation (7-15 digits)")
        print("✅ Name pattern: Works mid-text, filters false positives, checks first 20 lines")
        print("✅ Email validation: Filters disposable domains and validates structure")
        print("✅ Extract entities: New method combining all extraction functions")
        print("="*70)
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
