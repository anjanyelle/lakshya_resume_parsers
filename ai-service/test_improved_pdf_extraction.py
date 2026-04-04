#!/usr/bin/env python3
"""
Test improved multi-tier PDF extraction strategy.
Verifies: pdfplumber → pymupdf → OCR fallback chain.
"""

import sys
import os
from pathlib import Path

# Add the ai-service directory to path
sys.path.append(str(Path(__file__).parent))

from parsers.text_extractor import TextExtractor

def test_pdf_extraction():
    """Test the improved PDF extraction with Anjana's resume."""
    
    # Path to Anjana's resume (from the backend uploads)
    resume_path = "/Users/anjanyelle/Desktop/untitled folder 3/Lakshya-LLM-Resume-Parser/backend/src/uploads/7b21e42c-d83c-458b-8dfe-d1901f280ceb_Untitled_document-4.pdf"
    
    print("🧪 TESTING IMPROVED PDF EXTRACTION")
    print("=" * 70)
    print(f"📄 File: {Path(resume_path).name}")
    print()
    
    if not os.path.exists(resume_path):
        print(f"❌ Resume file not found: {resume_path}")
        print("\nPlease provide a valid PDF path to test.")
        return False
    
    try:
        # Initialize extractor
        extractor = TextExtractor()
        
        # Extract text with new multi-tier strategy
        print("🔍 Extracting text with multi-tier strategy...")
        print("   Tier 1: pdfplumber (primary)")
        print("   Tier 2: pymupdf (if < 200 chars)")
        print("   Tier 3: OCR (if < 200 chars)")
        print()
        
        result = extractor.extract(resume_path)
        
        # Display results
        print("=" * 70)
        print("📊 EXTRACTION RESULTS")
        print("=" * 70)
        print(f"✅ Method Used: {result['method']}")
        print(f"📏 Character Count: {result['char_count']}")
        print(f"📝 Word Count: {result['word_count']}")
        print(f"⭐ Quality Score: {result['quality_score']:.2f}")
        print()
        
        # Show text preview
        text = result['text']
        print("📄 TEXT PREVIEW (first 500 chars):")
        print("-" * 70)
        print(text[:500])
        print("-" * 70)
        print()
        
        # Validation checks
        print("🔍 VALIDATION CHECKS:")
        print("-" * 70)
        
        # Check 1: Character count
        if result['char_count'] >= 200:
            print(f"✅ Character count: {result['char_count']} (>= 200)")
        else:
            print(f"⚠️  Character count: {result['char_count']} (< 200 - may need OCR)")
        
        # Check 2: Expected content
        expected_keywords = ['anjana', 'reddy', 'developer', 'react', 'node', 'infosys']
        found_keywords = []
        missing_keywords = []
        
        text_lower = text.lower()
        for keyword in expected_keywords:
            if keyword in text_lower:
                found_keywords.append(keyword)
            else:
                missing_keywords.append(keyword)
        
        print(f"✅ Found keywords: {found_keywords}")
        if missing_keywords:
            print(f"⚠️  Missing keywords: {missing_keywords}")
        
        # Check 3: Text loss comparison
        original_expected_length = 2233  # From the original resume
        text_loss_percentage = ((original_expected_length - result['char_count']) / original_expected_length) * 100
        
        print(f"📊 Text loss: {text_loss_percentage:.1f}% (was 95.17% with old method)")
        
        if text_loss_percentage < 50:
            print("✅ EXCELLENT: Text loss < 50%")
        elif text_loss_percentage < 75:
            print("⚠️  MODERATE: Text loss 50-75%")
        else:
            print("❌ POOR: Text loss > 75%")
        
        print()
        
        # Summary
        print("=" * 70)
        print("📈 IMPROVEMENT SUMMARY")
        print("=" * 70)
        print(f"Old method: pymupdf only → 95.17% text loss")
        print(f"New method: {result['method']} → {text_loss_percentage:.1f}% text loss")
        print(f"Improvement: {95.17 - text_loss_percentage:.1f}% better!")
        print()
        
        # Success criteria
        success = (
            result['char_count'] >= 200 and
            len(found_keywords) >= 4 and
            text_loss_percentage < 75
        )
        
        if success:
            print("🎉 PDF EXTRACTION TEST PASSED!")
            return True
        else:
            print("⚠️  PDF extraction needs improvement")
            return False
        
    except Exception as e:
        print(f"❌ Error during PDF extraction: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_pdf_extraction()
    if not success:
        sys.exit(1)
