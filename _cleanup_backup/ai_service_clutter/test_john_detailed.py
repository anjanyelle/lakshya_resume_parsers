#!/usr/bin/env python3
"""
Detailed test to trace where companies are lost
"""

from resume_parser_pipeline import ResumeParser

# Read John's resume
with open('test_John.txt', 'r') as f:
    resume_text = f.read()

print("="*80)
print("🔍 DETAILED TRACE - JOHN'S RESUME")
print("="*80)

# Create parser
parser = ResumeParser("./models/resume-ner-deberta")

# Parse
result = parser.parse(resume_text)

print("\n📊 FINAL RESULT:")
print("-"*80)
print(f"Experience entries: {len(result['experience'])}")
print(f"Education entries: {len(result['education'])}")

print("\n🏢 EXPERIENCE DETAILS:")
for i, exp in enumerate(result['experience'], 1):
    print(f"\n  #{i}:")
    print(f"    Company: '{exp['company']}'")
    print(f"    Role: '{exp['role']}'")
    print(f"    Start: '{exp['start_date']}'")
    print(f"    End: '{exp['end_date']}'")

print("\n🎓 EDUCATION DETAILS:")
for i, edu in enumerate(result['education'], 1):
    print(f"\n  #{i}:")
    print(f"    Degree: '{edu['degree']}'")
    print(f"    Institution: '{edu['institution']}'")
    print(f"    Start: '{edu['start_date']}'")
    print(f"    End: '{edu['end_date']}'")

print("\n" + "="*80)
print("✅ EXPECTED:")
print("="*80)
print("Companies: Chevron Corporation, Sysco Corporation, Conduent Business Services, Mphasis Corporation")
print("Roles: SR Software Engineer Tech Lead, SR Full Stack Engineer, Backend Software Engineer, Software Developer")
print("="*80)
