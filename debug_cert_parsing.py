#!/usr/bin/env python3
"""
Debug Certification Parsing - Test with Vaishnavi's resume
"""

import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

def debug_cert_parsing():
    """Debug certification parsing issues"""
    
    print("🔍 DEBUGGING CERTIFICATION PARSING")
    print("=" * 50)
    
    from app.services.parser.certification_parser import CertificationParser
    from app.data.taxonomy.certifications_top import KNOWN_CERT_KEYWORDS, CERTIFICATION_ALIASES
    
    # Test certification lines from Vaishnavi's resume
    test_certs = [
        "AWS",
        "Devops",
        "## AWS",
        "## Devops"
    ]
    
    print("1. Checking KNOWN_CERT_KEYWORDS...")
    print(f"   'aws' in KNOWN_CERT_KEYWORDS: {'aws' in KNOWN_CERT_KEYWORDS}")
    print(f"   'devops' in KNOWN_CERT_KEYWORDS: {'devops' in KNOWN_CERT_KEYWORDS}")
    print()
    
    print("2. Checking CERTIFICATION_ALIASES...")
    aws_aliases = [k for k in CERTIFICATION_ALIASES.keys() if 'aws' in k.lower()]
    devops_aliases = [k for k in CERTIFICATION_ALIASES.keys() if 'devops' in k.lower()]
    print(f"   AWS-related aliases: {len(aws_aliases)} found")
    print(f"   DevOps-related aliases: {len(devops_aliases)} found")
    if devops_aliases:
        print(f"   DevOps aliases: {devops_aliases[:3]}...")
    print()
    
    print("3. Testing _extract_name method...")
    parser = CertificationParser()
    
    for cert in test_certs:
        result = parser._extract_name(cert)
        print(f"   Input: '{cert}'")
        print(f"   Output: {result}")
        print()
    
    print("4. Testing full parsing pipeline...")
    cert_text = "Certifications\nAWS\nDevops"
    entries = parser.extract_candidate_lines_from_full_text(cert_text)
    parsed_entries = []
    
    for line in entries:
        entry = parser._parse_line(line)
        if entry:
            parsed_entries.append(entry)
    
    print(f"   Input text: {repr(cert_text)}")
    print(f"   Extracted lines: {len(entries)}")
    print(f"   Parsed entries: {len(parsed_entries)}")
    for i, entry in enumerate(parsed_entries):
        print(f"     {i+1}. {entry.name} - {entry.issuing_organization}")
    print()
    
    print("🔍 ROOT CAUSE ANALYSIS:")
    print("=" * 30)
    
    # Test the exact logic from _extract_name
    print("Testing keyword matching logic:")
    for cert in ["AWS", "Devops"]:
        lowered = cert.lower()
        keyword_hits = sum(
            1 for keyword in KNOWN_CERT_KEYWORDS
            if keyword in lowered
        )
        print(f"   '{cert}': {keyword_hits} keyword hits")
        
        # Check token count
        token_count = len(cert.split())
        print(f"   Token count: {token_count}")
        print(f"   Length: {len(cert)}")
        
        # Check if it would pass the fallback logic
        passes_fallback = (
            3 <= token_count <= 10
            and len(cert) <= 120
        )
        print(f"   Passes fallback: {passes_fallback}")
        print()
    
    return True

if __name__ == "__main__":
    debug_cert_parsing()
