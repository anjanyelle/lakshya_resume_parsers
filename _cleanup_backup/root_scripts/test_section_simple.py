#!/usr/bin/env python3
"""
Simple test script to verify SectionExtractor with SectionSplitter integration
Tests section detection without requiring model dependencies
"""

import sys
import os
import logging

# Configure logging to see warnings
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# Add ai-service to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ai-service'))

# Import only the section extraction components
from parsers.section_splitter import SectionSplitter

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

def test_text_content(name, text):
    """Test section extraction on text content"""
    print(f"\n🔍 Testing: {name}")
    
    # Use SectionSplitter directly
    splitter = SectionSplitter()
    all_sections = splitter.split_sections(text)
    
    # Extract experience and education like SectionExtractor does
    sections = {
        'experience': all_sections.get('experience', ''),
        'education': all_sections.get('education', '')
    }
    
    print_section_results(name, sections)
    
    # Also show all sections detected by SectionSplitter
    print(f"   ℹ️  All sections detected by SectionSplitter: {list(all_sections.keys())}")
    
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
    
    resume1_path = os.path.join(base_path, 'resume1.txt')
    if os.path.exists(resume1_path):
        with open(resume1_path, 'r', encoding='utf-8') as f:
            text1 = f.read()
        test_text_content('resume1.txt (Standard headings)', text1)
    else:
        print(f"⚠️ File not found: {resume1_path}")
    
    # Test 2: Non-standard headings - Professional Background
    print("\n\n" + "🔬 TEST 2: Non-standard headings (Professional Background, Academic Qualifications)")
    print("-" * 80)
    
    test_resume2 = """
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
    
    test_text_content('Non-standard headings (Professional Background)', test_resume2)
    
    # Test 3: Career History variant
    print("\n\n" + "🔬 TEST 3: Non-standard headings (Career History, Educational Background)")
    print("-" * 80)
    
    test_resume3 = """
Jane Doe
jane@example.com

CAREER HISTORY

Lead Developer | Google Inc.
2021 - Present | Mountain View, CA
- Leading cloud infrastructure projects
- Mentoring junior developers

Developer | Microsoft
2018 - 2021 | Seattle, WA
- Built enterprise applications
- Worked on Azure services

EDUCATIONAL BACKGROUND

BS Computer Science
University of California, Berkeley
2014 - 2018
"""
    
    test_text_content('Non-standard headings (Career History)', test_resume3)
    
    # Test 4: Mixed case and punctuation
    print("\n\n" + "🔬 TEST 4: Mixed case with punctuation")
    print("-" * 80)
    
    test_resume4 = """
AMIT PATEL
amit.patel@email.com

Work Experience:

Full Stack Developer
Infosys Ltd
June 2019 - Present
Bangalore, India
• Developed web applications using React.js and Node.js
• Implemented RESTful APIs

Education:

B.Tech in Computer Science
JNTU Hyderabad
2015 - 2019
"""
    
    test_text_content('Mixed case with punctuation', test_resume4)
    
    print("\n\n" + "="*80)
    print("✅ ALL TESTS COMPLETED")
    print("="*80)
    print("\nℹ️  Note: Check the logs above for any fallback warnings")

if __name__ == "__main__":
    main()
