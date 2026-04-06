#!/usr/bin/env python3
"""Test full integration with Karthik's resume to verify structured parser results reach final output."""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from parsers.master_parser import MasterParser

# Karthik's resume text (extracted from PDF)
karthik_text = """Name: Karthik Varma
Contact: 91-90123-45678  karthik.varma.engineer@gmail.com
Based in: Pune, Maharashtra
Portfolio: github.comkarthikvarma-dev
PROFILE
A results-driven Full Stack Engineer with around three years of hands-on experience building
enterprise-grade web applications. Strong background in JavaScript ecosystems, backend
services, and cloud deployments. Delivered solutions for clients in finance, telecom, and retail
sectors.
SKILL SET
 Frontend Technologies: ReactJS, Vue.js, JavaScript, SCSS
 Backend Development: Node.js, Express, REST Services
 Databases: PostgreSQL, MongoDB
 DevOps  Tools: Docker, Jenkins, GitLab CI
 Cloud Platforms: AWS, Azure
PROFESSIONAL EXPERIENCE
Currently working with Tech Mahindra (since August 2023) as a Full Stack Engineer.
Assigned Projects:
For client Barclays
 Developed internal analytics tools for financial reporting
 Designed APIs for secure data exchange
 Worked on improving system scalability
For client ATT
 Built customer-facing dashboards
 Integrated telecom service APIs
 Optimized frontend rendering performance
Previously associated with Accenture (July 2022  July 2023) as Software Engineer.
Client Engagements:
Project handled for Amazon
 Developed backend services for order lifecycle
 Improved database query performance
Worked on module for Best Buy
 Built product listing UI
 Implemented search and recommendation logic
Started career at Mindtree (June 2021  June 2022) as Junior Developer.
Client Work:
Engaged with Cigna
 Developed insurance claim modules
 Created reusable UI components
Worked with Siemens Healthineers
 Maintained healthcare data applications
 Fixed performance issues and bugs
EDUCATIONAL BACKGROUND
Completed Bachelor of Engineering in Information Technology
Savitribai Phule Pune University
Duration: 2017 to 2021
Score: 7.6 CGPA"""

print("🧪 FULL INTEGRATION TEST - Karthik's Resume")
print("=" * 70)

parser = MasterParser()
result = parser.parse_text(karthik_text, "karthik-test-001")

print("\n📊 FINAL PARSED RESULT:")
print("=" * 70)

# Check work experience
work_exp = result.get('work_experience', [])
print(f"\n💼 Work Experience Count: {len(work_exp)}")

if len(work_exp) > 0:
    print("\n✅ WORK EXPERIENCE FOUND!")
    for i, exp in enumerate(work_exp, 1):
        print(f"\n--- Experience {i} ---")
        print(f"Job Title: {exp.get('job_title', exp.get('role', 'N/A'))}")
        print(f"Company: {exp.get('company_name', exp.get('company', 'N/A'))}")
        print(f"Location: {exp.get('location', 'N/A')}")
        
        # Check for clients (structured format)
        clients = exp.get('clients', [])
        if clients and isinstance(clients, list) and len(clients) > 0:
            if isinstance(clients[0], dict):
                print(f"Clients: {len(clients)} (STRUCTURED FORMAT ✅)")
                for client in clients:
                    print(f"  - {client.get('client_name')}: {len(client.get('descriptions', []))} descriptions")
            else:
                print(f"Clients: {clients} (OLD FORMAT ⚠️)")
        else:
            print(f"Clients: None")
else:
    print("\n❌ NO WORK EXPERIENCE FOUND")

# Check extracted entities
print(f"\n🏢 Companies: {result.get('companies', [])}")
print(f"📍 Locations: {result.get('locations', [])}")
print(f"💼 Job Titles: {result.get('job_titles', [])}")

# Check confidence
confidence = result.get('confidence', {})
print(f"\n📈 Overall Confidence: {confidence.get('overall', 0):.2f}")
print(f"Quality Level: {confidence.get('quality_level', 'unknown')}")

print("\n" + "=" * 70)

# Validation
expected_companies = ['Tech Mahindra', 'Accenture', 'Mindtree']
expected_clients = ['Barclays', 'ATT', 'Amazon', 'Best Buy', 'Cigna', 'Siemens Healthineers']

actual_companies = result.get('companies', [])
actual_work_exp_count = len(work_exp)

print("\n🔍 VALIDATION:")
if actual_work_exp_count == 3:
    print(f"✅ Work experience count: {actual_work_exp_count} (expected 3)")
else:
    print(f"❌ Work experience count: {actual_work_exp_count} (expected 3)")

if set(expected_companies).issubset(set(actual_companies)):
    print(f"✅ Companies extracted: {actual_companies}")
else:
    print(f"❌ Companies missing. Expected: {expected_companies}, Got: {actual_companies}")

# Check if structured format (with clients)
has_structured_clients = False
if work_exp:
    for exp in work_exp:
        clients = exp.get('clients', [])
        if clients and isinstance(clients, list) and len(clients) > 0:
            if isinstance(clients[0], dict) and 'client_name' in clients[0]:
                has_structured_clients = True
                break

if has_structured_clients:
    print(f"✅ Structured format with client blocks detected")
else:
    print(f"❌ Structured format NOT detected (old format or no clients)")

print("\n✅ Test complete")
