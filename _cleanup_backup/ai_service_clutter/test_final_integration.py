#!/usr/bin/env python3
"""
Final integration test - check actual work experience structure in parsed result.
"""

import sys
import os
import json
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from parsers.master_parser import MasterParser

resume_text = """
ANJANA REDDY
Email: anjana.reddy.dev@gmail.com
Phone: +91 98765 43210
Location: Bangalore, India
LinkedIn: linkedin.com/in/anjanareddy
GitHub: github.com/anjanareddy

PROFESSIONAL SUMMARY
Full Stack Developer with 3 years of experience in building scalable web applications using React.js, Node.js, and modern cloud technologies.

TECHNICAL SKILLS
Frontend: React.js, Next.js, JavaScript, HTML5, CSS3, Tailwind CSS
Backend: Node.js, Express.js
Database: MongoDB, MySQL
Cloud: AWS (EC2, S3, Lambda)
Tools: Git, GitHub, Postman, Docker
Other: REST APIs, JWT, Agile

WORK EXPERIENCE
Full Stack Developer
Infosys, Bangalore
June 2023 – Present
Client: Goldman Sachs
Developed internal financial dashboards for risk analysis using React.js
Built secure backend services with Node.js for transaction processing
Implemented authentication and data encryption for sensitive financial data
Client: HSBC
Created customer onboarding platform
Integrated KYC verification APIs
Improved API response time by 25%

Software Developer
Tata Consultancy Services, Hyderabad
May 2022 – May 2023
Client: Walmart
Developed e-commerce modules for product and order management
Built REST APIs for inventory tracking
Improved UI performance using React optimization techniques
Client: Target
Designed admin dashboards for managing large-scale product catalogs
Implemented advanced filtering and search features

Junior Web Developer
Wipro, Hyderabad
April 2021 – April 2022
Client: UnitedHealth Group
Developed patient management system
Built responsive UI for healthcare dashboards
Assisted in backend API development
Client: Pfizer
Worked on internal medical data tracking applications
Fixed bugs and improved system performance

EDUCATION
Bachelor of Technology (B.Tech) in Computer Science
JNTU Hyderabad
2017 – 2021
CGPA: 7.8/10
"""

print("🧪 FINAL INTEGRATION TEST")
print("=" * 70)

parser = MasterParser()
result = parser.parse_text(resume_text, "final-test-001")

print("\n📊 FINAL PARSED RESULT:")
print("=" * 70)

# Check work experience structure
work_exp = result.get('work_experience', [])
print(f"\n💼 Work Experience Count: {len(work_exp)}")

for i, exp in enumerate(work_exp, 1):
    print(f"\n--- Experience {i} ---")
    print(f"Job Title: {exp.get('job_title', exp.get('role', 'N/A'))}")
    print(f"Company: {exp.get('company_name', exp.get('company', 'N/A'))}")
    print(f"Location: {exp.get('location', 'N/A')}")
    print(f"Start Date: {exp.get('start_date', 'N/A')}")
    print(f"End Date: {exp.get('end_date', 'N/A')}")
    print(f"Is Current: {exp.get('is_current', False)}")
    
    # Check for clients
    clients = exp.get('clients', [])
    print(f"Clients: {len(clients)}")
    
    if clients and isinstance(clients, list) and len(clients) > 0:
        if isinstance(clients[0], dict):
            # Structured format
            print("  ✅ STRUCTURED CLIENT FORMAT:")
            for client in clients:
                print(f"    - {client.get('client_name')}: {len(client.get('descriptions', []))} descriptions")
        else:
            # Old format (just strings)
            print("  ⚠️  OLD FORMAT (strings):", clients)

# Check companies, locations, job_titles arrays
print(f"\n🏢 Companies: {result.get('companies', [])}")
print(f"📍 Locations: {result.get('locations', [])}")
print(f"💼 Job Titles: {result.get('job_titles', [])}")

# Check if DeBERTa was used
print(f"\n⏱️  DeBERTa parsing time: {result.get('processing_metrics', {}).get('timing_ms', {}).get('deberta_parsing_ms', 0)}ms")

print("\n" + "=" * 70)
print("✅ Test complete")
