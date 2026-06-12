#!/usr/bin/env python3
"""
Test script for the TextExtractor class.
Demonstrates usage with different file types and shows quality metrics.
"""

import os
import sys
from pathlib import Path

# Add the parsers directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'parsers'))

from parsers.text_extractor import TextExtractor


def test_text_extractor():
    """Test the TextExtractor with various file types."""
    
    extractor = TextExtractor()
    
    print("🔍 Text Extractor Test Suite")
    print("=" * 50)
    
    # Show supported formats
    print(f"Supported formats: {extractor.get_supported_formats()}")
    print()
    
    # Test files directory
    test_dir = Path("test_files")
    if not test_dir.exists():
        test_dir.mkdir(exist_ok=True)
        print(f"Created test directory: {test_dir}")
        print("Please add test files (PDF, DOCX, TXT) to the test_files directory")
        return
    
    # Find test files
    test_files = []
    for ext in extractor.get_supported_formats():
        test_files.extend(test_dir.glob(f"*{ext}"))
    
    if not test_files:
        print("No test files found. Please add files to test_files directory:")
        for ext in extractor.get_supported_formats():
            print(f"  - sample{ext}")
        return
    
    print(f"Found {len(test_files)} test files:")
    for file in test_files:
        print(f"  - {file.name}")
    print()
    
    # Test each file
    for test_file in test_files:
        print(f"📄 Processing: {test_file.name}")
        print("-" * 30)
        
        try:
            result = extractor.extract(str(test_file))
            
            print(f"✅ Extraction successful!")
            print(f"   Method: {result['method']}")
            print(f"   Word count: {result['word_count']}")
            print(f"   Quality score: {result['quality_score']:.2f}/1.00")
            
            # Show text preview
            text_preview = result['text'][:200] + "..." if len(result['text']) > 200 else result['text']
            print(f"   Text preview: {text_preview}")
            
            # Quality assessment
            if result['quality_score'] > 0.8:
                print("   🟢 Quality: Excellent")
            elif result['quality_score'] > 0.6:
                print("   🟡 Quality: Good")
            elif result['quality_score'] > 0.4:
                print("   🟠 Quality: Fair")
            else:
                print("   🔴 Quality: Poor")
            
        except Exception as e:
            print(f"❌ Extraction failed: {str(e)}")
        
        print()


def test_text_cleaning():
    """Test the text cleaning functionality."""
    
    extractor = TextExtractor()
    
    print("🧹 Text Cleaning Test")
    print("=" * 30)
    
    # Test text with various issues
    test_text = """
    John Doe
    Email: john.doe@example.com
    Phone: (555) 123-4567
    
    Education:
    Bachelor of Science in Computer Science
    
    Experience:
    Senior Software Engineer at Tech Corp
    
    Skills:    Python,    Java,   JavaScript
    
    Contact: +1-555-987-6543
    """
    
    print("Original text:")
    print(repr(test_text))
    print()
    
    cleaned_text = extractor.clean_text(test_text)
    
    print("Cleaned text:")
    print(repr(cleaned_text))
    print()
    
    print("Formatted cleaned text:")
    print(cleaned_text)
    print()


def create_sample_files():
    """Create sample test files for testing."""
    
    test_dir = Path("test_files")
    test_dir.mkdir(exist_ok=True)
    
    # Create sample TXT file
    txt_file = test_dir / "sample_resume.txt"
    with open(txt_file, 'w', encoding='utf-8') as f:
        f.write("""JOHN DOE
123 Main Street, Anytown, USA 12345
(555) 123-4567 | john.doe@example.com | linkedin.com/in/johndoe

PROFESSIONAL SUMMARY
Experienced software engineer with 5+ years in full-stack development.
Proficient in Python, JavaScript, and cloud technologies.

EDUCATION
Bachelor of Science in Computer Science
University of Technology, 2018-2022

EXPERIENCE
Senior Software Engineer | Tech Corp | 2022-Present
- Developed scalable web applications
- Led team of 3 junior developers
- Improved system performance by 40%

Software Engineer | Startup Inc | 2020-2022
- Built RESTful APIs
- Implemented CI/CD pipelines
- Maintained production systems

SKILLS
Programming: Python, JavaScript, Java, TypeScript
Frameworks: React, Node.js, Django, Flask
Cloud: AWS, Docker, Kubernetes
Databases: PostgreSQL, MongoDB, Redis
""")
    
    print(f"Created sample TXT file: {txt_file}")
    
    # Note: PDF and DOCX files need to be created manually
    print("Note: Please add sample PDF and DOCX files manually to test_files directory")


if __name__ == "__main__":
    print("🚀 AI Service Text Extractor Tests")
    print("=" * 60)
    print()
    
    # Check if test files exist, create sample if needed
    test_dir = Path("test_files")
    if not any(test_dir.glob("*.pdf")) and not any(test_dir.glob("*.docx")) and not any(test_dir.glob("*.txt")):
        print("No test files found. Creating sample files...")
        create_sample_files()
        print()
    
    # Run tests
    test_text_cleaning()
    test_text_extractor()
    
    print("🎉 Test suite completed!")
    print()
    print("To install dependencies:")
    print("  pip install -r requirements.txt")
    print()
    print("To install Tesseract OCR (required for PDF OCR):")
    print("  macOS: brew install tesseract")
    print("  Ubuntu: sudo apt-get install tesseract-ocr")
    print("  Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki")
