#!/usr/bin/env python3
"""Test company extraction after removing AI company extraction."""

from parsers.master_parser import MasterParser

file_path = "/Users/anjanyelle/Desktop/untitled folder 3/Lakshya-LLM-Resume-Parser/backend/src/uploads/a3475d4b-c664-4fcc-aa95-3ae277c305da_RAGHAVENDRA_PRASAD_VEMURI___9_pages__Devops.docx"

# Initialize parser
parser = MasterParser()

# Parse the resume
print("🚀 Testing company extraction after AI optimization...\n")
result = parser.parse_file(file_path, "test_candidate_company_extraction")

# Check results
print("="*80)
print("EXTRACTION RESULTS:")
print("="*80)
print(f"Name: {result.get('name')}")
print(f"Email: {result.get('email')}")
print(f"Status: {result.get('status')}")
print()

# Check work experience
work_exp = result.get('work_experience', [])
print("="*80)
print(f"WORK EXPERIENCE ({len(work_exp)} jobs):")
print("="*80)
for i, exp in enumerate(work_exp, 1):
    print(f"\n{i}. Job Title: {exp.get('job_title', 'N/A')}")
    print(f"   Company: {exp.get('company_name', 'N/A')}")
    print(f"   Dates: {exp.get('start_date', 'N/A')} - {exp.get('end_date', 'N/A')}")
    print(f"   Location: {exp.get('location', 'N/A')}")

# Check if companies field exists in top-level result
companies_list = result.get('companies', [])
print()
print("="*80)
print("TOP-LEVEL COMPANIES FIELD:")
print("="*80)
print(f"Companies: {companies_list}")
print(f"Count: {len(companies_list) if companies_list else 0}")

# Check timing metrics
metrics = result.get('processing_metrics', {}).get('timing_ms', {})
print()
print("="*80)
print("TIMING METRICS:")
print("="*80)
print(f"Rule Parsing: {metrics.get('rule_parsing_ms', 0):.1f}ms")
print(f"AI Parsing: {metrics.get('ai_parsing_ms', 0):.1f}ms")
print(f"Experience Extraction: {metrics.get('experience_extraction_ms', 0):.1f}ms")
print(f"Total: {metrics.get('total_ms', 0):.1f}ms")

# Verify companies are extracted correctly
print()
print("="*80)
print("VERIFICATION:")
print("="*80)

expected_companies = ["Goldman Sachs", "JPMorgan Chase", "Accenture"]
extracted_companies = [exp.get('company_name', '') for exp in work_exp if exp.get('company_name')]

print(f"Expected companies: {expected_companies}")
print(f"Extracted companies: {extracted_companies}")

# Check if all expected companies are found
all_found = all(
    any(expected.lower() in extracted.lower() for extracted in extracted_companies)
    for expected in expected_companies
)

if all_found and len(extracted_companies) >= len(expected_companies):
    print(f"\n✅ SUCCESS: All companies extracted correctly from work_experience blocks!")
    print(f"   Found {len(extracted_companies)} companies in work_experience")
elif len(extracted_companies) > 0:
    print(f"\n⚠️  PARTIAL: Some companies extracted")
    print(f"   Found {len(extracted_companies)} companies")
else:
    print(f"\n❌ FAILURE: No companies extracted!")

# Verify AI companies field is empty/not used
if not companies_list or len(companies_list) == 0:
    print(f"\n✅ CONFIRMED: AI companies field is empty (as expected)")
else:
    print(f"\n⚠️  WARNING: AI companies field still populated: {companies_list}")
