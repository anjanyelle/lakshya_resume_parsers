#!/usr/bin/env python3
"""
Debug script to see what DeBERTa parser is actually returning.
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from parsers.deberta_ner_parser import DeBERTaNerParser

# Sample work experience text
work_text = """
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
"""

print("🔍 DEBUG: Testing DeBERTa Parser Output")
print("=" * 70)

# Initialize parser
parser = DeBERTaNerParser()

# Extract sections
print("\n📄 Step 1: Extract sections")
sections = parser.extract_target_sections(work_text)
print(f"Work section length: {len(sections['work_experience_text'])} chars")
print(f"Preview: {sections['work_experience_text'][:200]}...")

# Parse sections
print("\n🎯 Step 2: Parse focused sections")
result = parser.parse_focused_sections(sections)

print("\n📊 Step 3: Result structure")
print(f"Keys in result: {list(result.keys())}")

print("\n🏢 Companies:")
print(result.get('companies', []))

print("\n📍 Locations:")
print(result.get('locations', []))

print("\n💼 Job Titles:")
print(result.get('job_titles', []))

print("\n👥 Clients:")
print(result.get('clients', []))

print("\n💼 Work Experience (structured):")
work_exp = result.get('work_experience', [])
print(f"Count: {len(work_exp)}")
for i, exp in enumerate(work_exp, 1):
    print(f"\nExperience {i}:")
    print(f"  Job Title: {exp.get('job_title')}")
    print(f"  Company: {exp.get('company_name')}")
    print(f"  Location: {exp.get('location')}")
    print(f"  Clients: {len(exp.get('clients', []))}")
    for client in exp.get('clients', []):
        print(f"    - {client.get('client_name')}: {len(client.get('descriptions', []))} descriptions")

print("\n✅ Debug complete")
