#!/usr/bin/env python3
"""
Test script for John's resume
"""

from resume_parser_pipeline import parse_resume

# Read John's resume
with open('test_John.txt', 'r') as f:
    resume_text = f.read()

print("="*80)
print("🧪 TESTING JOHN'S RESUME")
print("="*80)
print(f"\n📄 Resume Length: {len(resume_text)} characters\n")

result = parse_resume(resume_text)

print("="*80)
print("🏢 WORK EXPERIENCE EXTRACTED:")
print("="*80)

if not result['experience']:
    print("\n❌ No work experience found")
else:
    for i, exp in enumerate(result['experience'], 1):
        print(f"\n📌 Experience #{i}:")
        print(f"   Company:      {exp['company']}")
        print(f"   Role:         {exp['role']}")
        print(f"   Location:     {exp['location']}")
        print(f"   Start Date:   {exp['start_date']}")
        print(f"   End Date:     {exp['end_date']}")

print("\n" + "="*80)
print("🎓 EDUCATION EXTRACTED:")
print("="*80)

if not result['education']:
    print("\n❌ No education found")
else:
    for i, edu in enumerate(result['education'], 1):
        print(f"\n📌 Education #{i}:")
        print(f"   Degree:       {edu['degree']}")
        print(f"   Institution:  {edu['institution']}")
        print(f"   Start Date:   {edu['start_date']}")
        print(f"   End Date:     {edu['end_date']}")

print("\n" + "="*80)
print("📊 SUMMARY:")
print("="*80)
print(f"✅ Work Experience: {len(result['experience'])} entries")
print(f"✅ Education: {len(result['education'])} entries")
print("="*80)

# Show what should be extracted
print("\n" + "="*80)
print("✅ EXPECTED RESULTS:")
print("="*80)
print("\n🏢 Expected Companies:")
print("   1. Chevron Corporation")
print("   2. Sysco Corporation")
print("   3. Conduent Business Services")
print("   4. Mphasis Corporation")

print("\n👔 Expected Roles:")
print("   1. SR Software Engineer Tech Lead")
print("   2. SR Full Stack Engineer")
print("   3. Backend Software Engineer")
print("   4. Software Developer")

print("\n🎓 Expected Education:")
print("   1. Master of Science - University of Houston")
print("   2. Bachelor of Engineering - Visvesvaraya Technological University")
print("="*80)
