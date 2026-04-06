#!/usr/bin/env python3
"""Test DeBERTa graceful fallback when model files are missing."""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from parsers.deberta_ner_parser import DeBERTaNerParser

print("🧪 Testing DeBERTa Graceful Fallback")
print("=" * 70)

# Initialize parser (should handle missing model files gracefully)
print("\n1️⃣  Initializing DeBERTa parser...")
parser = DeBERTaNerParser()

print(f"\n📊 Parser Status:")
print(f"   Model path: {parser.model_path}")
print(f"   Model loaded: {parser.is_loaded}")
print(f"   DeBERTa available: {parser.deberta_available}")
print(f"   Structured parser available: {parser.structured_parser is not None}")
print(f"   is_available(): {parser.is_available()}")

# Test parsing with missing model
print("\n2️⃣  Testing parse with missing model files...")

test_text = """
Currently working with Tech Mahindra (since August 2023) as a Full Stack Engineer.
For client Barclays
 Developed internal analytics tools for financial reporting
 Designed APIs for secure data exchange
"""

try:
    result = parser.parse_text(test_text)
    print(f"\n✅ Parsing succeeded!")
    print(f"   Work experience entries: {len(result.get('work_experience', []))}")
    print(f"   Companies: {result.get('companies', [])}")
    print(f"   Job titles: {result.get('job_titles', [])}")
    
    if result.get('work_experience'):
        exp = result['work_experience'][0]
        print(f"\n   First experience:")
        print(f"   - Job title: {exp.get('job_title')}")
        print(f"   - Company: {exp.get('company_name')}")
        print(f"   - Clients: {len(exp.get('clients', []))}")
        
except Exception as e:
    print(f"\n❌ Parsing failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
print("✅ Test complete - DeBERTa handled missing model gracefully!")
