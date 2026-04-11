#!/usr/bin/env python3
"""
Test script for Rahul's resume using the new pipeline
"""

from resume_parser_pipeline import parse_resume

# Read Rahul's resume
with open('test_rahul.txt', 'r') as f:
    resume_text = f.read()

print("="*80)
print("🧪 TESTING RAHUL'S RESUME WITH NEW PIPELINE")
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
print("   1. Infosys Ltd")
print("   2. Tata Consultancy Services (TCS)")
print("   3. Wipro Technologies")

print("\n👔 Expected Roles:")
print("   1. Software Developer")
print("   2. Associate Software Engineer")
print("   3. Junior Developer")

print("\n🎓 Expected Education:")
print("   1. Bachelor of Technology (Computer Science) - JNTU Hyderabad")
print("="*80)
