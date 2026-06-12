#!/usr/bin/env python3
"""
Test script to process full resume text and display formatted results
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from resume_parser_pipeline import parse_resume
import json


def print_separator(char="=", length=80):
    """Print a separator line"""
    print(char * length)


def print_header(text):
    """Print a formatted header"""
    print_separator()
    print(f"🎯 {text}")
    print_separator()


def print_experience(experience_list):
    """Print formatted work experience"""
    if not experience_list:
        print("❌ No work experience found")
        return
    
    print(f"\n📊 FOUND {len(experience_list)} WORK EXPERIENCE ENTRIES:\n")
    
    for i, exp in enumerate(experience_list, 1):
        print(f"{'─' * 80}")
        print(f"🏢 EXPERIENCE #{i}")
        print(f"{'─' * 80}")
        print(f"  Company:      {exp.get('company', 'N/A')}")
        print(f"  Role:         {exp.get('role', 'N/A')}")
        print(f"  Location:     {exp.get('location', 'N/A')}")
        print(f"  Start Date:   {exp.get('start_date', 'N/A')}")
        print(f"  End Date:     {exp.get('end_date', 'N/A')}")
        print()


def print_education(education_list):
    """Print formatted education"""
    if not education_list:
        print("❌ No education found")
        return
    
    print(f"\n📚 FOUND {len(education_list)} EDUCATION ENTRIES:\n")
    
    for i, edu in enumerate(education_list, 1):
        print(f"{'─' * 80}")
        print(f"🎓 EDUCATION #{i}")
        print(f"{'─' * 80}")
        print(f"  Degree:       {edu.get('degree', 'N/A')}")
        print(f"  Institution:  {edu.get('institution', 'N/A')}")
        print(f"  Start Date:   {edu.get('start_date', 'N/A')}")
        print(f"  End Date:     {edu.get('end_date', 'N/A')}")
        print()


def test_resume(resume_text):
    """Test resume parsing and display results"""
    
    print_header("RESUME PARSING TEST")
    print(f"\n📄 Resume Length: {len(resume_text)} characters")
    print(f"📝 Word Count: {len(resume_text.split())} words\n")
    
    print_separator("─")
    print("🔄 Processing resume...")
    print_separator("─")
    
    # Parse resume
    result = parse_resume(resume_text)
    
    # Display results
    print_header("WORK EXPERIENCE")
    print_experience(result.get('experience', []))
    
    print_header("EDUCATION")
    print_education(result.get('education', []))
    
    print_header("FULL JSON OUTPUT")
    print(json.dumps(result, indent=2))
    print_separator()


if __name__ == "__main__":
    print("\n" * 2)
    print("=" * 80)
    print("🧪 FULL RESUME PARSER TEST")
    print("=" * 80)
    print("\nPaste your full resume text below.")
    print("When done, press Enter, then type 'END' and press Enter again.\n")
    print("─" * 80)
    
    lines = []
    while True:
        try:
            line = input()
            if line.strip().upper() == 'END':
                break
            lines.append(line)
        except EOFError:
            break
    
    resume_text = '\n'.join(lines)
    
    if resume_text.strip():
        test_resume(resume_text)
    else:
        print("\n❌ No resume text provided!")
