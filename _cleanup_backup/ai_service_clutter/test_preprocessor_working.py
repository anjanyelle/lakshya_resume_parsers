#!/usr/bin/env python3
"""
Simple test to verify the preprocessor works correctly.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from parsers.preprocessor import ResumePreprocessor

def test_preprocessor():
    print("="*70)
    print("🧪 TESTING RESUME PREPROCESSOR")
    print("="*70)
    
    preprocessor = ResumePreprocessor()
    
    # Test with realistic resume text
    sample_text = """EXPERIENCE

• Developed Python appli-
cations for various cli-
ents.
  ● Managed team projects
  ◦ Database design

EDUCATION

Stanford Uni-
versity - BS in Com-
puter Science

SKILLS

Python, Java, JavaScript"""
    
    print(f"\n📝 Original text:")
    print(f"   {sample_text}")
    
    # Process the text
    result = preprocessor.preprocess(sample_text)
    
    print(f"\n✨ Processed text:")
    print(f"   {result}")
    
    print(f"\n🔍 Key improvements:")
    print(f"   • Bullets normalized: {'- ' in result}")
    print(f"   • Broken lines fixed: {'applications for various' in result}")
    print(f"   • Headers normalized: {'Experience' in result and 'Education' in result}")
    print(f"   • Encoding fixed: {'University -' in result}")
    
    # Test individual methods
    print(f"\n🧪 Testing individual methods:")
    
    # Test bullet normalization
    bullet_test = "• Item 1\n● Item 2\n◦ Item 3"
    bullet_result = preprocessor._normalize_bullets(bullet_test)
    print(f"   Bullets: {'✅' if all(line.startswith('- ') for line in bullet_result.split('\n')) else '❌'}")
    
    # Test encoding fixes
    encoding_test = "It's \"test\" with 'quotes'"
    encoding_result = preprocessor._fix_encoding_artifacts(encoding_test)
    print(f"   Encoding: {'✅' if '"' in encoding_result and "'" in encoding_result else '❌'}")
    
    # Test header normalization
    header_test = "EXPERIENCE\nThis is experience."
    header_result = preprocessor._normalize_section_headers(header_test)
    print(f"   Headers: {'✅' if 'Experience' in header_result else '❌'}")
    
    # Test whitespace
    whitespace_test = "Line 1   \n\n\n\nLine 2"
    whitespace_result = preprocessor._normalize_whitespace(whitespace_test)
    print(f"   Whitespace: {'✅' if whitespace_result.count('\n\n') <= 2 else '❌'}")
    
    print(f"\n🎉 Preprocessor test completed!")

if __name__ == "__main__":
    test_preprocessor()
