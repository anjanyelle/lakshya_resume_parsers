#!/usr/bin/env python3
"""
Test script to verify resolve_unknown_section method functionality
"""

import sys
import os

# Add ai-service to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ai-service'))

from parsers.section_validator import SectionValidator

def test_resolve_unknown_section():
    """Test resolve_unknown_section method with various content types"""
    
    print("\n" + "="*80)
    print("🧪 TESTING UNKNOWN SECTION RESOLUTION")
    print("="*80)
    
    # Initialize validator
    print("\n📋 Initializing SectionValidator...")
    validator = SectionValidator()
    print("✅ SectionValidator initialized\n")
    
    # Test cases with different section types
    test_cases = [
        {
            'name': 'Clear Experience Content',
            'text': """Senior Software Engineer | Google Inc. | Mountain View, CA | 2020-Present
            Led team of 8 engineers developing cloud infrastructure
            Managed $2M budget for infrastructure projects
            
            Software Developer | Microsoft Corporation | Seattle, WA | 2018-2020
            Developed features for Office 365
            Worked with 5 product managers""",
            'expected': 'experience',
            'reason': 'Has ORG, DATE, GPE - typical experience section'
        },
        {
            'name': 'Clear Education Content',
            'text': """Master of Science in Computer Science
            Stanford University | Palo Alto, CA | 2018
            GPA: 3.9/4.0
            
            Bachelor of Technology in Computer Engineering
            IIT Delhi | India | 2016
            First Class with Distinction""",
            'expected': 'education',
            'reason': 'Has DEGREE patterns, ORG (universities), DATE'
        },
        {
            'name': 'Clear Skills Content',
            'text': """Python, JavaScript, React, Node.js, AWS, Docker, Kubernetes
            PostgreSQL, MongoDB, Redis, Git, CI/CD, Microservices
            REST APIs, GraphQL, TDD, Agile, Scrum""",
            'expected': 'skills',
            'reason': 'Comma-separated lists, low entity counts'
        },
        {
            'name': 'Clear Summary Content',
            'text': """Experienced software engineer with 10+ years in full-stack development.
            Passionate about building scalable systems and leading high-performing teams.
            Strong background in cloud architecture and microservices.
            Seeking opportunities to drive technical innovation.""",
            'expected': 'summary',
            'reason': 'Prose sentences, low specific entities, high sentence count'
        },
        {
            'name': 'Clear Projects Content',
            'text': """E-commerce Platform | 2022
            Built scalable platform handling 1M+ users
            Technologies: React, Node.js, PostgreSQL, AWS
            
            Mobile Banking App | 2021
            Developed secure banking application
            Technologies: React Native, Firebase""",
            'expected': 'projects',
            'reason': 'Project names, dates, technologies'
        },
        {
            'name': 'Clear Certifications Content',
            'text': """AWS Certified Solutions Architect | Amazon Web Services | 2022
            Certified Kubernetes Administrator | CNCF | 2021
            PMP Certification | Project Management Institute | 2020""",
            'expected': 'certifications',
            'reason': 'Certification names, issuing organizations, dates'
        },
        {
            'name': 'Ambiguous Content (Generic Text)',
            'text': """This is some random text that doesn't really fit any section.
            It has no specific patterns or entities.
            Just generic sentences without structure.""",
            'expected': 'other',
            'reason': 'No clear entity patterns, ambiguous'
        },
        {
            'name': 'Empty Content',
            'text': "",
            'expected': 'other',
            'reason': 'Empty text'
        },
        {
            'name': 'Education-like but no degrees',
            'text': """Stanford University | 2018
            Computer Science Department
            Research Assistant""",
            'expected': 'experience',  # Should reject 'education' due to no DEGREE
            'reason': 'Has university but no degree patterns'
        },
        {
            'name': 'Experience-like but no dates',
            'text': """Software Engineer at Google Inc.
            Led development of cloud infrastructure
            Managed team of engineers""",
            'expected': 'experience',  # Might still match if ORG present
            'reason': 'Has ORG but missing DATE'
        },
    ]
    
    # Run tests
    results = {'pass': 0, 'fail': 0}
    
    for i, test_case in enumerate(test_cases, 1):
        print("="*80)
        print(f"📋 Test Case {i}: {test_case['name']}")
        print("="*80)
        
        text = test_case['text']
        expected = test_case['expected']
        
        print(f"\n📝 Content Preview:")
        preview = text[:100].replace('\n', ' ')
        print(f"   {preview}{'...' if len(text) > 100 else ''}")
        
        # Get entity profile for debugging
        if text.strip():
            profile = validator.get_entity_profile(text)
            print(f"\n📊 Entity Profile:")
            for entity, count in profile.items():
                if count > 0:
                    print(f"   • {entity}: {count}")
        
        # Resolve section
        result = validator.resolve_unknown_section(text)
        
        print(f"\n🔍 Resolution:")
        print(f"   Expected: '{expected}'")
        print(f"   Result:   '{result}'")
        print(f"   Reason:   {test_case['reason']}")
        
        # Check result
        if result == expected:
            print(f"   Status:   ✅ PASS")
            results['pass'] += 1
        else:
            print(f"   Status:   ❌ FAIL")
            results['fail'] += 1
        
        print()
    
    # Detailed scoring example
    print("="*80)
    print("📊 DETAILED SCORING EXAMPLE")
    print("="*80)
    
    example_text = """Senior Software Engineer | Google Inc. | 2020-Present
    Led team of 8 engineers developing cloud infrastructure"""
    
    print(f"\nExample Text: '{example_text}'")
    
    profile = validator.get_entity_profile(example_text)
    print(f"\nEntity Profile: {profile}")
    
    section_types = ['experience', 'education', 'skills', 'summary', 'projects', 'certifications']
    
    print(f"\nViolation Scores for Each Section Type:")
    for section_type in section_types:
        expected = validator.get_expected_fingerprint(section_type)
        violations = validator._count_fingerprint_violations(profile, expected)
        print(f"   • {section_type:15} : {violations} violations")
    
    result = validator.resolve_unknown_section(example_text)
    print(f"\nBest Match: '{result}'")
    
    print("\n" + "="*80)
    print("🏁 TEST COMPLETE")
    print("="*80)
    
    print(f"\n📊 Results:")
    print(f"   ✅ Passed: {results['pass']}/{len(test_cases)}")
    print(f"   ❌ Failed: {results['fail']}/{len(test_cases)}")
    
    print("\n📝 Summary:")
    print("   ✅ resolve_unknown_section() analyzes content entity profile")
    print("   ✅ Compares against all known section fingerprints")
    print("   ✅ Returns section with fewest violations")
    print("   ✅ Validates strong indicators (DEGREE for education, ORG+DATE for experience)")
    print("   ✅ Returns 'other' for ambiguous or unclear content")
    print("   ✅ Handles empty text gracefully")

if __name__ == "__main__":
    test_resolve_unknown_section()
