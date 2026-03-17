#!/usr/bin/env python3
"""
Quick Backend Test - Verify all imports work
"""

import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

def test_backend_imports():
    """Test that all backend imports work correctly"""
    
    print("🧪 TESTING BACKEND IMPORTS")
    print("=" * 30)
    
    try:
        # Test main application
        print("1. Testing main application...")
        from app.main import app
        print("   ✅ Main app imported successfully")
        
        # Test certification parser
        print("2. Testing certification parser...")
        from app.services.parser.certification_parser import CertificationParser
        print("   ✅ CertificationParser imported successfully")
        
        # Test dataset imports
        print("3. Testing dataset imports...")
        from app.data.taxonomy.certifications_top import CERTIFICATION_ALIASES, KNOWN_CERT_KEYWORDS
        print(f"   ✅ {len(CERTIFICATION_ALIASES)} certification aliases loaded")
        print(f"   ✅ {len(KNOWN_CERT_KEYWORDS)} certification keywords loaded")
        
        # Test new dataset files
        print("4. Testing new dataset files...")
        from app.data.taxonomy.company_mappings import COMPANY_MAPPINGS
        from app.data.taxonomy.job_titles_mappings import JOB_TITLE_MAPPINGS
        print(f"   ✅ {len(COMPANY_MAPPINGS)} company mappings loaded")
        print(f"   ✅ {len(JOB_TITLE_MAPPINGS)} job title mappings loaded")
        
        # Test skills database
        print("5. Testing skills database...")
        from app.data.skills.skills_master import SKILLS_DATABASE
        print(f"   ✅ {len(SKILLS_DATABASE)} skills loaded")
        
        print("\n🎉 ALL IMPORTS SUCCESSFUL!")
        print("✅ Backend is ready to start!")
        print("✅ Datasets are integrated!")
        print("✅ Parser improvements should be active!")
        
        return True
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

if __name__ == "__main__":
    success = test_backend_imports()
    
    if success:
        print("\n🚀 READY TO START BACKEND!")
        print("Run: cd backend && uvicorn app.main:app --reload")
        print("Then test with real resumes for accuracy improvements!")
    else:
        print("\n❌ FIX ISSUES BEFORE STARTING BACKEND")
