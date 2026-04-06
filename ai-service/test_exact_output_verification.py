#!/usr/bin/env python3
"""Verify exact JSON output structure matches expected format."""

import sys
import json
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from parsers.master_parser import MasterParser

# Exact resume text from user
resume_text = """Full Stack Developer
Infosys, Bangalore
June 2023 – Present
Client: Goldman Sachs
  - Developed internal financial dashboards
Client: HSBC
  - Created customer onboarding platform

Software Developer
Tata Consultancy Services, Hyderabad
May 2022 – May 2023
Client: Walmart
  - Developed e-commerce modules"""

# Expected output structure
expected_output = {
    "work_experience": [
        {
            "job_title": "Full Stack Developer",
            "company_name": "Infosys",
            "location": "Bangalore",
            "start_date": "2023-06-01",
            "end_date": None,
            "is_current": True,
            "clients": [
                {
                    "client_name": "Goldman Sachs",
                    "descriptions": ["Developed internal financial dashboards"]
                },
                {
                    "client_name": "HSBC",
                    "descriptions": ["Created customer onboarding platform"]
                }
            ]
        },
        {
            "job_title": "Software Developer",
            "company_name": "Tata Consultancy Services",
            "location": "Hyderabad",
            "start_date": "2022-05-01",
            "end_date": "2023-05-01",
            "is_current": False,
            "clients": [
                {
                    "client_name": "Walmart",
                    "descriptions": ["Developed e-commerce modules"]
                }
            ]
        }
    ]
}

print("🧪 EXACT OUTPUT VERIFICATION TEST")
print("=" * 70)

# Parse the resume
parser = MasterParser()
result = parser.parse_text(resume_text, "exact-output-test-001")

# Extract work experience
actual_work_experience = result.get('work_experience', [])

print(f"\n📊 ACTUAL OUTPUT:")
print(json.dumps({"work_experience": actual_work_experience}, indent=2, default=str))

print(f"\n📋 EXPECTED OUTPUT:")
print(json.dumps(expected_output, indent=2))

print(f"\n🔍 DETAILED COMPARISON:")
print("=" * 70)

# Compare counts
expected_count = len(expected_output['work_experience'])
actual_count = len(actual_work_experience)

if actual_count != expected_count:
    print(f"❌ MISMATCH: Work experience count")
    print(f"   Expected: {expected_count}")
    print(f"   Actual: {actual_count}")
else:
    print(f"✅ Work experience count: {actual_count}")

# Compare each experience
for i, (expected_exp, actual_exp) in enumerate(zip(expected_output['work_experience'], actual_work_experience), 1):
    print(f"\n--- Experience {i} ---")
    
    # Check job_title
    expected_title = expected_exp['job_title']
    actual_title = actual_exp.get('job_title', actual_exp.get('role'))
    if actual_title != expected_title:
        print(f"❌ job_title mismatch:")
        print(f"   Expected: '{expected_title}'")
        print(f"   Actual: '{actual_title}'")
    else:
        print(f"✅ job_title: '{actual_title}'")
    
    # Check company_name
    expected_company = expected_exp['company_name']
    actual_company = actual_exp.get('company_name', actual_exp.get('company'))
    if actual_company != expected_company:
        print(f"❌ company_name mismatch:")
        print(f"   Expected: '{expected_company}'")
        print(f"   Actual: '{actual_company}'")
    else:
        print(f"✅ company_name: '{actual_company}'")
    
    # Check location
    expected_location = expected_exp['location']
    actual_location = actual_exp.get('location')
    if actual_location != expected_location:
        print(f"❌ location mismatch:")
        print(f"   Expected: '{expected_location}'")
        print(f"   Actual: '{actual_location}'")
    else:
        print(f"✅ location: '{actual_location}'")
    
    # Check dates
    expected_start = expected_exp['start_date']
    actual_start = actual_exp.get('start_date')
    if actual_start != expected_start:
        print(f"⚠️  start_date mismatch:")
        print(f"   Expected: '{expected_start}'")
        print(f"   Actual: '{actual_start}'")
    else:
        print(f"✅ start_date: '{actual_start}'")
    
    expected_end = expected_exp['end_date']
    actual_end = actual_exp.get('end_date')
    if actual_end != expected_end:
        print(f"⚠️  end_date mismatch:")
        print(f"   Expected: '{expected_end}'")
        print(f"   Actual: '{actual_end}'")
    else:
        print(f"✅ end_date: '{actual_end}'")
    
    # Check is_current
    expected_current = expected_exp['is_current']
    actual_current = actual_exp.get('is_current')
    if actual_current != expected_current:
        print(f"❌ is_current mismatch:")
        print(f"   Expected: {expected_current}")
        print(f"   Actual: {actual_current}")
    else:
        print(f"✅ is_current: {actual_current}")
    
    # Check clients
    expected_clients = expected_exp['clients']
    actual_clients = actual_exp.get('clients', [])
    
    if len(actual_clients) != len(expected_clients):
        print(f"❌ clients count mismatch:")
        print(f"   Expected: {len(expected_clients)} clients")
        print(f"   Actual: {len(actual_clients)} clients")
    else:
        print(f"✅ clients count: {len(actual_clients)}")
    
    # Check each client
    for j, (expected_client, actual_client) in enumerate(zip(expected_clients, actual_clients), 1):
        expected_client_name = expected_client['client_name']
        actual_client_name = actual_client.get('client_name') if isinstance(actual_client, dict) else str(actual_client)
        
        if actual_client_name != expected_client_name:
            print(f"   ❌ Client {j} name mismatch:")
            print(f"      Expected: '{expected_client_name}'")
            print(f"      Actual: '{actual_client_name}'")
        else:
            print(f"   ✅ Client {j}: '{actual_client_name}'")
        
        # Check descriptions
        if isinstance(actual_client, dict):
            expected_descs = expected_client['descriptions']
            actual_descs = actual_client.get('descriptions', [])
            
            if len(actual_descs) != len(expected_descs):
                print(f"      ❌ Descriptions count mismatch:")
                print(f"         Expected: {len(expected_descs)}")
                print(f"         Actual: {len(actual_descs)}")
            else:
                print(f"      ✅ Descriptions: {len(actual_descs)}")
                
                # Check description content
                for k, (expected_desc, actual_desc) in enumerate(zip(expected_descs, actual_descs), 1):
                    if actual_desc.strip() != expected_desc.strip():
                        print(f"         ⚠️  Description {k} mismatch:")
                        print(f"            Expected: '{expected_desc}'")
                        print(f"            Actual: '{actual_desc}'")

print("\n" + "=" * 70)
print("✅ Test complete")
