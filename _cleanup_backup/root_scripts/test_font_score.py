#!/usr/bin/env python3
"""
Test script to verify calculate_font_score function
"""

import sys
import os

# Add ai-service to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ai-service'))

from parsers.section_splitter import SectionSplitter

def test_font_score_calculation():
    """Test font score calculation with mock font metadata"""
    
    print("\n" + "="*80)
    print("🧪 TESTING FONT SCORE CALCULATION")
    print("="*80)
    
    splitter = SectionSplitter()
    baseline_font_size = 11.0
    
    # Create mock font metadata for a typical resume
    font_metadata = {
        "EXPERIENCE": {
            'font_size': 14.0,      # +3 points (>3 above baseline)
            'is_bold': True,         # +3 points
            'x_position': 72.0,      # +1 point (leftmost)
            'vertical_gap': 24.0     # +2 points (>1.5x avg ~12)
        },
        "Senior Software Engineer": {
            'font_size': 11.0,       # +0 points (same as baseline)
            'is_bold': False,        # +0 points
            'x_position': 72.0,      # +1 point (leftmost)
            'vertical_gap': 12.0     # +0 points (normal spacing)
        },
        "Company Name": {
            'font_size': 11.0,       # +0 points
            'is_bold': False,        # +0 points
            'x_position': 72.0,      # +1 point
            'vertical_gap': 8.0      # +0 points
        },
        "Bullet point": {
            'font_size': 10.0,       # +0 points (below baseline)
            'is_bold': False,        # +0 points
            'x_position': 90.0,      # +0 points (indented)
            'vertical_gap': 10.0     # +0 points
        },
        "SKILLS": {
            'font_size': 13.0,       # +2 points (>1.5 above baseline)
            'is_bold': True,         # +3 points
            'x_position': 72.0,      # +1 point
            'vertical_gap': 20.0     # +2 points
        },
        "Python, JavaScript": {
            'font_size': 11.0,       # +0 points
            'is_bold': False,        # +0 points
            'x_position': 72.0,      # +1 point
            'vertical_gap': 10.0     # +0 points
        },
    }
    
    print(f"\n📊 Baseline font size: {baseline_font_size}")
    print(f"📊 Average line spacing: ~12.0 (calculated from metadata)")
    
    # Test Case 1: Section header (large, bold, left-aligned, big gap)
    print("\n" + "="*80)
    print("📋 Test Case 1: Section Header - 'EXPERIENCE'")
    print("="*80)
    line = "EXPERIENCE"
    score = splitter.calculate_font_score(line, font_metadata, baseline_font_size)
    print(f"   Font size: 14.0 (baseline: 11.0, diff: +3.0) → +3 points")
    print(f"   Bold: True → +3 points")
    print(f"   X position: 72.0 (leftmost: 72.0) → +1 point")
    print(f"   Vertical gap: 24.0 (avg: ~12.0, 1.5x: 18.0) → +2 points")
    print(f"   Total score: {score}")
    print(f"   Expected: 9 (3+3+1+2)")
    print(f"   Status: {'✅ PASS' if score == 9 else '❌ FAIL'}")
    
    # Test Case 2: Job title (normal size, not bold, left-aligned)
    print("\n" + "="*80)
    print("📋 Test Case 2: Job Title - 'Senior Software Engineer'")
    print("="*80)
    line = "Senior Software Engineer"
    score = splitter.calculate_font_score(line, font_metadata, baseline_font_size)
    print(f"   Font size: 11.0 (baseline: 11.0, diff: 0.0) → +0 points")
    print(f"   Bold: False → +0 points")
    print(f"   X position: 72.0 (leftmost: 72.0) → +1 point")
    print(f"   Vertical gap: 12.0 (avg: ~12.0, 1.5x: 18.0) → +0 points")
    print(f"   Total score: {score}")
    print(f"   Expected: 1 (0+0+1+0)")
    print(f"   Status: {'✅ PASS' if score == 1 else '❌ FAIL'}")
    
    # Test Case 3: Bullet point (small, indented)
    print("\n" + "="*80)
    print("📋 Test Case 3: Bullet Point - 'Bullet point'")
    print("="*80)
    line = "Bullet point"
    score = splitter.calculate_font_score(line, font_metadata, baseline_font_size)
    print(f"   Font size: 10.0 (baseline: 11.0, diff: -1.0) → +0 points")
    print(f"   Bold: False → +0 points")
    print(f"   X position: 90.0 (leftmost: 72.0, diff: 18.0) → +0 points")
    print(f"   Vertical gap: 10.0 (avg: ~12.0, 1.5x: 18.0) → +0 points")
    print(f"   Total score: {score}")
    print(f"   Expected: 0 (0+0+0+0)")
    print(f"   Status: {'✅ PASS' if score == 0 else '❌ FAIL'}")
    
    # Test Case 4: Section header (moderately large, bold)
    print("\n" + "="*80)
    print("📋 Test Case 4: Section Header - 'SKILLS'")
    print("="*80)
    line = "SKILLS"
    score = splitter.calculate_font_score(line, font_metadata, baseline_font_size)
    print(f"   Font size: 13.0 (baseline: 11.0, diff: +2.0) → +2 points")
    print(f"   Bold: True → +3 points")
    print(f"   X position: 72.0 (leftmost: 72.0) → +1 point")
    print(f"   Vertical gap: 20.0 (avg: ~12.0, 1.5x: 18.0) → +2 points")
    print(f"   Total score: {score}")
    print(f"   Expected: 8 (2+3+1+2)")
    print(f"   Status: {'✅ PASS' if score == 8 else '❌ FAIL'}")
    
    # Test Case 5: Line not in metadata
    print("\n" + "="*80)
    print("📋 Test Case 5: Line Not in Metadata - 'Unknown Line'")
    print("="*80)
    line = "Unknown Line"
    score = splitter.calculate_font_score(line, font_metadata, baseline_font_size)
    print(f"   Line not found in font metadata")
    print(f"   Total score: {score}")
    print(f"   Expected: 0 (no metadata)")
    print(f"   Status: {'✅ PASS' if score == 0 else '❌ FAIL'}")
    
    # Test Case 6: Empty metadata
    print("\n" + "="*80)
    print("📋 Test Case 6: Empty Metadata Dictionary")
    print("="*80)
    line = "Any Line"
    score = splitter.calculate_font_score(line, {}, baseline_font_size)
    print(f"   Empty metadata dictionary")
    print(f"   Total score: {score}")
    print(f"   Expected: 0 (no metadata)")
    print(f"   Status: {'✅ PASS' if score == 0 else '❌ FAIL'}")
    
    print("\n" + "="*80)
    print("🏁 TEST COMPLETE")
    print("="*80)
    
    print("\n📝 Summary:")
    print("   • Score range: 0-9 points")
    print("   • Font size >3 above baseline: +3 points")
    print("   • Font size >1.5 above baseline: +2 points")
    print("   • Bold font: +3 points")
    print("   • Left-aligned (within 10px): +1 point")
    print("   • Large vertical gap (>1.5x avg): +2 points")
    print("   • No metadata: 0 points")

if __name__ == "__main__":
    test_font_score_calculation()
