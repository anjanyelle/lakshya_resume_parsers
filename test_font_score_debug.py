#!/usr/bin/env python3
"""
Debug test to understand font score calculation
"""

import sys
import os

# Add ai-service to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ai-service'))

from parsers.section_splitter import SectionSplitter

def debug_font_score():
    """Debug font score calculation"""
    
    splitter = SectionSplitter()
    baseline_font_size = 11.0
    
    # Mock font metadata
    font_metadata = {
        "EXPERIENCE": {'font_size': 14.0, 'is_bold': True, 'x_position': 72.0, 'vertical_gap': 24.0},
        "Senior Software Engineer": {'font_size': 11.0, 'is_bold': False, 'x_position': 72.0, 'vertical_gap': 12.0},
        "Company Name": {'font_size': 11.0, 'is_bold': False, 'x_position': 72.0, 'vertical_gap': 8.0},
        "Bullet point": {'font_size': 10.0, 'is_bold': False, 'x_position': 90.0, 'vertical_gap': 10.0},
        "SKILLS": {'font_size': 13.0, 'is_bold': True, 'x_position': 72.0, 'vertical_gap': 20.0},
        "Python, JavaScript": {'font_size': 11.0, 'is_bold': False, 'x_position': 72.0, 'vertical_gap': 10.0},
    }
    
    # Calculate average vertical gap
    vertical_gaps = [m.get('vertical_gap', 0) for m in font_metadata.values() if m.get('vertical_gap', 0) > 0]
    avg_gap = sum(vertical_gaps) / len(vertical_gaps)
    
    print(f"Vertical gaps: {vertical_gaps}")
    print(f"Average gap: {avg_gap:.2f}")
    print(f"1.5x average: {avg_gap * 1.5:.2f}")
    
    print("\n" + "="*80)
    
    # Test EXPERIENCE
    line = "EXPERIENCE"
    metadata = font_metadata[line]
    score = splitter.calculate_font_score(line, font_metadata, baseline_font_size)
    
    print(f"Line: {line}")
    print(f"  Font size: {metadata['font_size']} (baseline: {baseline_font_size}, diff: {metadata['font_size'] - baseline_font_size})")
    print(f"  Bold: {metadata['is_bold']}")
    print(f"  X position: {metadata['x_position']}")
    print(f"  Vertical gap: {metadata['vertical_gap']} (avg: {avg_gap:.2f}, threshold: {avg_gap * 1.5:.2f})")
    print(f"  Gap > threshold? {metadata['vertical_gap'] > avg_gap * 1.5}")
    print(f"  Total score: {score}")
    
    print("\n" + "="*80)
    
    # Test SKILLS
    line = "SKILLS"
    metadata = font_metadata[line]
    score = splitter.calculate_font_score(line, font_metadata, baseline_font_size)
    
    print(f"Line: {line}")
    print(f"  Font size: {metadata['font_size']} (baseline: {baseline_font_size}, diff: {metadata['font_size'] - baseline_font_size})")
    print(f"  Bold: {metadata['is_bold']}")
    print(f"  X position: {metadata['x_position']}")
    print(f"  Vertical gap: {metadata['vertical_gap']} (avg: {avg_gap:.2f}, threshold: {avg_gap * 1.5:.2f})")
    print(f"  Gap > threshold? {metadata['vertical_gap'] > avg_gap * 1.5}")
    print(f"  Total score: {score}")

if __name__ == "__main__":
    debug_font_score()
