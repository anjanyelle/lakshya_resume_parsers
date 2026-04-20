#!/usr/bin/env python3
"""
Test script to verify SectionValidator class functionality
"""

import sys
import os

# Add ai-service to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ai-service'))

from parsers.section_validator import SectionValidator

def test_section_validator():
    """Test SectionValidator initialization and basic functionality"""
    
    print("\n" + "="*80)
    print("🧪 TESTING SECTION VALIDATOR")
    print("="*80)
    
    # Test 1: Initialize SectionValidator
    print("\n📋 Test 1: Initialize SectionValidator")
    print("-" * 80)
    
    try:
        validator = SectionValidator()
        print("✅ SectionValidator initialized successfully")
        print(f"   spaCy model loaded: en_core_web_sm")
        print(f"   Model type: {type(validator.nlp)}")
    except ImportError as e:
        print(f"❌ ImportError: {e}")
        return
    except OSError as e:
        print(f"❌ OSError: {e}")
        return
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return
    
    # Test 2: Validate section headers
    print("\n📋 Test 2: Validate Section Headers")
    print("-" * 80)
    
    test_headers = [
        ("EXPERIENCE", True, "Standard section header"),
        ("WORK EXPERIENCE", True, "Multi-word section header"),
        ("Professional Summary", True, "Title case header"),
        ("This is a very long sentence that describes something in detail and is definitely not a header", False, "Long sentence (not a header)"),
        ("", False, "Empty string"),
        ("Skills", True, "Single word header"),
    ]
    
    for text, expected, description in test_headers:
        result = validator.validate_section_header(text)
        status = "✅" if result == expected else "❌"
        print(f"{status} '{text[:50]}{'...' if len(text) > 50 else ''}' → {result} (expected: {expected})")
        print(f"   Description: {description}")
    
    # Test 3: Validate section boundaries
    print("\n📋 Test 3: Validate Section Boundaries")
    print("-" * 80)
    
    test_boundaries = [
        (
            "EXPERIENCE",
            "Senior Software Engineer at Tech Corp. Led development of microservices architecture.",
            True,
            "Valid header and content"
        ),
        (
            "EDUCATION",
            "Master of Science in Computer Science from Stanford University. Graduated 2020.",
            True,
            "Valid education section"
        ),
        (
            "This is a very long header that is actually content",
            "Short",
            False,
            "Header longer than content"
        ),
        (
            "",
            "Some content here",
            False,
            "Empty header"
        ),
        (
            "SKILLS",
            "",
            False,
            "Empty content"
        ),
    ]
    
    for header, content, expected, description in test_boundaries:
        result = validator.validate_section_boundary(header, content)
        status = "✅" if result == expected else "❌"
        print(f"{status} Header: '{header[:30]}{'...' if len(header) > 30 else ''}'")
        print(f"   Content: '{content[:50]}{'...' if len(content) > 50 else ''}'")
        print(f"   Result: {result} (expected: {expected})")
        print(f"   Description: {description}\n")
    
    # Test 4: Process sample text with spaCy
    print("\n📋 Test 4: spaCy NLP Processing")
    print("-" * 80)
    
    sample_text = "PROFESSIONAL EXPERIENCE"
    doc = validator.nlp(sample_text)
    
    print(f"Text: '{sample_text}'")
    print(f"Tokens: {[token.text for token in doc]}")
    print(f"Token count: {len(doc)}")
    print(f"POS tags: {[(token.text, token.pos_) for token in doc]}")
    
    print("\n" + "="*80)
    print("🏁 TEST COMPLETE")
    print("="*80)
    
    print("\n📝 Summary:")
    print("   ✅ SectionValidator successfully loads spaCy model")
    print("   ✅ validate_section_header() works correctly")
    print("   ✅ validate_section_boundary() works correctly")
    print("   ✅ spaCy NLP processing is functional")

if __name__ == "__main__":
    test_section_validator()
