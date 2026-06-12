#!/usr/bin/env python3
"""
Direct test of DeBERTa model on sample resume text.
This bypasses the upload flow to test the model directly.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from parsers.deberta_ner_parser import DeBERTaNerParser
import logging

logging.basicConfig(level=logging.INFO)

# Sample work experience text from Anjan's resume
WORK_EXPERIENCE_TEXT = """
Full Stack Developer	Nov 2024 – Present
Lalataksha Consulting Services Pvt. Ltd. | Hyderabad, India
AI Resume Parser & Candidate Intelligence System
Built an end-to-end AI-powered resume parsing system to extract structured candidate data including skills, experience, and education.

Frontend Developer	Oct 2022 – Nov 2024
OxyLoans (FinTech – P2P Lending Platform) | Hyderabad, India
Developed a multi-role FinTech platform with secure authentication and role-based routing.
Integrated Cashfree and Getepay payment gateways for real-time transaction processing.

Junior Frontend Developer	Jan 2022 – Sep 2022
AskOxy.ai – Grocery Delivery Platform | Hyderabad, India
Developed a Progressive Web App (PWA) with cart, checkout, and real-time order tracking features.
Integrated Firebase Authentication and Firestore for real-time data sync and user management.
"""

def main():
    print("=" * 80)
    print("TESTING DeBERTa MODEL DIRECTLY")
    print("=" * 80)
    
    # Initialize parser
    parser = DeBERTaNerParser()
    
    if not parser.is_loaded:
        print("❌ DeBERTa model not loaded!")
        return
    
    print("✅ DeBERTa model loaded successfully")
    print(f"Model path: {parser.model_path}")
    print(f"Number of labels: {len(parser.id_to_label)}")
    print()
    
    # Test parsing
    print("Testing work experience text:")
    print("-" * 80)
    print(WORK_EXPERIENCE_TEXT[:200] + "...")
    print("-" * 80)
    print()
    
    # Parse the section
    sections = {
        'work_experience_text': WORK_EXPERIENCE_TEXT,
        'education_text': ''
    }
    
    result = parser.parse_focused_sections(sections)
    
    print("\n" + "=" * 80)
    print("RESULTS")
    print("=" * 80)
    print(f"Companies: {result.get('companies', [])}")
    print(f"Job Titles: {result.get('job_titles', [])}")
    print(f"Locations: {result.get('locations', [])}")
    print(f"Work Experiences: {len(result.get('work_experience', []))}")
    print()
    
    for i, exp in enumerate(result.get('work_experience', []), 1):
        print(f"\nExperience {i}:")
        print(f"  Company: {exp.get('company_name')}")
        print(f"  Role: {exp.get('job_title')}")
        print(f"  Start: {exp.get('start_date')}")
        print(f"  End: {exp.get('end_date')}")
        print(f"  Current: {exp.get('is_current')}")

if __name__ == '__main__':
    main()
