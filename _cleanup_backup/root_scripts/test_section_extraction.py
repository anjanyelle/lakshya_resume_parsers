#!/usr/bin/env python3
"""
Test script to verify SectionExtractor with SectionSplitter integration
Tests on PDF, DOCX, and text files with various heading formats
"""

import sys
import os

# Add ai-service to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ai-service'))

from resume_parser_pipeline import SectionExtractor
from parsers.text_extractor import TextExtractor

def print_section_results(filename, sections):
    """Print section detection results"""
    print(f"\n{'='*80}")
    print(f"📄 FILE: {filename}")
    print(f"{'='*80}")
    
    detected_sections = [k for k, v in sections.items() if v.strip()]
    print(f"\n✅ Detected sections: {detected_sections}")
    print(f"   Total: {len(detected_sections)} sections\n")
    
    for section_name, content in sections.items():
        if content.strip():
            preview = content[:100].replace('\n', ' ')
            print(f"📌 {section_name.upper()}:")
            print(f"   Length: {len(content)} chars")
            print(f"   Preview: {preview}...")
            print()

def test_text_file(filepath):
    """Test on plain text file"""
    print(f"\n🔍 Testing TEXT file: {filepath}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()
    
    sections = SectionExtractor.extract_sections(text)
    print_section_results(os.path.basename(filepath), sections)
    return sections

def test_pdf_file(filepath):
    """Test on PDF file"""
    print(f"\n🔍 Testing PDF file: {filepath}")
    
    extractor = TextExtractor()
    text = extractor.extract_from_pdf(filepath)
    
    sections = SectionExtractor.extract_sections(text)
    print_section_results(os.path.basename(filepath), sections)
    return sections

def test_docx_file(filepath):
    """Test on DOCX file"""
    print(f"\n🔍 Testing DOCX file: {filepath}")
    
    extractor = TextExtractor()
    text = extractor.extract_from_docx(filepath)
    
    sections = SectionExtractor.extract_sections(text)
    print_section_results(os.path.basename(filepath), sections)
    return sections

def main():
    """Run tests on different resume formats"""
    
    print("\n" + "="*80)
    print("🧪 TESTING SECTION EXTRACTION WITH SECTIONSPLITTER INTEGRATION")
    print("="*80)
    
    base_path = os.path.dirname(__file__)
    
    # Test 1: Standard text file with "EXPERIENCE" and "EDUCATION"
    print("\n\n" + "🔬 TEST 1: Standard headings (EXPERIENCE, EDUCATION)")
    print("-" * 80)
    test_text_file(os.path.join(base_path, 'resume1.txt'))
    
    # Test 2: PDF file
    print("\n\n" + "🔬 TEST 2: PDF file")
    print("-" * 80)
    pdf_path = os.path.join(base_path, 'resumes/Python_Developer_Resume.pdf')
    if os.path.exists(pdf_path):
        test_pdf_file(pdf_path)
    else:
        print(f"⚠️ PDF not found: {pdf_path}")
    
    # Test 3: DOCX file
    print("\n\n" + "🔬 TEST 3: DOCX file")
    print("-" * 80)
    docx_path = os.path.join(base_path, 'resumes/Rahul_Sharma_Senior_Python_Engineer.docx')
    if os.path.exists(docx_path):
        test_docx_file(docx_path)
    else:
        print(f"⚠️ DOCX not found: {docx_path}")
    
    # Test 4: Create a test file with non-standard headings
    print("\n\n" + "🔬 TEST 4: Non-standard headings (Professional Background, Career History)")
    print("-" * 80)
    
    test_resume = """
John Smith
john.smith@email.com | (555) 123-4567

PROFESSIONAL BACKGROUND

Senior Software Engineer
Tech Corp Inc.
March 2020 - Present
• Led development of microservices architecture
• Managed team of 5 developers
• Implemented CI/CD pipelines

Software Developer
StartUp Solutions
Jan 2018 - Feb 2020
• Built web applications using React and Node.js
• Optimized database performance

ACADEMIC QUALIFICATIONS

Master of Science in Computer Science
Stanford University
2016 - 2018

Bachelor of Technology
MIT
2012 - 2016
"""
    
    test_file_path = os.path.join(base_path, 'test_nonstandard_headings.txt')
    with open(test_file_path, 'w', encoding='utf-8') as f:
        f.write(test_resume)
    
    test_text_file(test_file_path)
    
    # Clean up test file
    os.remove(test_file_path)
    
    print("\n\n" + "="*80)
    print("✅ ALL TESTS COMPLETED")
    print("="*80)

if __name__ == "__main__":
    main()
