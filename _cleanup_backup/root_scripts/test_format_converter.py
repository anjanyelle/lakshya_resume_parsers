#!/usr/bin/env python3
"""Test the CSV to natural language format converter"""

import sys
sys.path.insert(0, 'ai-service')

from parsers.deberta_ner_parser import DeBERTaNerParser

# Initialize parser
parser = DeBERTaNerParser()

# Test cases
test_cases = [
    {
        "name": "CSV Format",
        "input": "Twitch,Seattle WA,Senior Video Platform Engineer,December 2020,Present"
    },
    {
        "name": "Double Colon Format",
        "input": "Lyft :: San Francisco CA :: Lead Backend Engineer :: March 2022 :: Present"
    },
    {
        "name": "Pipe Format (no @)",
        "input": "Nutanix | San Jose CA | Distinguished Cloud Engineer | September 2021 | Present"
    },
    {
        "name": "Natural Language (already correct)",
        "input": "Senior Software Engineer @ Amazon | Seattle, WA | March 2022 - Present"
    }
]

print("=" * 80)
print("FORMAT CONVERTER TEST")
print("=" * 80)

for test in test_cases:
    print(f"\n{'=' * 80}")
    print(f"Test: {test['name']}")
    print(f"{'=' * 80}")
    
    input_text = test['input']
    print(f"\n📥 Input:")
    print(f"   {input_text}")
    
    # Detect format
    format_type = parser._detect_format(input_text)
    print(f"\n🔍 Detected format: {format_type}")
    
    # Convert
    converted = parser._convert_to_natural_language(input_text)
    print(f"\n📤 Converted output:")
    print(f"   {converted}")
    
    if converted != input_text:
        print(f"\n✅ Conversion applied")
    else:
        print(f"\n⏭️  No conversion needed (already natural language)")

print("\n" + "=" * 80)
print("TEST COMPLETE")
print("=" * 80)
