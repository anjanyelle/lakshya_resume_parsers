#!/usr/bin/env python3
"""Test the fixed label-value format parser."""

import sys
import json
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from parsers.master_parser import MasterParser

# Test with one of the problematic PDFs
pdf_path = "/Users/anjanyelle/Desktop/untitled folder 3/Lakshya-LLM-Resume-Parser/backend/src/uploads/e263d46b-69c8-4d0f-8b3d-b1492a3ac082_Untitled_document__4_.pdf"

print("🧪 TESTING LABEL-VALUE FORMAT FIX")
print("=" * 70)

if not Path(pdf_path).exists():
    print(f"❌ File not found: {pdf_path}")
    sys.exit(1)

parser = MasterParser()
result = parser.parse_file(pdf_path, "label-value-test-001")

print("\n📊 PARSED WORK EXPERIENCE:")
print("=" * 70)

work_exp = result.get('work_experience', [])
print(f"\nTotal experiences: {len(work_exp)}")

for i, exp in enumerate(work_exp, 1):
    print(f"\n--- Experience {i} ---")
    print(f"Job Title: {exp.get('job_title', exp.get('role'))}")
    print(f"Company: {exp.get('company_name', exp.get('company'))}")
    print(f"Location: {exp.get('location')}")
    print(f"Start Date: {exp.get('start_date')}")
    print(f"End Date: {exp.get('end_date')}")
    print(f"Is Current: {exp.get('is_current')}")
    
    clients = exp.get('clients', [])
    print(f"Clients: {len(clients)}")
    for j, client in enumerate(clients, 1):
        if isinstance(client, dict):
            print(f"  {j}. {client.get('client_name')}")
            descs = client.get('descriptions', [])
            print(f"     Descriptions: {len(descs)}")
            for desc in descs:
                print(f"     - {desc}")

print("\n" + "=" * 70)
print("🔍 VALIDATION:")
print("=" * 70)

# Check for the bug
has_bug = False
for exp in work_exp:
    job_title = exp.get('job_title', '')
    company = exp.get('company_name', '')
    
    if 'Role:' in job_title:
        print(f"❌ BUG FOUND: job_title still contains 'Role:' prefix: {job_title}")
        has_bug = True
    elif 'Location:' in company:
        print(f"❌ BUG FOUND: company_name contains 'Location:' prefix: {company}")
        has_bug = True
    elif 'Company:' in company:
        print(f"❌ BUG FOUND: company_name contains 'Company:' prefix: {company}")
        has_bug = True

if not has_bug:
    print("✅ No label prefixes found - FIX SUCCESSFUL!")
    
    # Verify correct data
    expected_companies = ['Wipro', 'Cognizant']
    expected_titles = ['Full Stack Developer', 'Programmer Analyst']
    expected_clients = ['ICICI Bank', 'HSBC']
    
    actual_companies = [exp.get('company_name') for exp in work_exp]
    actual_titles = [exp.get('job_title') for exp in work_exp]
    
    print(f"\n✅ Companies: {actual_companies}")
    print(f"✅ Job Titles: {actual_titles}")
    
    # Check clients
    all_clients = []
    for exp in work_exp:
        for client in exp.get('clients', []):
            if isinstance(client, dict):
                all_clients.append(client.get('client_name'))
    
    print(f"✅ Clients: {all_clients}")
    
    # Verify dates
    if work_exp[0].get('start_date'):
        print(f"✅ Dates extracted: {work_exp[0].get('start_date')} to {work_exp[0].get('end_date')}")
    else:
        print(f"⚠️  Dates not extracted")

print("\n✅ Test complete")
