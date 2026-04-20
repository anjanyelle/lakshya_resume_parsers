#!/usr/bin/env python3
"""
Test script to verify font score integration into heading detection
"""

import sys
import os

# Add ai-service to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ai-service'))

from parsers.section_splitter import SectionSplitter

def test_font_score_integration():
    """Test font score integration with heuristic scoring"""
    
    print("\n" + "="*80)
    print("🧪 TESTING FONT SCORE INTEGRATION")
    print("="*80)
    
    splitter = SectionSplitter()
    baseline_font_size = 11.0
    
    # Create mock font metadata
    font_metadata = {
        "EXPERIENCE": {
            'font_size': 14.0,      # Large font
            'is_bold': True,         # Bold
            'x_position': 72.0,      # Left-aligned
            'vertical_gap': 24.0     # Large gap
        },
        "Senior Software Engineer": {
            'font_size': 11.0,       # Normal size
            'is_bold': False,        # Not bold
            'x_position': 72.0,      # Left-aligned
            'vertical_gap': 12.0     # Normal gap
        },
        "Tech Corp Inc.": {
            'font_size': 11.0,       # Normal size
            'is_bold': False,        # Not bold
            'x_position': 72.0,      # Left-aligned
            'vertical_gap': 8.0      # Small gap
        },
    }
    
    print(f"\n📊 Baseline font size: {baseline_font_size}")
    
    # Test Case 1: Line with heuristic score 4-6 and high font score (should upgrade)
    print("\n" + "="*80)
    print("📋 Test Case 1: Heuristic 4-6 + Font Score ≥5 → Upgrade to Confirmed")
    print("="*80)
    
    # Simulate a line that scores 5 on heuristic (Title Case, short, no punctuation)
    # and has high font score (large, bold, left-aligned, big gap)
    line = "EXPERIENCE"
    prev_line = ""
    next_line = "Senior Software Engineer"
    
    # Calculate scores manually
    heuristic = splitter.calculate_heuristic_score(line, prev_line, next_line)
    font_score = splitter.calculate_font_score(line, font_metadata, baseline_font_size)
    
    print(f"   Line: '{line}'")
    print(f"   Heuristic score: {heuristic}")
    print(f"   Font score: {font_score}")
    
    result = splitter.detect_section_header(line, prev_line, next_line, font_metadata, baseline_font_size)
    
    print(f"   Result: {result}")
    print(f"   Expected: Section name (upgraded from possible to confirmed)")
    print(f"   Status: {'✅ PASS' if result and result != 'possible_section' else '❌ FAIL'}")
    
    # Test Case 2: Line with heuristic score 4-6 and low font score (should downgrade)
    print("\n" + "="*80)
    print("📋 Test Case 2: Heuristic 4-6 + Font Score <3 → Downgrade to Content")
    print("="*80)
    
    # Simulate a line with moderate heuristic but low font score
    line = "Tech Corp Inc."
    prev_line = "Senior Software Engineer"
    next_line = ""
    
    heuristic = splitter.calculate_heuristic_score(line, prev_line, next_line)
    font_score = splitter.calculate_font_score(line, font_metadata, baseline_font_size)
    
    print(f"   Line: '{line}'")
    print(f"   Heuristic score: {heuristic}")
    print(f"   Font score: {font_score}")
    
    result = splitter.detect_section_header(line, prev_line, next_line, font_metadata, baseline_font_size)
    
    print(f"   Result: {result}")
    print(f"   Expected: None (downgraded to content)")
    print(f"   Status: {'✅ PASS' if result is None else '❌ FAIL'}")
    
    # Test Case 3: Line with heuristic score 4-6, no font metadata (should keep as possible)
    print("\n" + "="*80)
    print("📋 Test Case 3: Heuristic 4-6 + No Font Metadata → Keep as Possible")
    print("="*80)
    
    line = "Unknown Line"
    prev_line = ""
    next_line = ""
    
    heuristic = splitter.calculate_heuristic_score(line, prev_line, next_line)
    
    print(f"   Line: '{line}'")
    print(f"   Heuristic score: {heuristic}")
    print(f"   Font metadata: Not available")
    
    result = splitter.detect_section_header(line, prev_line, next_line, font_metadata, baseline_font_size)
    
    print(f"   Result: {result}")
    print(f"   Expected: 'possible_section' (no font data, keep heuristic decision)")
    
    # Test Case 4: No font metadata provided at all
    print("\n" + "="*80)
    print("📋 Test Case 4: No Font Metadata Dictionary → Heuristic Only")
    print("="*80)
    
    line = "EXPERIENCE"
    prev_line = ""
    next_line = ""
    
    heuristic = splitter.calculate_heuristic_score(line, prev_line, next_line)
    
    print(f"   Line: '{line}'")
    print(f"   Heuristic score: {heuristic}")
    print(f"   Font metadata: None")
    
    result = splitter.detect_section_header(line, prev_line, next_line, None, baseline_font_size)
    
    print(f"   Result: {result}")
    print(f"   Expected: Based on heuristic only (no font scoring)")
    
    print("\n" + "="*80)
    print("🏁 TEST COMPLETE")
    print("="*80)
    
    print("\n📝 Summary:")
    print("   • Heuristic 4-6 + Font ≥5 → Upgrade to confirmed heading")
    print("   • Heuristic 4-6 + Font <3 → Downgrade to content")
    print("   • Heuristic 4-6 + Font 3-4 → Keep as possible section")
    print("   • Heuristic 4-6 + No font data → Keep as possible section")
    print("   • No font metadata → Use heuristic only")

if __name__ == "__main__":
    test_font_score_integration()
