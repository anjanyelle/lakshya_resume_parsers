#!/usr/bin/env python3
"""Test parsing of Karthik's resume text."""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from parsers.deberta_ner_parser import DeBERTaNerParser

# Actual extracted text from Karthik's PDF
text = """Name: Karthik Varma
Contact: 91-90123-45678  karthik.varma.engineer@gmail.com
Based in: Pune, Maharashtra
Portfolio: github.comkarthikvarma-dev
PROFILE
A results-driven Full Stack Engineer with around three years of hands-on experience building
enterprise-grade web applications. Strong background in JavaScript ecosystems, backend
services, and cloud deployments. Delivered solutions for clients in finance, telecom, and retail
sectors. SKILL SET
 Frontend Technologies: ReactJS, Vue.js, JavaScript, SCSS
 Backend Development: Node.js, Express, REST Services
 Databases: PostgreSQL, MongoDB
 DevOps  Tools: Docker, Jenkins, GitLab CI
 Cloud Platforms: AWS, Azure
PROFESSIONAL EXPERIENCE
Currently working with Tech Mahindra (since August 2023) as a Full Stack Engineer. Assigned Projects: For client Barclays
 Developed internal analytics tools for financial reporting
 Designed APIs for secure data exchange
 Worked on improving system scalability
For client ATT
 Built customer-facing dashboards
 Integrated telecom service APIs
 Optimized frontend rendering performance
Previously associated with Accenture (July 2022  July 2023) as Software Engineer. Client Engagements: Project handled for Amazon
 Developed backend services for order lifecycle
 Improved database query performance
Worked on module for Best Buy
 Built product listing UI
 Implemented search and recommendation logic
Started career at Mindtree (June 2021  June 2022) as Junior Developer. Client Work: Engaged with Cigna
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

print("🔍 Testing Karthik's Resume Parsing")
print("=" * 70)

parser = DeBERTaNerParser()

# Extract sections
sections = parser.extract_target_sections(text)
print(f"\n📄 Work Experience Section: {len(sections['work_experience_text'])} chars")
print("\nPreview:")
print(sections['work_experience_text'][:500])

# Parse with structured parser
print("\n" + "=" * 70)
print("🎯 Parsing Work Experience...")
result = parser.parse_focused_sections(sections)

print(f"\n📊 Results:")
print(f"Companies: {result.get('companies', [])}")
print(f"Locations: {result.get('locations', [])}")
print(f"Job Titles: {result.get('job_titles', [])}")
print(f"Clients: {result.get('clients', [])}")
print(f"Work Experiences: {len(result.get('work_experience', []))}")

for i, exp in enumerate(result.get('work_experience', []), 1):
    print(f"\n--- Experience {i} ---")
    print(f"Job Title: {exp.get('job_title')}")
    print(f"Company: {exp.get('company_name')}")
    print(f"Location: {exp.get('location')}")
    print(f"Clients: {len(exp.get('clients', []))}")
    for client in exp.get('clients', []):
        print(f"  - {client.get('client_name')}: {len(client.get('descriptions', []))} descriptions")

print("\n✅ Test complete")
