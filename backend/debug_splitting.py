#!/usr/bin/env python3

import re

# Test the splitting logic
work_text = """Bank of America: June 2023 - Current (Location: Charlotte, NC)
Role: Sr Data Engineer
Responsibilities:
- Led detailed requirement sessions with finance, risk, and revenue stakeholders to translate regulatory reporting mandates into scalable ETL solutions using Palantir Foundry, integrating transactional, ERP, and CRM datasets into a governed AWS data lake architecture.
Cigna Health: August 2020 - May 2023 (Location: Bloomfield, CT)
Role: Sr Data Engineer
Workday: October 2017 - July 2020 (Location: Pleasanton, CA)"""

# Mounika pattern - Updated with more companies
mounika_pattern = r'([A-Z][a-z\s&]+(?:Health|America|Bank of|Group|Corporation|Inc|LLC|Ltd|Co|Tech|Global|Financial|Retail|Telecom|Energy|Services|Cigna|Workday|Progressive|Mastek)):\s*([A-Za-z]+\s+\d{4}\s*[–-]\s*(?:Current|[A-Za-z]+\s+\d{4}))\s*\((?:Location:\s*)?([^)])\)'
mounika_matches = re.findall(mounika_pattern, work_text)

print("🔍 Mounika Pattern Matches:")
for i, match in enumerate(mounika_matches):
    print(f"  Match {i+1}: {match}")

# Test the splitting
parts = work_text
print(f"\n📋 Original text length: {len(work_text)}")

for i, (company, date_range, location) in enumerate(mounika_matches):
    company_full = f"{company}: {date_range} (Location: {location})"
    print(f"  Replacing: '{company_full}' with '###SPLIT###{company}'")
    parts = parts.replace(company_full, f'###SPLIT###{company}')
    print(f"  After replacement {i+1}: {len(parts)} chars")

company_sections = parts.split('###SPLIT###')
print(f"\n🎯 Final sections: {len(company_sections)}")
for i, section in enumerate(company_sections):
    print(f"  Section {i+1}: '{section[:50]}...' (Length: {len(section)})")
