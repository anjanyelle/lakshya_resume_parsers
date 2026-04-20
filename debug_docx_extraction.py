#!/usr/bin/env python3
"""
Debug script to check what's happening with DOCX extraction
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ai-service'))

from parsers.text_extractor import TextExtractor

# Test with one DOCX file
test_file = "resumes/Rohan_Shah_Data_Analyst_5_Years_Resume.docx"

if os.path.exists(test_file):
    print(f"Testing DOCX extraction with: {test_file}")
    print("="*80)
    
    extractor = TextExtractor()
    
    # Test basic extraction
    print("\n1. Testing extract_from_docx():")
    try:
        text = extractor.extract_from_docx(test_file)
        print(f"   Length: {len(text)} chars")
        print(f"   Preview: {text[:500]}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test extraction with styles
    print("\n2. Testing extract_from_docx_with_styles():")
    try:
        text, heading_map = extractor.extract_from_docx_with_styles(test_file)
        print(f"   Length: {len(text)} chars")
        print(f"   Heading map entries: {len(heading_map)}")
        print(f"   Preview: {text[:500]}")
        print(f"\n   Headings found:")
        for line, is_heading in list(heading_map.items())[:10]:
            if is_heading:
                print(f"      • {line}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test extract_with_font_metadata
    print("\n3. Testing extract_with_font_metadata():")
    try:
        text, font_metadata = extractor.extract_with_font_metadata(test_file)
        print(f"   Length: {len(text)} chars")
        print(f"   Font metadata entries: {len(font_metadata)}")
        print(f"   Preview: {text[:500]}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test section splitting
    print("\n4. Testing section splitting:")
    try:
        from parsers.section_splitter import SectionSplitter
        
        text, font_metadata = extractor.extract_with_font_metadata(test_file)
        baseline = extractor.calculate_baseline_font_size(font_metadata)
        
        splitter = SectionSplitter()
        sections = splitter.split_sections(text, font_metadata, baseline)
        
        print(f"   Sections found: {list(sections.keys())}")
        for name, content in sections.items():
            print(f"      • {name}: {len(content)} chars")
    except Exception as e:
        print(f"   Error: {e}")
        import traceback
        traceback.print_exc()
else:
    print(f"File not found: {test_file}")
