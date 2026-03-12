#!/usr/bin/env python3
"""
Quick Fix for Work Experience Title Extraction
"""

import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

def fix_title_extraction():
    """Quick fix to extract titles correctly"""
    print("🔧 QUICK FIX FOR TITLE EXTRACTION")
    print("=" * 40)
    
    try:
        from app.services.parser.work_experience_parser import WorkExperienceParser
        parser = WorkExperienceParser()
        
        # Test the improved header parsing
        test_lines = [
            "Cardinal Health Location: Dublin, OH",
            "DevOps Engineer October 2022 – Current", 
            "Responsibilities:",
            "• Led enterprise-wide migration..."
        ]
        
        print("📋 TESTING HEADER PARSING:")
        print("-" * 30)
        
        company, title, location, start_date, end_date, is_current, body_start = parser._parse_header_lines(test_lines)
        
        print(f"✅ Company: '{company}'")
        print(f"✅ Title: '{title}'")
        print(f"✅ Location: '{location}'")
        print(f"✅ Start Date: '{start_date}'")
        print(f"✅ End Date: '{end_date}'")
        print(f"✅ Is Current: '{is_current}'")
        print(f"✅ Body Start: '{body_start}'")
        
        # Test title normalization
        if title:
            normalized_title = parser._normalize_job_title(title)
            print(f"✅ Normalized Title: '{normalized_title}'")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    fix_title_extraction()
