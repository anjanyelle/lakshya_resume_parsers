#!/usr/bin/env python3
"""Debug _parse_experience_block for Ganesh format."""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from parsers.work_experience_structured_parser import StructuredWorkExperienceParser

work_text = """Visa Forster City, CA
Site Reliability  DevOps Engineer Dec 2022  Current
Environment: Git, GitLab, GitHub
Implemented Kubernetes and AWS EKS"""

parser = StructuredWorkExperienceParser()
lines = work_text.split('\n')

print("🔍 TESTING PARSE_EXPERIENCE_BLOCK")
print("=" * 70)

print("\n📝 Lines:")
for i, line in enumerate(lines):
    print(f"{i}: {line}")

print("\n🧪 Parsing from index 0 (Visa):")
exp = parser._parse_experience_block(lines, 0)

if exp:
    print(f"\n✅ SUCCESS!")
    print(f"  Job Title: {exp.get('job_title')}")
    print(f"  Company: {exp.get('company_name')}")
    print(f"  Location: {exp.get('location')}")
    print(f"  Start: {exp.get('start_date')}")
    print(f"  End: {exp.get('end_date')}")
    print(f"  Current: {exp.get('is_current')}")
    print(f"  Next Index: {exp.get('_next_index')}")
else:
    print(f"\n❌ FAILED - returned None")
    print(f"   Likely reason: Missing job_title or company_name")
