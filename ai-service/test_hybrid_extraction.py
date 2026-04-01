#!/usr/bin/env python3
"""
Test hybrid experience extraction approach.
Verifies that custom NER model + rule-based extraction works WITHOUT Gemini API key.
"""

import sys
sys.path.insert(0, '.')
import os
import glob

# Temporarily remove GEMINI_API_KEY to test hybrid approach
original_key = os.environ.pop('GEMINI_API_KEY', None)

print("=" * 80)
print("🧪 TESTING HYBRID EXTRACTION APPROACH")
print("=" * 80)
print(f"GEMINI_API_KEY present: {bool(original_key)}")
print(f"Testing WITHOUT API key to verify custom model + rule-based works")
print("=" * 80)

# Find a test resume
resume_files = glob.glob('../resumes/*.pdf') + glob.glob('../resumes/*.docx')
if not resume_files:
    print("❌ No resume files found in ../resumes/")
    sys.exit(1)

test_file = resume_files[0]
print(f"\n📄 Testing with: {os.path.basename(test_file)}")
print(f"File size: {os.path.getsize(test_file):,} bytes\n")

# Import parser
from parsers.master_parser import MasterParser

# Parse resume
print("🔄 Parsing resume...\n")
parser = MasterParser()
result = parser.parse(test_file)

# Extract results
parsed_data = result.get('parsed_data', {})
work_experience = parsed_data.get('work_experience', [])
extraction_method = parsed_data.get('_extraction_method', 'unknown')
processing_metrics = parsed_data.get('processing_metrics', {})

# Display results
print("=" * 80)
print("📊 EXTRACTION RESULTS")
print("=" * 80)

print(f"\n✅ Extraction Method: {extraction_method}")
print(f"✅ Experiences Extracted: {len(work_experience)}")
print(f"✅ Processing Time: {processing_metrics.get('timing_ms', {}).get('experience_extraction_ms', 'N/A')}ms")

if work_experience:
    print(f"\n📋 Extracted Experiences:")
    for i, exp in enumerate(work_experience[:3], 1):  # Show first 3
        print(f"\n{i}. {exp.get('job_title', 'N/A')}")
        print(f"   Company: {exp.get('company_name', 'N/A')}")
        print(f"   Dates: {exp.get('start_date', 'N/A')} - {exp.get('end_date', 'Present' if exp.get('is_current') else 'N/A')}")
        print(f"   Description: {exp.get('description', 'N/A')[:100]}...")
    
    if len(work_experience) > 3:
        print(f"\n   ... and {len(work_experience) - 3} more")
else:
    print("\n⚠️ No experiences extracted")

# Verify extraction method
print("\n" + "=" * 80)
print("🎯 VERIFICATION")
print("=" * 80)

if extraction_method == 'custom_ner_model':
    print("✅ SUCCESS: Used Custom NER Model (PRIMARY)")
    print("   - Fast extraction (< 1 second)")
    print("   - No API costs")
    print("   - Offline capable")
elif extraction_method == 'rule_based':
    print("✅ SUCCESS: Used Rule-Based Extraction (SECONDARY)")
    print("   - Very fast extraction (< 100ms)")
    print("   - No API costs")
    print("   - Offline capable")
elif 'gemini' in extraction_method.lower():
    print("⚠️ WARNING: Used Gemini LLM (should only be fallback)")
    print("   - Slower extraction (3-15 seconds)")
    print("   - API costs apply")
    print("   - Requires internet")
    print("\n   This means custom NER model and rule-based both failed.")
    print("   Consider improving the models or patterns.")
else:
    print(f"❌ UNKNOWN: Extraction method '{extraction_method}'")

# Check other fields
print("\n" + "=" * 80)
print("📋 OTHER FIELDS")
print("=" * 80)

print(f"Name: {parsed_data.get('name', 'N/A')}")
print(f"Email: {parsed_data.get('email', 'N/A')}")
print(f"Phone: {parsed_data.get('phone', 'N/A')}")
print(f"Skills: {len(parsed_data.get('skills', []))} found")
print(f"Education: {len(parsed_data.get('education', []))} found")

# Overall confidence
confidence = parsed_data.get('confidence', {})
print(f"\nOverall Confidence: {confidence.get('overall', 'N/A')}")
print(f"Quality Level: {confidence.get('quality_level', 'N/A')}")

# Restore API key if it existed
if original_key:
    os.environ['GEMINI_API_KEY'] = original_key

print("\n" + "=" * 80)
print("✅ TEST COMPLETE")
print("=" * 80)

# Summary
print("\n📝 SUMMARY:")
if work_experience and extraction_method in ['custom_ner_model', 'rule_based']:
    print("✅ Hybrid approach working correctly!")
    print("✅ Custom model or rule-based extraction succeeded")
    print("✅ No Gemini API key required")
    print("\n💡 Your resume parser is now using FREE, FAST extraction methods!")
elif work_experience and 'gemini' in extraction_method.lower():
    print("⚠️ Hybrid approach fell back to Gemini")
    print("⚠️ Custom model and rule-based both failed")
    print("\n💡 Recommendations:")
    print("   1. Check if custom NER model is loaded correctly")
    print("   2. Improve rule-based patterns for this resume format")
    print("   3. Collect training data to fine-tune custom model")
else:
    print("❌ No experiences extracted by any method")
    print("\n💡 Recommendations:")
    print("   1. Check if experience section is detected correctly")
    print("   2. Verify resume has work experience section")
    print("   3. Check logs for detailed error messages")

print()
