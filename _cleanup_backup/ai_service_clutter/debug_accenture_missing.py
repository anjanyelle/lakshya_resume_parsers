#!/usr/bin/env python3
"""Debug why Accenture experience is missing."""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from parsers.work_experience_structured_parser import StructuredWorkExperienceParser

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
Developed backend services using Java and Spring Framework"""

parser = StructuredWorkExperienceParser()
lines = work_text.split('\n')

print("🔍 DEBUGGING LINE BY LINE")
print("=" * 70)

for i, line in enumerate(lines):
    line_stripped = line.strip()
    if not line_stripped:
        continue
    
    next_line = lines[i + 1].strip() if i + 1 < len(lines) else ''
    
    is_title = parser._is_job_title_line(line_stripped)
    is_next_title = parser._is_job_title_line(next_line) if next_line else False
    is_start = is_title or is_next_title
    
    marker = "🚀 START" if is_start else "   "
    print(f"{i:3d} {marker} | {line_stripped[:60]}")

print("\n" + "=" * 70)
print("📊 PARSING:")
print("=" * 70)

experiences = parser.parse_work_section(work_text)
print(f"\n✅ Found {len(experiences)} experiences\n")

for i, exp in enumerate(experiences, 1):
    print(f"{i}. {exp.get('job_title')} at {exp.get('company_name')}")
