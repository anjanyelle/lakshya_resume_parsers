#!/usr/bin/env python3
"""Debug merge and source tracking."""

from parsers.master_parser import MasterParser
from parsers.hybrid_merger import HybridMerger

file_path = "/Users/anjanyelle/Desktop/untitled folder 3/Lakshya-LLM-Resume-Parser/backend/src/uploads/a3475d4b-c664-4fcc-aa95-3ae277c305da_RAGHAVENDRA_PRASAD_VEMURI___9_pages__Devops.docx"

parser = MasterParser()
result = parser.parse_file(file_path, "test_merge_debug")

print("="*80)
print("MERGE DEBUG - CHECKING SOURCE KEYS")
print("="*80)
print()

# Print ALL keys in result
all_keys = list(result.keys())
print(f"Total keys in result: {len(all_keys)}")
print()

# Separate source keys from regular keys
source_keys = [k for k in all_keys if k.startswith('_') and k.endswith('_source')]
regular_keys = [k for k in all_keys if not k.startswith('_')]
metadata_keys = [k for k in all_keys if k.startswith('_') and not k.endswith('_source')]

print(f"Regular keys ({len(regular_keys)}):")
for k in sorted(regular_keys)[:20]:
    print(f"  {k}")
print()

print(f"Source keys ({len(source_keys)}):")
for k in sorted(source_keys):
    field = k[1:-7]
    source = result[k]
    value = result.get(field)
    print(f"  {k:30s} = {source:20s} (value: {str(value)[:50]})")
print()

print(f"Metadata keys ({len(metadata_keys)}):")
for k in sorted(metadata_keys):
    print(f"  {k}")
print()

# Check merge_metadata
merge_meta = result.get('_merge_metadata')
if merge_meta:
    print("Merge metadata found:")
    print(f"  {merge_meta}")
else:
    print("⚠️  No merge_metadata found")

print()
print("AI Status:")
print(f"  ai_skipped in result: {result.get('ai_skipped', 'N/A')}")
metrics = result.get('processing_metrics', {}).get('timing_ms', {})
print(f"  ai_skipped in metrics: {metrics.get('ai_skipped', 'N/A')}")
print(f"  ai_parsing_ms: {metrics.get('ai_parsing_ms', 0):.1f}ms")
