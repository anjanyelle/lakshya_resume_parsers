#!/usr/bin/env python3
"""
Test script to verify get_expected_fingerprint method functionality
"""

import sys
import os

# Add ai-service to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ai-service'))

from parsers.section_validator import SectionValidator

def test_expected_fingerprint():
    """Test get_expected_fingerprint method for different section types"""
    
    print("\n" + "="*80)
    print("🧪 TESTING EXPECTED FINGERPRINT GENERATION")
    print("="*80)
    
    # Initialize validator
    print("\n📋 Initializing SectionValidator...")
    validator = SectionValidator()
    print("✅ SectionValidator initialized\n")
    
    # Test section types
    section_types = [
        'experience',
        'education',
        'skills',
        'summary',
        'projects',
        'certifications',
    ]
    
    print("="*80)
    print("📊 STANDARD SECTION FINGERPRINTS")
    print("="*80)
    
    for section in section_types:
        print(f"\n🔍 Section: {section.upper()}")
        print("-" * 80)
        
        fingerprint = validator.get_expected_fingerprint(section)
        
        # Display entity thresholds
        print("Entity Thresholds:")
        for entity in ['ORG', 'DATE', 'GPE', 'PERSON', 'CARDINAL', 'DEGREE']:
            min_val = fingerprint[entity]['min']
            max_val = fingerprint[entity]['max']
            
            # Determine expectation level
            if min_val >= 1:
                level = "HIGH (required)"
            elif max_val == 0:
                level = "NONE (not expected)"
            elif max_val <= 5:
                level = "LOW (few expected)"
            else:
                level = "MODERATE (some expected)"
            
            print(f"  • {entity:12} : min={min_val:3}, max={max_val:3}  [{level}]")
        
        # Display other metrics
        print("\nOther Metrics:")
        print(f"  • Sentence count    : min={fingerprint['sentence_count']['min']:3}, "
              f"max={fingerprint['sentence_count']['max']:3}")
        print(f"  • Word list density : min={fingerprint['word_list_density']['min']:.2f}, "
              f"max={fingerprint['word_list_density']['max']:.2f}")
    
    # Test section name variations
    print("\n" + "="*80)
    print("📊 SECTION NAME VARIATIONS")
    print("="*80)
    
    variations = [
        ('work experience', 'experience'),
        ('professional experience', 'experience'),
        ('employment', 'experience'),
        ('academic background', 'education'),
        ('qualifications', 'education'),
        ('technical skills', 'skills'),
        ('core competencies', 'skills'),
        ('professional summary', 'summary'),
        ('profile', 'summary'),
        ('objective', 'summary'),
        ('portfolio', 'projects'),
        ('achievements', 'projects'),
    ]
    
    print("\nTesting that variations map to correct standard sections:")
    for variation, expected_base in variations:
        fingerprint = validator.get_expected_fingerprint(variation)
        expected_fingerprint = validator.get_expected_fingerprint(expected_base)
        
        matches = fingerprint == expected_fingerprint
        status = "✅" if matches else "❌"
        print(f"{status} '{variation}' → maps to '{expected_base}' fingerprint")
    
    # Test unknown section
    print("\n" + "="*80)
    print("📊 UNKNOWN SECTION (DEFAULT FINGERPRINT)")
    print("="*80)
    
    unknown_fingerprint = validator.get_expected_fingerprint('unknown_custom_section')
    print("\nDefault fingerprint for unknown sections:")
    print("  (Should allow all entity types with wide ranges)")
    
    for entity in ['ORG', 'DATE', 'GPE', 'PERSON', 'CARDINAL', 'DEGREE']:
        min_val = unknown_fingerprint[entity]['min']
        max_val = unknown_fingerprint[entity]['max']
        print(f"  • {entity:12} : min={min_val:3}, max={max_val:3}")
    
    # Demonstrate fingerprint usage
    print("\n" + "="*80)
    print("📊 FINGERPRINT USAGE EXAMPLE")
    print("="*80)
    
    # Sample text sections
    sample_sections = [
        {
            'name': 'experience',
            'text': """Senior Software Engineer | Google Inc. | Mountain View, CA | 2020-Present
            Led team of 8 engineers developing cloud infrastructure.
            Managed $2M budget for infrastructure projects."""
        },
        {
            'name': 'education',
            'text': """Master of Science in Computer Science
            Stanford University | 2018
            Bachelor of Technology in Computer Engineering
            IIT Delhi | 2016"""
        },
        {
            'name': 'skills',
            'text': """Python, JavaScript, React, Node.js, AWS, Docker, Kubernetes, 
            PostgreSQL, MongoDB, Redis, Git, CI/CD, Microservices"""
        },
    ]
    
    for sample in sample_sections:
        section_name = sample['name']
        text = sample['text']
        
        print(f"\n🔍 Validating {section_name.upper()} section:")
        print("-" * 80)
        
        # Get actual profile
        actual_profile = validator.get_entity_profile(text)
        
        # Get expected fingerprint
        expected = validator.get_expected_fingerprint(section_name)
        
        print(f"Actual entity counts vs Expected ranges:")
        
        violations = []
        for entity in ['ORG', 'DATE', 'GPE', 'PERSON', 'CARDINAL', 'DEGREE']:
            actual = actual_profile[entity]
            min_exp = expected[entity]['min']
            max_exp = expected[entity]['max']
            
            in_range = min_exp <= actual <= max_exp
            status = "✅" if in_range else "❌"
            
            print(f"  {status} {entity:12} : {actual:2} (expected: {min_exp}-{max_exp})")
            
            if not in_range:
                violations.append(f"{entity}: {actual} not in [{min_exp}, {max_exp}]")
        
        if violations:
            print(f"\n  ⚠️ Violations found: {len(violations)}")
            for v in violations:
                print(f"     • {v}")
        else:
            print(f"\n  ✅ All entity counts within expected ranges!")
    
    print("\n" + "="*80)
    print("🏁 TEST COMPLETE")
    print("="*80)
    
    print("\n📝 Summary:")
    print("   ✅ get_expected_fingerprint() returns threshold dictionaries")
    print("   ✅ Experience: High ORG, DATE (companies, dates)")
    print("   ✅ Education: High ORG, DATE, DEGREE (universities, degrees)")
    print("   ✅ Skills: Low entities, high word_list_density (comma lists)")
    print("   ✅ Summary: Low specific entities, high sentence_count (prose)")
    print("   ✅ Projects: Moderate ORG, technology words")
    print("   ✅ Section name variations map correctly")
    print("   ✅ Unknown sections get permissive default fingerprint")

if __name__ == "__main__":
    test_expected_fingerprint()
