#!/usr/bin/env python3
"""Debug label-value parsing to see why only 1 experience is extracted."""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from parsers.work_experience_structured_parser import StructuredWorkExperienceParser

# The actual extracted text from the PDF
work_text = """Work Experience: Company: Wipro
Client: ICICI Bank
Role: Full Stack Developer
Location: Hyderabad, India
Date: Aug 2022 – Present
 Developed microservices using Spring Boot
 Built responsive UI using React
Company: Cognizant
Client: HSBC
Role: Programmer Analyst
Location: Chennai, India
Date: June 2021 – July 2022
 Maintained legacy banking applications
 Implemented API integrations"""

print("🔍 DEBUGGING LABEL-VALUE PARSING")
print("=" * 70)
print("\n📝 Input text:")
print(work_text)
print("\n" + "=" * 70)

parser = StructuredWorkExperienceParser()
experiences = parser.parse_work_section(work_text)

print(f"\n📊 Parsed {len(experiences)} experiences")

for i, exp in enumerate(experiences, 1):
    print(f"\n--- Experience {i} ---")
    print(f"Job Title: {exp.get('job_title')}")
    print(f"Company: {exp.get('company_name')}")
    print(f"Location: {exp.get('location')}")
    print(f"Start Date: {exp.get('start_date')}")
    print(f"End Date: {exp.get('end_date')}")
    print(f"Is Current: {exp.get('is_current')}")
    
    clients = exp.get('clients', [])
    print(f"Clients: {len(clients)}")
    for client in clients:
        print(f"  - {client.get('client_name')}: {len(client.get('descriptions', []))} descriptions")
        for desc in client.get('descriptions', []):
            print(f"    • {desc}")

if len(experiences) != 2:
    print(f"\n❌ ERROR: Expected 2 experiences, got {len(experiences)}")
else:
    print(f"\n✅ Correct number of experiences extracted")
