#!/usr/bin/env python3
"""
Test script to verify font signal detection on PDF resumes
Tests both standard and creative resumes to see which headings are detected
using font signals that keywords and heuristics missed.
"""

import sys
import os

# Add ai-service to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ai-service'))

from parsers.text_extractor import TextExtractor
from parsers.section_splitter import SectionSplitter

def test_font_signal_detection():
    """Test font signal detection on PDF resumes"""
    
    print("\n" + "="*80)
    print("🧪 TESTING FONT SIGNAL DETECTION ON PDF RESUMES")
    print("="*80)
    
    # Test files - select two different types of resumes
    test_files = [
        "ai-service/training/data/resumes/Julian Vance Executive Resume (1).pdf",
        "ai-service/training/data/resumes/Thaddeus Vance Executive QA Resume.pdf",
    ]
    
    extractor = TextExtractor()
    splitter = SectionSplitter()
    
    for pdf_file in test_files:
        if not os.path.exists(pdf_file):
            print(f"\n⚠️ Skipping {pdf_file} - file not found")
            continue
        
        print("\n" + "="*80)
        print(f"📄 Testing: {os.path.basename(pdf_file)}")
        print("="*80)
        
        try:
            # Extract with font metadata
            print("\n🔍 Step 1: Extracting text and font metadata...")
            text, font_metadata = extractor.extract_with_font_metadata(pdf_file)
            
            print(f"   ✅ Extracted {len(text)} characters")
            print(f"   ✅ Font metadata for {len(font_metadata)} lines")
            
            # Calculate baseline font size
            baseline_font_size = extractor.calculate_baseline_font_size(font_metadata)
            print(f"   ✅ Baseline font size: {baseline_font_size}")
            
            # Show sample of font metadata
            print(f"\n📊 Font Metadata Sample (first 10 lines with metadata):")
            count = 0
            for line_text, metadata in list(font_metadata.items())[:10]:
                count += 1
                print(f"\n   {count}. '{line_text[:60]}{'...' if len(line_text) > 60 else ''}'")
                print(f"      Font: {metadata['font_size']:.1f}pt, Bold: {metadata['is_bold']}, "
                      f"Gap: {metadata['vertical_gap']:.1f}px")
            
            # Test detection with three modes
            print("\n" + "="*80)
            print("🔍 Step 2: Testing Detection Modes")
            print("="*80)
            
            # Mode 1: Keywords only (no heuristics, no font)
            print("\n📋 Mode 1: KEYWORDS ONLY")
            print("   (Simulating old detection without heuristics or font signals)")
            
            lines = text.split('\n')
            keyword_detected = []
            
            for line in lines[:50]:  # Test first 50 lines
                if not line.strip():
                    continue
                
                # Try keyword matching only
                normalized = line.strip().lower()
                result = splitter._match_section_keywords(normalized)
                if result:
                    keyword_detected.append((line.strip(), result))
            
            print(f"   Detected {len(keyword_detected)} headers using keywords:")
            for line, section in keyword_detected[:10]:
                print(f"      • {section}: '{line[:50]}{'...' if len(line) > 50 else ''}'")
            
            # Mode 2: Keywords + Heuristics (no font)
            print("\n📋 Mode 2: KEYWORDS + HEURISTICS")
            print("   (Without font signals)")
            
            heuristic_detected = []
            for i, line in enumerate(lines[:50]):
                if not line.strip():
                    continue
                
                prev_line = lines[i-1] if i > 0 else ''
                next_line = lines[i+1] if i < len(lines)-1 else ''
                
                # Detect without font metadata
                result = splitter.detect_section_header(line.strip(), prev_line, next_line, None, baseline_font_size)
                if result and result not in ['possible_section']:
                    heuristic_detected.append((line.strip(), result))
            
            print(f"   Detected {len(heuristic_detected)} headers using keywords+heuristics:")
            for line, section in heuristic_detected[:10]:
                print(f"      • {section}: '{line[:50]}{'...' if len(line) > 50 else ''}'")
            
            # Mode 3: Keywords + Heuristics + Font Signals
            print("\n📋 Mode 3: KEYWORDS + HEURISTICS + FONT SIGNALS")
            print("   (Full detection with font metadata)")
            
            font_detected = []
            font_upgraded = []
            
            for i, line in enumerate(lines[:50]):
                if not line.strip():
                    continue
                
                prev_line = lines[i-1] if i > 0 else ''
                next_line = lines[i+1] if i < len(lines)-1 else ''
                
                # Calculate scores for analysis
                heuristic_score = splitter.calculate_heuristic_score(line.strip(), prev_line, next_line)
                font_score = splitter.calculate_font_score(line.strip(), font_metadata, baseline_font_size)
                
                # Detect with font metadata
                result = splitter.detect_section_header(line.strip(), prev_line, next_line, 
                                                       font_metadata, baseline_font_size)
                
                if result and result not in ['possible_section']:
                    font_detected.append((line.strip(), result, heuristic_score, font_score))
                    
                    # Check if this was upgraded by font signals
                    if heuristic_score >= 4 and heuristic_score <= 6 and font_score >= 5:
                        font_upgraded.append((line.strip(), result, heuristic_score, font_score))
            
            print(f"   Detected {len(font_detected)} headers using full detection:")
            for line, section, h_score, f_score in font_detected[:10]:
                print(f"      • {section}: '{line[:50]}{'...' if len(line) > 50 else ''}' "
                      f"(H:{h_score}, F:{f_score})")
            
            # Analysis: What did font signals add?
            print("\n" + "="*80)
            print("📊 ANALYSIS: Font Signal Impact")
            print("="*80)
            
            keyword_lines = set(line for line, _ in keyword_detected)
            heuristic_lines = set(line for line, _ in heuristic_detected)
            font_lines = set(line for line, _, _, _ in font_detected)
            
            # Headers detected by font but not by keywords
            font_only = font_lines - keyword_lines
            
            # Headers upgraded by font signals
            upgraded_lines = set(line for line, _, _, _ in font_upgraded)
            
            print(f"\n✅ Headers detected by KEYWORDS only: {len(keyword_detected)}")
            print(f"✅ Headers detected by KEYWORDS+HEURISTICS: {len(heuristic_detected)}")
            print(f"✅ Headers detected by FULL DETECTION: {len(font_detected)}")
            
            print(f"\n🎯 NEW headers found by font signals: {len(font_only)}")
            if font_only:
                print("   (Headers that keywords missed but font signals caught):")
                for line in list(font_only)[:5]:
                    # Find the scores for this line
                    for l, s, h, f in font_detected:
                        if l == line:
                            print(f"      • '{line[:60]}{'...' if len(line) > 60 else ''}' "
                                  f"(Heuristic:{h}, Font:{f})")
                            break
            
            print(f"\n⬆️ Headers UPGRADED by font signals: {len(upgraded_lines)}")
            if upgraded_lines:
                print("   (Headers with heuristic 4-6 upgraded to confirmed by font ≥5):")
                for line, section, h_score, f_score in font_upgraded[:5]:
                    print(f"      • '{line[:60]}{'...' if len(line) > 60 else ''}' "
                          f"(H:{h_score}→Confirmed, F:{f_score})")
            
            # Show lines with high font scores
            print(f"\n🔥 Lines with HIGH font scores (≥7):")
            high_font_lines = [(l, s, h, f) for l, s, h, f in font_detected if f >= 7]
            for line, section, h_score, f_score in high_font_lines[:5]:
                print(f"      • '{line[:60]}{'...' if len(line) > 60 else ''}' "
                      f"(Font:{f_score}, Heuristic:{h_score})")
            
        except Exception as e:
            print(f"\n❌ Error processing {pdf_file}: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*80)
    print("🏁 TEST COMPLETE")
    print("="*80)
    
    print("\n📝 Summary:")
    print("   • Font signals detect headers that keywords miss")
    print("   • Font signals upgrade ambiguous headers (heuristic 4-6)")
    print("   • High font scores (≥7) indicate strong visual prominence")
    print("   • Combination of all three methods provides best accuracy")

if __name__ == "__main__":
    test_font_signal_detection()
