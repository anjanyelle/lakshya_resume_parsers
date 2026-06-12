#!/usr/bin/env python3
"""Debug why structured parser is failing on Aditya's resume."""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from parsers.work_experience_structured_parser import StructuredWorkExperienceParser

# Simulate the work experience section
work_text = """PROFESSIONAL EXPERIENCE
Infosys Ltd
Lead Full Stack AI Engineer
Jan 2020 – Present
Architected and developed AI-driven recommendation systems using deep learning models improving customer engagement by 35
Designed microservices architecture using Node.js, Spring Boot, and Docker containers
Built real-time analytics pipelines using Kafka and Apache Spark for processing millions of events daily

Accenture
Senior Software Engineer
June 2016 – Dec 2019
Developed enterprise web applications using Angular and React.js
Built fraud detection systems using machine learning algorithms

Tata Consultancy Services (TCS)
Software Engineer
July 2013 – May 2016
Developed backend services using Java and Spring Framework
Built internal dashboards and reporting tools"""

print("🔍 DEBUGGING PARSER DETECTION")
print("=" * 70)

parser = StructuredWorkExperienceParser()

# Test line detection
test_lines = [
    "PROFESSIONAL EXPERIENCE",
    "Infosys Ltd",
    "Lead Full Stack AI Engineer",
    "Jan 2020 – Present",
    "Architected and developed AI-driven recommendation systems",
    "Accenture",
    "Senior Software Engineer",
    "June 2016 – Dec 2019"
]

print("\n📊 LINE DETECTION TEST:")
print("-" * 70)
for line in test_lines:
    is_title = parser._is_job_title_line(line)
    is_date = parser._is_date_line(line)
    print(f"{'✅' if is_title else '❌'} Title | {'✅' if is_date else '❌'} Date | {line}")

print("\n" + "=" * 70)
print("📊 PARSING FULL TEXT:")
print("-" * 70)

experiences = parser.parse_work_section(work_text)
print(f"\n✅ Found {len(experiences)} experiences")

for i, exp in enumerate(experiences, 1):
    print(f"\n--- Experience {i} ---")
    print(f"Job Title: {exp.get('job_title')}")
    print(f"Company: {exp.get('company_name')}")
    print(f"Location: {exp.get('location')}")
    print(f"Start: {exp.get('start_date')}")
    print(f"End: {exp.get('end_date')}")
    print(f"Current: {exp.get('is_current')}")
