#!/usr/bin/env python3
"""Test if the DeBERTa model loads successfully."""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from parsers.deberta_ner_parser import DeBERTaNerParser

print("🧪 Testing DeBERTa Model Loading")
print("=" * 70)

# Initialize parser
print("\n1️⃣  Initializing DeBERTa parser...")
parser = DeBERTaNerParser()

print(f"\n📊 Parser Status:")
print(f"   Model path: {parser.model_path}")
print(f"   Model loaded: {parser.is_loaded}")
print(f"   DeBERTa available: {parser.deberta_available}")
print(f"   Model object: {parser.model is not None}")
print(f"   Tokenizer object: {parser.tokenizer is not None}")

if parser.deberta_available and parser.is_loaded:
    print(f"\n✅ SUCCESS! DeBERTa model loaded successfully!")
    
    # Test parsing
    print(f"\n2️⃣  Testing model inference...")
    test_text = """
    Full Stack Developer
    Wipro, Bangalore
    June 2022 - Present
    Client: ICICI Bank
     Developed microservices using Spring Boot
    """
    
    try:
        result = parser.parse_text(test_text)
        print(f"\n✅ Parsing successful!")
        print(f"   Companies: {result.get('companies', [])}")
        print(f"   Job titles: {result.get('job_titles', [])}")
        print(f"   Locations: {result.get('locations', [])}")
        print(f"   Work experience: {len(result.get('work_experience', []))} entries")
        
        if result.get('work_experience'):
            exp = result['work_experience'][0]
            print(f"\n   First experience:")
            print(f"   - Job title: {exp.get('job_title')}")
            print(f"   - Company: {exp.get('company_name')}")
            print(f"   - Location: {exp.get('location')}")
            print(f"   - Clients: {len(exp.get('clients', []))}")
    except Exception as e:
        print(f"\n❌ Parsing failed: {e}")
        import traceback
        traceback.print_exc()
else:
    print(f"\n❌ FAILED! DeBERTa model did not load")
    print(f"   Using fallback: Structured Parser")

print("\n" + "=" * 70)
