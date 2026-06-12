#!/usr/bin/env python3
"""
Test script to verify heuristic section header detection
Tests non-standard headings to see which are caught by keywords vs heuristics
"""

import sys
import os
import logging

# Configure logging to see all detection messages
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)

# Add ai-service to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ai-service'))

from parsers.section_splitter import SectionSplitter

def test_heuristic_detection():
    """Test non-standard section headings"""
    
    # Create test resume with non-standard headings
    test_resume = """
John Doe
john.doe@email.com | (555) 123-4567

MY PROFESSIONAL JOURNEY

Senior Software Engineer
Tech Corp Inc.
March 2020 - Present
• Led development of microservices architecture
• Managed team of 5 developers

Software Developer
StartUp Solutions
Jan 2018 - Feb 2020
• Built web applications using React and Node.js

Where I Have Worked

Consultant | Freelance
2017 - 2018
• Provided consulting services to various clients

THINGS I KNOW

Python, JavaScript, React, Node.js, AWS, Docker, Kubernetes
Machine Learning, Data Analysis, Cloud Architecture

Academic Life

Master of Science in Computer Science
Stanford University
2016 - 2018

Bachelor of Technology
MIT
2012 - 2016

What I Built

E-commerce Platform - Built scalable platform with 100k users
AI Chatbot - Developed NLP-based customer service bot
Mobile App - Created cross-platform app with React Native
"""
    
    print("\n" + "="*80)
    print("🧪 TESTING HEURISTIC SECTION HEADER DETECTION")
    print("="*80)
    
    print("\n📋 Test Headings:")
    print("1. MY PROFESSIONAL JOURNEY")
    print("2. Where I Have Worked")
    print("3. THINGS I KNOW")
    print("4. Academic Life")
    print("5. What I Built")
    
    print("\n" + "="*80)
    print("🔍 RUNNING SECTION SPLITTER")
    print("="*80 + "\n")
    
    # Create splitter and process
    splitter = SectionSplitter()
    sections = splitter.split_sections(test_resume)
    
    print("\n" + "="*80)
    print("📊 RESULTS")
    print("="*80)
    
    print(f"\n✅ Detected {len(sections)} sections:")
    for section_name in sections.keys():
        content_preview = sections[section_name][:100].replace('\n', ' ')
        print(f"   • {section_name}: {content_preview}...")
    
    print("\n" + "="*80)
    print("📈 DETECTION ANALYSIS")
    print("="*80)
    
    # Analyze which headings were detected
    detected_headings = {
        'MY PROFESSIONAL JOURNEY': None,
        'Where I Have Worked': None,
        'THINGS I KNOW': None,
        'Academic Life': None,
        'What I Built': None
    }
    
    # Map detected sections to original headings
    section_mapping = {
        'experience': ['MY PROFESSIONAL JOURNEY', 'Where I Have Worked'],
        'skills': ['THINGS I KNOW'],
        'education': ['Academic Life'],
        'projects': ['What I Built']
    }
    
    print("\n🎯 Expected Detections:")
    print("   • MY PROFESSIONAL JOURNEY → should map to 'experience' (partial match: 'professional')")
    print("   • Where I Have Worked → should map to 'experience' (partial match: 'work')")
    print("   • THINGS I KNOW → should map to 'skills' or custom section (no direct match)")
    print("   • Academic Life → should map to 'education' (partial match: 'academic')")
    print("   • What I Built → should map to 'projects' or custom section (no direct match)")
    
    print("\n✅ Actual Detections:")
    for section_name, content in sections.items():
        if section_name != 'other':
            print(f"\n   📌 Section: '{section_name}'")
            print(f"      Content length: {len(content)} chars")
            print(f"      First 150 chars: {content[:150].replace(chr(10), ' ')}...")
    
    print("\n" + "="*80)
    print("🏁 TEST COMPLETE")
    print("="*80)
    
    # Summary
    print("\n📝 SUMMARY:")
    print("   Check the logs above to see:")
    print("   • Which headings were detected by keyword matching (✅ Detected header)")
    print("   • Which were detected by heuristics (✅ Detected unknown section header)")
    print("   • Which used partial matching (🔍 Partial match)")
    print("   • Which created custom sections (📝 Creating custom section)")
    print("   • Which were missed (no log entry)")

if __name__ == "__main__":
    test_heuristic_detection()
