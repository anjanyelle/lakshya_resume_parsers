#!/usr/bin/env python3
"""Test name extraction after removing AI name extraction."""

from parsers.master_parser import MasterParser

file_path = "/Users/anjanyelle/Desktop/untitled folder 3/Lakshya-LLM-Resume-Parser/backend/src/uploads/a3475d4b-c664-4fcc-aa95-3ae277c305da_RAGHAVENDRA_PRASAD_VEMURI___9_pages__Devops.docx"

# Initialize parser
parser = MasterParser()

# Parse the resume
print("🚀 Testing name extraction after AI optimization...\n")
result = parser.parse_file(file_path, "test_candidate_name_extraction")

# Check results
print("="*80)
print("EXTRACTION RESULTS:")
print("="*80)
print(f"Name: {result.get('name')}")
print(f"Email: {result.get('email')}")
print(f"Phone: {result.get('phone')}")
print(f"Status: {result.get('status')}")
print()

# Check timing metrics
metrics = result.get('processing_metrics', {}).get('timing_ms', {})
print("="*80)
print("TIMING METRICS:")
print("="*80)
print(f"Rule Parsing: {metrics.get('rule_parsing_ms', 0):.1f}ms")
print(f"AI Parsing: {metrics.get('ai_parsing_ms', 0):.1f}ms")
print(f"Total: {metrics.get('total_ms', 0):.1f}ms")
print()

# Check merge metadata
merge_meta = result.get('merge_metadata', {})
if merge_meta:
    print("="*80)
    print("MERGE METADATA:")
    print("="*80)
    print(f"Strategy: {merge_meta.get('strategy_used', {})}")
    print()

# Verify name is correct
expected_name = "RAGHAVENDRA PRASAD VEMURI"
actual_name = result.get('name')

print("="*80)
print("VERIFICATION:")
print("="*80)
if actual_name == expected_name:
    print(f"✅ SUCCESS: Name extracted correctly!")
    print(f"   Expected: {expected_name}")
    print(f"   Actual:   {actual_name}")
elif actual_name and expected_name.lower() in actual_name.lower():
    print(f"⚠️  PARTIAL: Name extracted but format differs")
    print(f"   Expected: {expected_name}")
    print(f"   Actual:   {actual_name}")
else:
    print(f"❌ FAILURE: Name extraction failed!")
    print(f"   Expected: {expected_name}")
    print(f"   Actual:   {actual_name}")
