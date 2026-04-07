#!/usr/bin/env python3
"""Test full pipeline to see where DeBERTa results are getting lost."""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from parsers.master_parser import MasterParser

# Rohan's resume
pdf_path = "/Users/anjanyelle/Desktop/untitled folder 3/Lakshya-LLM-Resume-Parser/backend/src/uploads/164d0638-e69b-4e64-ade5-316745f93d94_Untitled_document__2_.docx"

print("🧪 TESTING FULL PIPELINE")
print("=" * 70)

parser = MasterParser()
result = parser.parse_file(pdf_path, "test-rohan-001")

print("\n📊 FINAL RESULT:")
print("-" * 70)

work_exp = result.get('work_experience', [])
print(f"\nWork Experience: {len(work_exp)} entries")

for i, exp in enumerate(work_exp, 1):
    print(f"\n--- Experience {i} ---")
    print(f"Job Title: {exp.get('job_title', exp.get('role'))}")
    print(f"Company: {exp.get('company_name', exp.get('company'))}")
    print(f"Location: {exp.get('location')}")
    print(f"Start: {exp.get('start_date')}")
    print(f"End: {exp.get('end_date')}")
    print(f"Current: {exp.get('is_current')}")
    
    clients = exp.get('clients', [])
    if clients:
        print(f"Clients: {len(clients)}")
        for client in clients:
            if isinstance(client, dict):
                print(f"  - {client.get('client_name')}")

print("\n" + "=" * 70)
print("🔍 VALIDATION:")
print("=" * 70)

# Check for wrong data
has_errors = False
for exp in work_exp:
    job_title = exp.get('job_title', '')
    company = exp.get('company_name', '')
    
    # Check for skills in job title
    if any(tech in job_title for tech in ['Node.js', 'Express.js', 'MongoDB', 'React', 'Backend:', 'Database:', 'Frontend:']):
        print(f"❌ ERROR: Job title contains technology: {job_title}")
        has_errors = True
    
    # Check for descriptions in company
    if any(word in company for word in ['Developed', 'Built', 'Improved', 'Integrated', 'Database:', 'MongoDB']):
        print(f"❌ ERROR: Company contains description/tech: {company}")
        has_errors = True
    
    # Check for "Date:" in job title
    if 'Date:' in job_title or 'Present' in job_title:
        print(f"❌ ERROR: Job title contains date info: {job_title}")
        has_errors = True

if not has_errors:
    print("✅ No obvious errors detected!")
    
    # Verify correct data
    expected_companies = ['Infosys Ltd', 'TCS']
    expected_titles = ['Full Stack Developer', 'Software Engineer']
    
    actual_companies = [exp.get('company_name') for exp in work_exp]
    actual_titles = [exp.get('job_title') for exp in work_exp]
    
    print(f"\n✅ Companies: {actual_companies}")
    print(f"✅ Job Titles: {actual_titles}")
    
    if 'Infosys Ltd' in actual_companies or 'TCS' in actual_companies:
        print(f"\n🎉 SUCCESS! Correct companies extracted!")
    else:
        print(f"\n⚠️  Expected companies not found")
