#!/usr/bin/env python3
"""
Demonstration of font signal detection on PDF resumes
Shows how font signals detect headers that keywords and heuristics miss
Uses realistic mock data based on typical resume patterns
"""

import sys
import os

# Add ai-service to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ai-service'))

from parsers.section_splitter import SectionSplitter
from parsers.text_extractor import TextExtractor

def test_standard_resume():
    """Test font signal detection on a standard single-column resume"""
    
    print("\n" + "="*80)
    print("📄 TEST 1: STANDARD SINGLE-COLUMN RESUME")
    print("="*80)
    
    # Mock text from a standard resume
    text = """John Doe
Senior Software Engineer
john.doe@email.com | (555) 123-4567

PROFESSIONAL SUMMARY
Experienced software engineer with 10+ years in full-stack development.

WORK EXPERIENCE
Senior Software Engineer | Tech Corp Inc. | 2020-Present
• Led development of microservices architecture
• Managed team of 5 engineers

Software Developer | StartUp Solutions | 2018-2020
• Built web applications using React and Node.js

EDUCATION
Master of Science in Computer Science
Stanford University | 2016-2018

TECHNICAL SKILLS
Python, JavaScript, React, Node.js, AWS, Docker, Kubernetes"""
    
    # Mock font metadata (simulating what PyMuPDF would extract)
    font_metadata = {
        "John Doe": {
            'font_size': 18.0, 'is_bold': True, 'x_position': 72.0, 'vertical_gap': 0.0
        },
        "Senior Software Engineer": {
            'font_size': 12.0, 'is_bold': False, 'x_position': 72.0, 'vertical_gap': 8.0
        },
        "john.doe@email.com | (555) 123-4567": {
            'font_size': 10.0, 'is_bold': False, 'x_position': 72.0, 'vertical_gap': 6.0
        },
        "PROFESSIONAL SUMMARY": {
            'font_size': 14.0, 'is_bold': True, 'x_position': 72.0, 'vertical_gap': 20.0
        },
        "Experienced software engineer with 10+ years in full-stack development.": {
            'font_size': 11.0, 'is_bold': False, 'x_position': 72.0, 'vertical_gap': 10.0
        },
        "WORK EXPERIENCE": {
            'font_size': 14.0, 'is_bold': True, 'x_position': 72.0, 'vertical_gap': 20.0
        },
        "Senior Software Engineer | Tech Corp Inc. | 2020-Present": {
            'font_size': 11.0, 'is_bold': False, 'x_position': 72.0, 'vertical_gap': 10.0
        },
        "• Led development of microservices architecture": {
            'font_size': 10.0, 'is_bold': False, 'x_position': 90.0, 'vertical_gap': 8.0
        },
        "• Managed team of 5 engineers": {
            'font_size': 10.0, 'is_bold': False, 'x_position': 90.0, 'vertical_gap': 8.0
        },
        "Software Developer | StartUp Solutions | 2018-2020": {
            'font_size': 11.0, 'is_bold': False, 'x_position': 72.0, 'vertical_gap': 12.0
        },
        "• Built web applications using React and Node.js": {
            'font_size': 10.0, 'is_bold': False, 'x_position': 90.0, 'vertical_gap': 8.0
        },
        "EDUCATION": {
            'font_size': 14.0, 'is_bold': True, 'x_position': 72.0, 'vertical_gap': 20.0
        },
        "Master of Science in Computer Science": {
            'font_size': 11.0, 'is_bold': False, 'x_position': 72.0, 'vertical_gap': 10.0
        },
        "Stanford University | 2016-2018": {
            'font_size': 11.0, 'is_bold': False, 'x_position': 72.0, 'vertical_gap': 8.0
        },
        "TECHNICAL SKILLS": {
            'font_size': 14.0, 'is_bold': True, 'x_position': 72.0, 'vertical_gap': 20.0
        },
        "Python, JavaScript, React, Node.js, AWS, Docker, Kubernetes": {
            'font_size': 11.0, 'is_bold': False, 'x_position': 72.0, 'vertical_gap': 10.0
        },
    }
    
    baseline_font_size = 11.0
    
    return analyze_detection(text, font_metadata, baseline_font_size, "Standard Resume")


def test_creative_resume():
    """Test font signal detection on a creative resume with unusual heading words"""
    
    print("\n" + "="*80)
    print("📄 TEST 2: CREATIVE RESUME WITH UNUSUAL HEADINGS")
    print("="*80)
    
    # Mock text from a creative resume with non-standard section names
    text = """ALEX CHEN
UX Designer & Creative Technologist
alex.chen@design.io | Portfolio: alexchen.design

WHO I AM
Creative designer passionate about human-centered design and emerging technologies.

WHERE I'VE WORKED
Lead UX Designer | Innovation Lab | 2021-Present
• Designed award-winning mobile experiences
• Led design thinking workshops

UX Designer | Digital Agency | 2019-2021
• Created user interfaces for Fortune 500 clients

MY LEARNING JOURNEY
Bachelor of Fine Arts in Interaction Design
Rhode Island School of Design | 2015-2019

WHAT I BRING TO THE TABLE
Figma, Sketch, Adobe XD, Prototyping, User Research, Design Systems

THINGS I'VE BUILT
Mobile Banking App - Redesigned onboarding flow (2M+ users)
AR Shopping Experience - Created immersive product visualization
Design System - Built component library for enterprise platform"""
    
    # Mock font metadata - creative resume uses different fonts/sizes
    font_metadata = {
        "ALEX CHEN": {
            'font_size': 24.0, 'is_bold': True, 'x_position': 72.0, 'vertical_gap': 0.0
        },
        "UX Designer & Creative Technologist": {
            'font_size': 13.0, 'is_bold': False, 'x_position': 72.0, 'vertical_gap': 10.0
        },
        "alex.chen@design.io | Portfolio: alexchen.design": {
            'font_size': 10.0, 'is_bold': False, 'x_position': 72.0, 'vertical_gap': 8.0
        },
        "WHO I AM": {
            'font_size': 16.0, 'is_bold': True, 'x_position': 72.0, 'vertical_gap': 24.0
        },
        "Creative designer passionate about human-centered design and emerging technologies.": {
            'font_size': 11.0, 'is_bold': False, 'x_position': 72.0, 'vertical_gap': 12.0
        },
        "WHERE I'VE WORKED": {
            'font_size': 16.0, 'is_bold': True, 'x_position': 72.0, 'vertical_gap': 24.0
        },
        "Lead UX Designer | Innovation Lab | 2021-Present": {
            'font_size': 11.0, 'is_bold': False, 'x_position': 72.0, 'vertical_gap': 12.0
        },
        "• Designed award-winning mobile experiences": {
            'font_size': 10.0, 'is_bold': False, 'x_position': 90.0, 'vertical_gap': 8.0
        },
        "• Led design thinking workshops": {
            'font_size': 10.0, 'is_bold': False, 'x_position': 90.0, 'vertical_gap': 8.0
        },
        "UX Designer | Digital Agency | 2019-2021": {
            'font_size': 11.0, 'is_bold': False, 'x_position': 72.0, 'vertical_gap': 12.0
        },
        "• Created user interfaces for Fortune 500 clients": {
            'font_size': 10.0, 'is_bold': False, 'x_position': 90.0, 'vertical_gap': 8.0
        },
        "MY LEARNING JOURNEY": {
            'font_size': 16.0, 'is_bold': True, 'x_position': 72.0, 'vertical_gap': 24.0
        },
        "Bachelor of Fine Arts in Interaction Design": {
            'font_size': 11.0, 'is_bold': False, 'x_position': 72.0, 'vertical_gap': 12.0
        },
        "Rhode Island School of Design | 2015-2019": {
            'font_size': 11.0, 'is_bold': False, 'x_position': 72.0, 'vertical_gap': 8.0
        },
        "WHAT I BRING TO THE TABLE": {
            'font_size': 16.0, 'is_bold': True, 'x_position': 72.0, 'vertical_gap': 24.0
        },
        "Figma, Sketch, Adobe XD, Prototyping, User Research, Design Systems": {
            'font_size': 11.0, 'is_bold': False, 'x_position': 72.0, 'vertical_gap': 12.0
        },
        "THINGS I'VE BUILT": {
            'font_size': 16.0, 'is_bold': True, 'x_position': 72.0, 'vertical_gap': 24.0
        },
        "Mobile Banking App - Redesigned onboarding flow (2M+ users)": {
            'font_size': 11.0, 'is_bold': False, 'x_position': 72.0, 'vertical_gap': 12.0
        },
        "AR Shopping Experience - Created immersive product visualization": {
            'font_size': 11.0, 'is_bold': False, 'x_position': 72.0, 'vertical_gap': 10.0
        },
        "Design System - Built component library for enterprise platform": {
            'font_size': 11.0, 'is_bold': False, 'x_position': 72.0, 'vertical_gap': 10.0
        },
    }
    
    baseline_font_size = 11.0
    
    return analyze_detection(text, font_metadata, baseline_font_size, "Creative Resume")


def analyze_detection(text, font_metadata, baseline_font_size, resume_type):
    """Analyze detection results across three modes"""
    
    splitter = SectionSplitter()
    lines = text.split('\n')
    
    print(f"\n📊 Baseline font size: {baseline_font_size}")
    print(f"📊 Lines with font metadata: {len(font_metadata)}")
    
    # Mode 1: Keywords only
    print("\n" + "="*80)
    print("📋 MODE 1: KEYWORDS ONLY")
    print("="*80)
    
    keyword_detected = []
    for line in lines:
        if not line.strip():
            continue
        normalized = line.strip().lower()
        result = splitter._match_section_keywords(normalized)
        if result:
            keyword_detected.append((line.strip(), result))
    
    print(f"\n✅ Detected {len(keyword_detected)} headers:")
    for line, section in keyword_detected:
        print(f"   • {section}: '{line}'")
    
    # Mode 2: Keywords + Heuristics (no font)
    print("\n" + "="*80)
    print("📋 MODE 2: KEYWORDS + HEURISTICS (No Font)")
    print("="*80)
    
    heuristic_detected = []
    for i, line in enumerate(lines):
        if not line.strip():
            continue
        prev_line = lines[i-1] if i > 0 else ''
        next_line = lines[i+1] if i < len(lines)-1 else ''
        
        result = splitter.detect_section_header(line.strip(), prev_line, next_line, None, baseline_font_size)
        if result and result not in ['possible_section']:
            heuristic_score = splitter.calculate_heuristic_score(line.strip(), prev_line, next_line)
            heuristic_detected.append((line.strip(), result, heuristic_score))
    
    print(f"\n✅ Detected {len(heuristic_detected)} headers:")
    for line, section, h_score in heuristic_detected:
        print(f"   • {section}: '{line}' (Heuristic: {h_score})")
    
    # Mode 3: Full detection with font signals
    print("\n" + "="*80)
    print("📋 MODE 3: FULL DETECTION (Keywords + Heuristics + Font)")
    print("="*80)
    
    font_detected = []
    font_upgraded = []
    
    for i, line in enumerate(lines):
        if not line.strip():
            continue
        prev_line = lines[i-1] if i > 0 else ''
        next_line = lines[i+1] if i < len(lines)-1 else ''
        
        heuristic_score = splitter.calculate_heuristic_score(line.strip(), prev_line, next_line)
        font_score = splitter.calculate_font_score(line.strip(), font_metadata, baseline_font_size)
        
        result = splitter.detect_section_header(line.strip(), prev_line, next_line, 
                                               font_metadata, baseline_font_size)
        
        if result and result not in ['possible_section']:
            font_detected.append((line.strip(), result, heuristic_score, font_score))
            
            # Check if upgraded by font
            if 4 <= heuristic_score <= 6 and font_score >= 5:
                font_upgraded.append((line.strip(), result, heuristic_score, font_score))
    
    print(f"\n✅ Detected {len(font_detected)} headers:")
    for line, section, h_score, f_score in font_detected:
        print(f"   • {section}: '{line}' (H:{h_score}, F:{f_score})")
    
    # Analysis
    print("\n" + "="*80)
    print("📊 IMPACT ANALYSIS")
    print("="*80)
    
    keyword_lines = set(line for line, _ in keyword_detected)
    heuristic_lines = set(line for line, _, _ in heuristic_detected)
    font_lines = set(line for line, _, _, _ in font_detected)
    
    font_only = font_lines - keyword_lines
    
    print(f"\n📈 Detection Summary:")
    print(f"   Keywords only: {len(keyword_detected)} headers")
    print(f"   + Heuristics: {len(heuristic_detected)} headers")
    print(f"   + Font signals: {len(font_detected)} headers")
    
    print(f"\n🎯 NEW headers found by font signals: {len(font_only)}")
    if font_only:
        print("   (Headers that keywords missed but font signals caught):")
        for line in font_only:
            for l, s, h, f in font_detected:
                if l == line:
                    print(f"      ✨ '{line}' → {s} (H:{h}, F:{f})")
                    break
    
    print(f"\n⬆️ Headers UPGRADED by font signals: {len(font_upgraded)}")
    if font_upgraded:
        print("   (Heuristic 4-6 upgraded to confirmed by font ≥5):")
        for line, section, h_score, f_score in font_upgraded:
            print(f"      ⬆️ '{line}' → {section} (H:{h_score}→Confirmed, F:{f_score})")
    
    return {
        'keyword_count': len(keyword_detected),
        'heuristic_count': len(heuristic_detected),
        'font_count': len(font_detected),
        'font_only': len(font_only),
        'upgraded': len(font_upgraded)
    }


def main():
    print("\n" + "="*80)
    print("🧪 FONT SIGNAL DETECTION TEST - PDF RESUMES")
    print("="*80)
    print("\nThis test demonstrates how font signals detect headers that")
    print("keywords and heuristics miss, using realistic mock data.")
    
    # Test both resume types
    standard_results = test_standard_resume()
    creative_results = test_creative_resume()
    
    # Final summary
    print("\n" + "="*80)
    print("🏁 FINAL SUMMARY")
    print("="*80)
    
    print(f"\n📊 Standard Resume:")
    print(f"   Keywords: {standard_results['keyword_count']} headers")
    print(f"   + Heuristics: {standard_results['heuristic_count']} headers")
    print(f"   + Font: {standard_results['font_count']} headers")
    print(f"   🎯 New by font: {standard_results['font_only']}")
    print(f"   ⬆️ Upgraded: {standard_results['upgraded']}")
    
    print(f"\n📊 Creative Resume:")
    print(f"   Keywords: {creative_results['keyword_count']} headers")
    print(f"   + Heuristics: {creative_results['heuristic_count']} headers")
    print(f"   + Font: {creative_results['font_count']} headers")
    print(f"   🎯 New by font: {creative_results['font_only']}")
    print(f"   ⬆️ Upgraded: {creative_results['upgraded']}")
    
    print("\n✅ Key Findings:")
    print("   • Font signals catch non-standard headings (e.g., 'WHO I AM', 'WHERE I'VE WORKED')")
    print("   • Large font + bold + spacing = high confidence header")
    print("   • Works even when keywords don't match")
    print("   • Essential for creative resumes with unusual section names")

if __name__ == "__main__":
    main()
