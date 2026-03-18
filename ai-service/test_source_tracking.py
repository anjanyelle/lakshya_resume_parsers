#!/usr/bin/env python3
"""Test source tracking for all merged fields."""

from parsers.master_parser import MasterParser
import json

file_path = "/Users/anjanyelle/Desktop/untitled folder 3/Lakshya-LLM-Resume-Parser/backend/src/uploads/a3475d4b-c664-4fcc-aa95-3ae277c305da_RAGHAVENDRA_PRASAD_VEMURI___9_pages__Devops.docx"

print("="*80)
print("TESTING SOURCE TRACKING FOR ALL FIELDS")
print("="*80)
print()

# Parse the resume
parser = MasterParser()
result = parser.parse_file(file_path, "test_source_tracking")

# Extract source tracking information
print("FIELD SOURCE TRACKING:")
print("-" * 80)
print()

fields_with_sources = []
for key, value in result.items():
    if key.startswith('_') and key.endswith('_source'):
        field_name = key[1:-7]  # Remove leading _ and trailing _source
        source = value
        field_value = result.get(field_name)
        has_value = bool(field_value)
        
        # Format value for display
        if isinstance(field_value, list):
            value_display = f"[{len(field_value)} items]"
        elif isinstance(field_value, str):
            value_display = field_value[:50] + "..." if len(field_value) > 50 else field_value
        else:
            value_display = str(field_value)
        
        fields_with_sources.append({
            'field': field_name,
            'source': source,
            'hasValue': has_value,
            'value': value_display
        })

# Sort by source for better readability
fields_with_sources.sort(key=lambda x: (x['source'], x['field']))

# Group by source
sources = {}
for item in fields_with_sources:
    source = item['source']
    if source not in sources:
        sources[source] = []
    sources[source].append(item)

# Display by source
for source, items in sorted(sources.items()):
    print(f"📍 SOURCE: {source.upper()}")
    print("-" * 80)
    for item in items:
        status = "✅" if item['hasValue'] else "❌"
        print(f"  {status} {item['field']}: {item['value']}")
    print()

# Summary statistics
print("="*80)
print("SOURCE DISTRIBUTION:")
print("="*80)
for source, items in sorted(sources.items()):
    count = len(items)
    with_values = sum(1 for item in items if item['hasValue'])
    print(f"{source:20s}: {with_values}/{count} fields with values")
print()

# Check AI skipped status
ai_skipped = result.get('ai_skipped', False)
print("="*80)
print("AI MODEL STATUS:")
print("="*80)
if ai_skipped:
    print("✅ AI MODEL COMPLETELY SKIPPED")
    print(f"   Reason: {result.get('reason', 'Unknown')}")
else:
    print("⚠️  AI MODEL WAS CALLED")
    ai_time = result.get('processing_metrics', {}).get('timing_ms', {}).get('ai_parsing_ms', 0)
    print(f"   AI Time: {ai_time:.1f}ms")
print()

# Timing metrics
metrics = result.get('processing_metrics', {}).get('timing_ms', {})
print("="*80)
print("TIMING METRICS:")
print("="*80)
print(f"Rule Parsing:          {metrics.get('rule_parsing_ms', 0):>8.1f}ms")
print(f"AI Parsing:            {metrics.get('ai_parsing_ms', 0):>8.1f}ms  {'← SKIPPED' if ai_skipped else ''}")
print(f"Experience Extraction: {metrics.get('experience_extraction_ms', 0):>8.1f}ms")
print(f"Total:                 {metrics.get('total_ms', 0):>8.1f}ms")
print()

# Verification
print("="*80)
print("VERIFICATION:")
print("="*80)
print(f"✅ Source tracking implemented: {len(fields_with_sources)} fields tracked")
print(f"✅ Rule-based fields: {len(sources.get('rule', []))}")
print(f"✅ AI fields: {len(sources.get('ai', []))}")
print(f"✅ Experience extractor fields: {len(sources.get('experience_extractor', []))}")
print(f"✅ Hybrid fields (rule+ai): {len(sources.get('rule+ai', []))}")
print()

# Export trace for backend verification
trace_output = {
    'fields': fields_with_sources,
    'ai_skipped': ai_skipped,
    'timing': metrics,
    'summary': {
        'total_fields': len(fields_with_sources),
        'by_source': {source: len(items) for source, items in sources.items()}
    }
}

print("="*80)
print("TRACE OUTPUT (for backend verification):")
print("="*80)
print(json.dumps(trace_output, indent=2))
print()

print("="*80)
print("NEXT STEP:")
print("="*80)
print("Run a resume parse through the backend API and check the terminal logs")
print("for '[PARSE TRACE]' to verify source tracking is working end-to-end.")
