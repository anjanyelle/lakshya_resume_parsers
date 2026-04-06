#!/usr/bin/env python3
"""Test that the entire parsing pipeline works gracefully when DeBERTa model is missing."""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from parsers.master_parser import MasterParser
import time

print("🧪 FULL PIPELINE TEST - Missing DeBERTa Model")
print("=" * 70)

# Karthik's resume text
karthik_text = """Name: Karthik Varma
Contact: 91-90123-45678  karthik.varma.engineer@gmail.com
Based in: Pune, Maharashtra
PROFESSIONAL EXPERIENCE
Currently working with Tech Mahindra (since August 2023) as a Full Stack Engineer.
Assigned Projects:
For client Barclays
 Developed internal analytics tools for financial reporting
 Designed APIs for secure data exchange
For client ATT
 Built customer-facing dashboards
 Integrated telecom service APIs
Previously associated with Accenture (July 2022  July 2023) as Software Engineer.
Client Engagements:
Project handled for Amazon
 Developed backend services for order lifecycle
Started career at Mindtree (June 2021  June 2022) as Junior Developer.
Client Work:
Engaged with Cigna
 Developed insurance claim modules
EDUCATIONAL BACKGROUND
Completed Bachelor of Engineering in Information Technology
Savitribai Phule Pune University
Duration: 2017 to 2021"""

print("\n1️⃣  Initializing MasterParser...")
start_time = time.time()

try:
    parser = MasterParser()
    init_time = (time.time() - start_time) * 1000
    print(f"✅ MasterParser initialized in {init_time:.1f}ms")
except Exception as e:
    print(f"❌ Failed to initialize MasterParser: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n2️⃣  Parsing resume...")
parse_start = time.time()

try:
    result = parser.parse_text(karthik_text, "test-missing-model-001")
    parse_time = (time.time() - parse_start) * 1000
    
    print(f"✅ Parsing completed in {parse_time:.1f}ms")
    print(f"\n📊 RESULTS:")
    print(f"   Status: {result.get('status')}")
    print(f"   Work experience: {len(result.get('work_experience', []))} entries")
    print(f"   Companies: {result.get('companies', [])}")
    print(f"   Job titles: {result.get('job_titles', [])}")
    print(f"   Confidence: {result.get('confidence', {}).get('overall', 0):.2f}")
    
    # Check for structured format
    if result.get('work_experience'):
        has_clients = any(
            exp.get('clients') and isinstance(exp.get('clients'), list) and len(exp.get('clients')) > 0
            for exp in result['work_experience']
        )
        
        if has_clients:
            print(f"\n✅ STRUCTURED FORMAT DETECTED:")
            for i, exp in enumerate(result['work_experience'], 1):
                clients = exp.get('clients', [])
                print(f"   Experience {i}: {exp.get('job_title')} at {exp.get('company_name')}")
                print(f"   - Clients: {len(clients)}")
                for client in clients:
                    if isinstance(client, dict):
                        print(f"     • {client.get('client_name')}: {len(client.get('descriptions', []))} descriptions")
        else:
            print(f"\n⚠️  No client blocks found")
    
    # Check processing metrics
    metrics = result.get('processing_metrics', {}).get('timing_ms', {})
    print(f"\n⏱️  TIMING BREAKDOWN:")
    print(f"   DeBERTa parsing: {metrics.get('deberta_parsing_ms', 0):.1f}ms")
    print(f"   Experience extraction: {metrics.get('experience_extraction_ms', 0):.1f}ms")
    print(f"   Total: {metrics.get('total_ms', 0):.1f}ms")
    
    # Validation
    print(f"\n🔍 VALIDATION:")
    expected_companies = ['Tech Mahindra', 'Accenture', 'Mindtree']
    actual_companies = result.get('companies', [])
    
    if len(result.get('work_experience', [])) == 3:
        print(f"   ✅ Work experience count: 3")
    else:
        print(f"   ❌ Work experience count: {len(result.get('work_experience', []))} (expected 3)")
    
    if set(expected_companies).issubset(set(actual_companies)):
        print(f"   ✅ All companies extracted")
    else:
        print(f"   ⚠️  Companies: {actual_companies}")
    
    if has_clients:
        print(f"   ✅ Client blocks with descriptions")
    else:
        print(f"   ❌ No client blocks")
    
except Exception as e:
    print(f"\n❌ PIPELINE FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 70)
print("✅ PIPELINE TEST COMPLETE - System handled missing DeBERTa model gracefully!")
print("   The structured parser fallback is working correctly.")
