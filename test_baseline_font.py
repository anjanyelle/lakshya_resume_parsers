#!/usr/bin/env python3
"""
Test script to verify calculate_baseline_font_size function
"""

import sys
import os

# Add ai-service to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ai-service'))

from parsers.text_extractor import TextExtractor

def test_baseline_font_calculation():
    """Test baseline font size calculation with mock data"""
    
    print("\n" + "="*80)
    print("🧪 TESTING BASELINE FONT SIZE CALCULATION")
    print("="*80)
    
    extractor = TextExtractor()
    
    # Test Case 1: Empty metadata (should return default 11.0)
    print("\n📋 Test Case 1: Empty metadata")
    empty_metadata = {}
    baseline = extractor.calculate_baseline_font_size(empty_metadata)
    print(f"   Input: Empty dictionary")
    print(f"   Result: {baseline}")
    print(f"   Expected: 11.0")
    print(f"   Status: {'✅ PASS' if baseline == 11.0 else '❌ FAIL'}")
    
    # Test Case 2: Single font size
    print("\n📋 Test Case 2: Single font size")
    single_metadata = {
        "Line 1": {'font_size': 12.0, 'is_bold': False, 'x_position': 72.0, 'vertical_gap': 0},
        "Line 2": {'font_size': 12.0, 'is_bold': False, 'x_position': 72.0, 'vertical_gap': 12.0},
        "Line 3": {'font_size': 12.0, 'is_bold': False, 'x_position': 72.0, 'vertical_gap': 12.0},
    }
    baseline = extractor.calculate_baseline_font_size(single_metadata)
    print(f"   Input: 3 lines, all with font size 12.0")
    print(f"   Result: {baseline}")
    print(f"   Expected: 12.0")
    print(f"   Status: {'✅ PASS' if baseline == 12.0 else '❌ FAIL'}")
    
    # Test Case 3: Mixed font sizes (typical resume)
    print("\n📋 Test Case 3: Mixed font sizes (typical resume)")
    mixed_metadata = {
        "EXPERIENCE": {'font_size': 14.0, 'is_bold': True, 'x_position': 72.0, 'vertical_gap': 24.0},
        "Senior Engineer": {'font_size': 11.0, 'is_bold': False, 'x_position': 72.0, 'vertical_gap': 12.0},
        "Company Name": {'font_size': 11.0, 'is_bold': False, 'x_position': 72.0, 'vertical_gap': 8.0},
        "Bullet point 1": {'font_size': 10.0, 'is_bold': False, 'x_position': 90.0, 'vertical_gap': 10.0},
        "Bullet point 2": {'font_size': 10.0, 'is_bold': False, 'x_position': 90.0, 'vertical_gap': 10.0},
        "Bullet point 3": {'font_size': 10.0, 'is_bold': False, 'x_position': 90.0, 'vertical_gap': 10.0},
        "Bullet point 4": {'font_size': 10.0, 'is_bold': False, 'x_position': 90.0, 'vertical_gap': 10.0},
        "EDUCATION": {'font_size': 14.0, 'is_bold': True, 'x_position': 72.0, 'vertical_gap': 24.0},
        "Degree Name": {'font_size': 11.0, 'is_bold': False, 'x_position': 72.0, 'vertical_gap': 12.0},
        "University": {'font_size': 11.0, 'is_bold': False, 'x_position': 72.0, 'vertical_gap': 8.0},
    }
    baseline = extractor.calculate_baseline_font_size(mixed_metadata)
    print(f"   Input: 10 lines with sizes: 14.0 (2x), 11.0 (4x), 10.0 (4x)")
    print(f"   Result: {baseline}")
    print(f"   Expected: 10.0 or 11.0 (most common)")
    print(f"   Status: {'✅ PASS' if baseline in [10.0, 11.0] else '❌ FAIL'}")
    
    # Test Case 4: Realistic resume with body text dominance
    print("\n📋 Test Case 4: Realistic resume (body text dominant)")
    realistic_metadata = {
        "Name": {'font_size': 18.0, 'is_bold': True, 'x_position': 72.0, 'vertical_gap': 0},
        "SUMMARY": {'font_size': 14.0, 'is_bold': True, 'x_position': 72.0, 'vertical_gap': 20.0},
        "Summary line 1": {'font_size': 11.0, 'is_bold': False, 'x_position': 72.0, 'vertical_gap': 12.0},
        "Summary line 2": {'font_size': 11.0, 'is_bold': False, 'x_position': 72.0, 'vertical_gap': 12.0},
        "Summary line 3": {'font_size': 11.0, 'is_bold': False, 'x_position': 72.0, 'vertical_gap': 12.0},
        "EXPERIENCE": {'font_size': 14.0, 'is_bold': True, 'x_position': 72.0, 'vertical_gap': 20.0},
        "Job 1": {'font_size': 11.0, 'is_bold': False, 'x_position': 72.0, 'vertical_gap': 12.0},
        "Desc 1": {'font_size': 11.0, 'is_bold': False, 'x_position': 72.0, 'vertical_gap': 10.0},
        "Desc 2": {'font_size': 11.0, 'is_bold': False, 'x_position': 72.0, 'vertical_gap': 10.0},
        "Desc 3": {'font_size': 11.0, 'is_bold': False, 'x_position': 72.0, 'vertical_gap': 10.0},
        "Job 2": {'font_size': 11.0, 'is_bold': False, 'x_position': 72.0, 'vertical_gap': 12.0},
        "Desc 4": {'font_size': 11.0, 'is_bold': False, 'x_position': 72.0, 'vertical_gap': 10.0},
        "Desc 5": {'font_size': 11.0, 'is_bold': False, 'x_position': 72.0, 'vertical_gap': 10.0},
        "EDUCATION": {'font_size': 14.0, 'is_bold': True, 'x_position': 72.0, 'vertical_gap': 20.0},
        "Degree": {'font_size': 11.0, 'is_bold': False, 'x_position': 72.0, 'vertical_gap': 12.0},
    }
    baseline = extractor.calculate_baseline_font_size(realistic_metadata)
    print(f"   Input: 15 lines with sizes: 18.0 (1x), 14.0 (3x), 11.0 (11x)")
    print(f"   Result: {baseline}")
    print(f"   Expected: 11.0 (body text)")
    print(f"   Status: {'✅ PASS' if baseline == 11.0 else '❌ FAIL'}")
    
    print("\n" + "="*80)
    print("🏁 TEST COMPLETE")
    print("="*80)
    
    print("\n📝 Summary:")
    print("   • Empty metadata → returns default 11.0")
    print("   • Single font size → returns that size")
    print("   • Mixed sizes → returns most common (mode)")
    print("   • Typical resume → identifies body text size (ignores headers)")

if __name__ == "__main__":
    test_baseline_font_calculation()
