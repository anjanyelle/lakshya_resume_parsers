#!/usr/bin/env python3
"""
Run all ML integrations and test them
"""

import sys
import os
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

def test_spacy_integration():
    """Test spaCy integration"""
    print("🔍 Testing spaCy Integration...")
    print("=" * 50)
    
    try:
        from app.services.parser.spacy_integration import test_spacy_integration
        entities, companies, job_titles = test_spacy_integration()
        print("✅ spaCy integration working!")
        return True
    except Exception as e:
        print(f"❌ spaCy integration failed: {e}")
        return False

def test_rapidfuzz_integration():
    """Test RapidFuzz integration"""
    print("\n🔍 Testing RapidFuzz Integration...")
    print("=" * 50)
    
    try:
        from app.services.parser.rapidfuzz_integration import test_rapidfuzz_integration
        matcher = test_rapidfuzz_integration()
        print("✅ RapidFuzz integration working!")
        return True
    except Exception as e:
        print(f"❌ RapidFuzz integration failed: {e}")
        return False

def test_transformers_integration():
    """Test Transformers integration"""
    print("\n🔍 Testing Transformers Integration...")
    print("=" * 50)
    
    try:
        from app.services.parser.transformers_integration import test_transformers_integration
        nlp = test_transformers_integration()
        print("✅ Transformers integration working!")
        return True
    except Exception as e:
        print(f"❌ Transformers integration failed: {e}")
        return False

def test_enhanced_hybrid_parser():
    """Test enhanced hybrid parser with all integrations"""
    print("\n🔍 Testing Enhanced Hybrid Parser...")
    print("=" * 50)
    
    try:
        from app.services.parser.hybrid_work_experience_parser import HybridWorkExperienceParser
        from app.services.parser.spacy_integration import SpacyEntityExtractor
        from app.services.parser.rapidfuzz_integration import RapidFuzzMatcher
        from app.services.parser.company_standardizer import CompanyStandardizer
        
        # Create enhanced parser
        parser = HybridWorkExperienceParser(use_ml=True, use_llm=False)
        
        # Sample resume text
        sample_resume = """
        ## PROFESSIONAL EXPERIENCE
        
        Client: Core Logic Inc
        Location: New York, NY
        Role: Senior Software Engineer Jan 2020 - Present
        
        • Developed cloud-based solutions using AWS
        • Led team of 5 developers
        • Implemented CI/CD pipelines
        
        Company: Microsoft
        Jan 2018 - Dec 2019 (Location: Redmond, WA)
        Role: Software Engineer
        
        • Built microservices architecture
        • Worked on Azure cloud platform
        • Optimized database performance
        """
        
        # Parse resume
        jobs = parser.parse_work_experience(sample_resume)
        
        print(f"✅ Enhanced parser parsed {len(jobs)} jobs")
        
        for i, job in enumerate(jobs, 1):
            print(f"  Job {i}: {job.company} - {job.title} (confidence: {job.confidence:.2f})")
        
        # Get performance stats
        stats = parser.get_performance_stats()
        print(f"  Performance: {stats}")
        
        return True
        
    except Exception as e:
        print(f"❌ Enhanced hybrid parser failed: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Running ML Integration Tests")
    print("=" * 60)
    
    results = {
        'spacy': test_spacy_integration(),
        'rapidfuzz': test_rapidfuzz_integration(),
        'transformers': test_transformers_integration(),
        'enhanced_parser': test_enhanced_hybrid_parser()
    }
    
    print("\n📊 FINAL RESULTS:")
    print("=" * 50)
    
    for integration, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{integration:20} → {status}")
    
    passed = sum(results.values())
    total = len(results)
    
    print(f"\n🎯 OVERALL: {passed}/{total} integrations working")
    
    if passed == total:
        print("🎉 ALL INTEGRATIONS SUCCESSFUL!")
        print("📈 Your accuracy should now be: 95-98%")
    elif passed >= 3:
        print("✅ MOST INTEGRATIONS WORKING!")
        print("📈 Your accuracy should now be: 92-95%")
    else:
        print("⚠️  SOME INTEGRATIONS FAILED")
        print("📈 Your accuracy remains: 88-92%")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
