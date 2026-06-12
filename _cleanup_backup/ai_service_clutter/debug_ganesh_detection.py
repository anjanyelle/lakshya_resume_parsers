#!/usr/bin/env python3
"""Debug line detection for Ganesh's resume."""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from parsers.work_experience_structured_parser import StructuredWorkExperienceParser

work_text = """PROFESSIONAL EXPERIENCE
Visa Forster City, CA
Site Reliability  DevOps Engineer Dec 2022  Current
Environment: Git, GitLab, GitHub, CICD, GitHub Actions, TypeScript, Docker
Implemented Kubernetes and AWS EKS to orchestrate containerized financial applications

Target Minneapolis, MN
Senior DevOps Engineer Jan 2020  Nov 2022
Environment: Jenkins, Docker, Kubernetes, AWS
Built CICD pipelines for microservices architecture"""

parser = StructuredWorkExperienceParser()
lines = work_text.split('\n')

print("🔍 LINE-BY-LINE DETECTION")
print("=" * 70)

for i, line in enumerate(lines):
    line_stripped = line.strip()
    if not line_stripped:
        continue
    
    next_line = lines[i + 1].strip() if i + 1 < len(lines) else ''
    
    is_title = parser._is_job_title_line(line_stripped)
    is_date = parser._is_date_line(line_stripped)
    is_next_title = parser._is_job_title_line(next_line) if next_line else False
    
    # Check if next line has title + date
    has_title_and_date = False
    if next_line and parser._is_date_line(next_line):
        for keyword in ['developer', 'engineer', 'architect', 'manager', 'lead']:
            if keyword in next_line.lower():
                has_title_and_date = True
                break
    
    is_start = is_title or is_next_title or has_title_and_date
    
    marker = "🚀" if is_start else "  "
    title_mark = "T" if is_title else " "
    date_mark = "D" if is_date else " "
    next_mark = "N" if is_next_title else " "
    combo_mark = "C" if has_title_and_date else " "
    
    print(f"{i:2d} {marker} [{title_mark}{date_mark}{next_mark}{combo_mark}] {line_stripped[:55]}")

print("\n" + "=" * 70)
print("📊 FULL PARSE:")
print("=" * 70)

experiences = parser.parse_work_section(work_text)
print(f"\nFound {len(experiences)} experiences\n")

for i, exp in enumerate(experiences, 1):
    print(f"{i}. {exp.get('job_title')} at {exp.get('company_name')}")
    print(f"   Location: {exp.get('location')}")
    print(f"   Dates: {exp.get('start_date')} to {exp.get('end_date')}")
    print(f"   Current: {exp.get('is_current')}")
