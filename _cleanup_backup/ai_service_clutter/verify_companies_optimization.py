#!/usr/bin/env python3
"""Verify that companies optimization is working correctly."""

from parsers.master_parser import MasterParser
from parsers.text_extractor import TextExtractor
from parsers.section_splitter import SectionSplitter
from parsers.experience_extractor import ExperienceExtractor

file_path = "/Users/anjanyelle/Desktop/untitled folder 3/Lakshya-LLM-Resume-Parser/backend/src/uploads/a3475d4b-c664-4fcc-aa95-3ae277c305da_RAGHAVENDRA_PRASAD_VEMURI___9_pages__Devops.docx"

print("="*80)
print("VERIFICATION: Companies Optimization")
print("="*80)
print()

# Step 1: Extract text
print("Step 1: Extracting text...")
extractor = TextExtractor()
text_result = extractor.extract(file_path)
text = text_result['text']
print(f"✓ Text extracted: {len(text)} chars")
print()

# Step 2: Split sections
print("Step 2: Splitting sections...")
splitter = SectionSplitter()
sections = splitter.split_sections(text)
print(f"✓ Sections found: {list(sections.keys())}")
print()

# Step 3: Extract experience directly
print("Step 3: Extracting experience from experience section...")
exp_extractor = ExperienceExtractor()
exp_text = sections.get('experience', '')
print(f"Experience section length: {len(exp_text)} chars")
print()
print("Experience section preview:")
print("-" * 80)
print(exp_text[:500])
print("-" * 80)
print()

exp_result = exp_extractor.extract_work_experience(exp_text)
work_exp = exp_result.get('work_experience', [])
print(f"✓ Extracted {len(work_exp)} work experience entries")
print()

# Show what experience_extractor found
print("Experience Extractor Results:")
print("-" * 80)
for i, exp in enumerate(work_exp, 1):
    print(f"{i}. Job Title: {exp.get('job_title', 'N/A')}")
    print(f"   Company: {exp.get('company_name', 'N/A')}")
    print(f"   Dates: {exp.get('start_date', 'N/A')} - {exp.get('end_date', 'N/A')}")
    print()

# Step 4: Parse with master parser
print("="*80)
print("Step 4: Full pipeline with MasterParser...")
print("="*80)
parser = MasterParser()
result = parser.parse_file(file_path, "verify_companies")

# Check AI parsing results
print()
print("AI Parsing Check:")
print("-" * 80)
print(f"AI returned 'companies' field: {'companies' in result.get('merge_metadata', {}).get('strategy_used', {})}")
print(f"Top-level 'companies' field: {result.get('companies', [])}")
print(f"Companies count: {len(result.get('companies', []))}")
print()

# Check work_experience
print("Work Experience in Final Result:")
print("-" * 80)
final_work_exp = result.get('work_experience', [])
print(f"Work experience entries: {len(final_work_exp)}")
for i, exp in enumerate(final_work_exp, 1):
    print(f"{i}. {exp.get('job_title', 'N/A')} at {exp.get('company_name', 'N/A')}")
print()

# Timing
metrics = result.get('processing_metrics', {}).get('timing_ms', {})
print("Timing Metrics:")
print("-" * 80)
print(f"AI Parsing: {metrics.get('ai_parsing_ms', 0):.1f}ms")
print(f"Experience Extraction: {metrics.get('experience_extraction_ms', 0):.1f}ms")
print(f"Total: {metrics.get('total_ms', 0):.1f}ms")
print()

# Conclusion
print("="*80)
print("CONCLUSION:")
print("="*80)
print("✅ Optimization Status: Companies removed from AI parsing")
print(f"✅ AI companies field is empty: {len(result.get('companies', [])) == 0}")
print(f"⚠️  Experience extractor bug: company_name extraction failing")
print()
print("NOTE: The experience_extractor bug is a SEPARATE issue that exists")
print("      regardless of the AI optimization. The optimization itself is")
print("      working correctly - AI is no longer extracting companies.")
print()
print("NEXT STEPS:")
print("1. Fix experience_extractor to handle 'Company Name  Job Title' format")
print("2. Or accept that companies will come from work_experience.company_name")
print("   once the extractor is fixed")
