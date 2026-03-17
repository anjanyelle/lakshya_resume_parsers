#!/usr/bin/env python3

import re

# Test Mounika's work experience pattern
work_text = """Bank of America: June 2023 - Current (Location: Charlotte, NC)
Role: Sr Data Engineer
Responsibilities:
- Led detailed requirement sessions with finance, risk, and revenue stakeholders to translate regulatory reporting mandates into scalable ETL solutions using Palantir Foundry, integrating transactional, ERP, and CRM datasets into a governed AWS data lake architecture.
Cigna Health: August 2020 - May 2023 (Location: Bloomfield, CT)
Role: Sr Data Engineer
Workday: October 2017 - July 2020 (Location: Pleasanton, CA)
Role: Data Engineer / Data Analyst"""

# Current pattern
mounika_pattern = r'([A-Z][a-z\s&]+(?:Health|America|Bank of|Group|Corporation|Inc|LLC|Ltd|Co|Tech|Global|Financial|Retail|Telecom|Energy|Services)):\s*([A-Za-z]+\s+\d{4}\s*[–-]\s*(?:Current|[A-Za-z]+\s+\d{4}))\s*\((?:Location:\s*)?([^)]+)\)'

print("🔍 Testing Mounika Pattern:")
print(f"Pattern: {mounika_pattern}")
print(f"Text: {work_text[:200]}...")

matches = re.findall(mounika_pattern, work_text)
print(f"Matches: {matches}")

# Test with simpler pattern
simple_pattern = r'([A-Z][a-z\s&]+):\s*([A-Za-z]+\s+\d{4}\s*[–-]\s*(?:Current|[A-Za-z]+\s+\d{4}))\s*\((?:Location:\s*)?([^)]+)\)'
simple_matches = re.findall(simple_pattern, work_text)
print(f"Simple matches: {simple_matches}")

# Test even simpler pattern
very_simple_pattern = r'([A-Za-z\s&]+):\s*([A-Za-z]+\s+\d{4}\s*[–-]\s*(?:Current|[A-Za-z]+\s+\d{4}))\s*\((?:Location:\s*)?([^)]+)\)'
very_simple_matches = re.findall(very_simple_pattern, work_text)
print(f"Very simple matches: {very_simple_matches}")

# Test line by line
lines = work_text.split('\n')
for i, line in enumerate(lines[:5]):
    print(f"Line {i+1}: {line}")
    match = re.search(very_simple_pattern, line)
    if match:
        print(f"  ✅ MATCH: {match.groups()}")
