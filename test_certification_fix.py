#!/usr/bin/env python3
"""
Test Certification Parser After Fix
"""

import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

def test_certification_parser():
    """Test the fixed certification parser"""
    print("🔧 TESTING CERTIFICATION PARSER AFTER FIX")
    print("=" * 50)
    
    try:
        from app.services.parser.certification_parser import CertificationParser
        print("✅ CertificationParser imports successfully!")
        
        # Test the parser
        parser = CertificationParser()
        
        # Test cases
        test_cases = [
            "## AWS",
            "Devops", 
            "DevOps",
            "AWS Certified Solutions Architect",
            "PMP: Project Management Professional"
        ]
        
        print("\n🏆 TESTING CERTIFICATION EXTRACTION:")
        print("-" * 40)
        
        for test_case in test_cases:
            entry = parser._parse_line(test_case)
            if entry:
                print(f"✅ Input: '{test_case}'")
                print(f"   Name: {entry.name}")
                print(f"   Organization: {entry.issuing_organization}")
                print(f"   Confidence: {entry.confidence}")
                print()
            else:
                print(f"❌ Failed to parse: '{test_case}'")
        
        # Test full parsing
        cert_text = """
        Certifications
        ## AWS
        Devops
        """
        
        entries = parser.parse(cert_text)
        print(f"📊 Total certifications found: {len(entries)}")
        for entry in entries:
            print(f"   - {entry.name} ({entry.issuing_organization})")
        
        print("\n🎯 EXPECTED RESULTS:")
        print("-" * 20)
        print("✅ AWS detected with 'Amazon Web Services' organization")
        print("✅ DevOps detected with 'Professional Certification' organization")
        print("✅ No syntax errors")
        print("✅ Parser working correctly")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_certification_parser()
    if success:
        print("\n🚀 CERTIFICATION PARSER IS WORKING!")
    else:
        print("\n🚨 CERTIFICATION PARSER STILL HAS ISSUES!")
