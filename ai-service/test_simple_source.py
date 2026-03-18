#!/usr/bin/env python3
"""Simple test to verify source tracking."""

from parsers.master_parser import MasterParser

file_path = "/Users/anjanyelle/Desktop/untitled folder 3/Lakshya-LLM-Resume-Parser/backend/src/uploads/a3475d4b-c664-4fcc-aa95-3ae277c305da_RAGHAVENDRA_PRASAD_VEMURI___9_pages__Devops.docx"

parser = MasterParser()
result = parser.parse_file(file_path, "test_simple")

print("="*80)
print("SOURCE TRACKING TEST")
print("="*80)
print()

# Check for _source keys
source_keys = [k for k in result.keys() if k.endswith('_source')]
print(f"Found {len(source_keys)} source tracking keys:")
for key in sorted(source_keys):
    field = key[1:-7]  # Remove _ prefix and _source suffix
    source = result[key]
    value = result.get(field)
    has_value = bool(value) and (not isinstance(value, list) or len(value) > 0)
    print(f"  {key:30s} = {source:20s} (has_value: {has_value})")

print()
print("Key fields:")
print(f"  name: {result.get('name')} (source: {result.get('_name_source', 'N/A')})")
print(f"  email: {result.get('email')} (source: {result.get('_email_source', 'N/A')})")
print(f"  skills: {len(result.get('skills', []))} skills (source: {result.get('_skills_source', 'N/A')})")
print(f"  locations: {result.get('locations', [])} (source: {result.get('_locations_source', 'N/A')})")

print()
print("AI Status:")
ai_skipped = result.get('processing_metrics', {}).get('timing_ms', {}).get('ai_skipped', False)
ai_time = result.get('processing_metrics', {}).get('timing_ms', {}).get('ai_parsing_ms', 0)
print(f"  AI Skipped: {ai_skipped}")
print(f"  AI Time: {ai_time:.1f}ms")
