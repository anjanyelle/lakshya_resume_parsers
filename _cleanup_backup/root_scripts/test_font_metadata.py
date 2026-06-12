#!/usr/bin/env python3
"""
Test script to verify font metadata extraction from PDF files
"""

import sys
import os

# Add ai-service to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ai-service'))

from parsers.text_extractor import TextExtractor

def test_font_metadata_extraction():
    """Test font metadata extraction from different file types"""
    
    print("\n" + "="*80)
    print("🧪 TESTING FONT METADATA EXTRACTION")
    print("="*80)
    
    extractor = TextExtractor()
    
    # Test files
    test_files = [
        ('resume1.txt', 'TXT'),
        # Add PDF test when available
    ]
    
    # Check for PDF files in current directory
    pdf_files = [f for f in os.listdir('.') if f.endswith('.pdf')]
    if pdf_files:
        test_files.append((pdf_files[0], 'PDF'))
    
    for file_path, file_type in test_files:
        if not os.path.exists(file_path):
            print(f"\n⚠️ Skipping {file_path} - file not found")
            continue
        
        print(f"\n{'='*80}")
        print(f"📄 Testing: {file_path} ({file_type})")
        print("="*80)
        
        try:
            text, font_metadata = extractor.extract_with_font_metadata(file_path)
            
            print(f"\n✅ Extraction successful!")
            print(f"   Text length: {len(text)} characters")
            print(f"   Metadata entries: {len(font_metadata)}")
            
            # Calculate baseline font size
            baseline_font_size = extractor.calculate_baseline_font_size(font_metadata)
            print(f"   Baseline font size: {baseline_font_size}")
            
            if font_metadata:
                print(f"\n📊 Font Metadata Sample (first 5 lines):")
                for i, (line_text, metadata) in enumerate(list(font_metadata.items())[:5]):
                    print(f"\n   Line {i+1}: '{line_text[:60]}{'...' if len(line_text) > 60 else ''}'")
                    print(f"      • Font size: {metadata['font_size']}")
                    print(f"      • Is bold: {metadata['is_bold']}")
                    print(f"      • X position: {metadata['x_position']}")
                    print(f"      • Vertical gap: {metadata['vertical_gap']}")
            else:
                print(f"\n   ℹ️ No font metadata (expected for {file_type} files)")
            
            print(f"\n📝 Text Preview (first 200 chars):")
            print(f"   {text[:200]}...")
            
        except Exception as e:
            print(f"\n❌ Extraction failed: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*80)
    print("🏁 TEST COMPLETE")
    print("="*80)
    
    print("\n📝 Summary:")
    print("   • For PDF files: Returns text + font metadata dictionary")
    print("   • For DOCX/TXT files: Returns text + empty dictionary")
    print("   • Font metadata includes: font_size, is_bold, x_position, vertical_gap")

if __name__ == "__main__":
    test_font_metadata_extraction()
