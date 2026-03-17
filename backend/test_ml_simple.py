#!/usr/bin/env python3
"""
Simple test for ML models without dataset dependencies
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

def test_ml_models_only():
    """Test ML models directly without datasets"""
    print("🧪 Testing ML Models Only")
    print("=" * 40)
    
    try:
        # Test lightweight model manager
        from models.lightweight_model_manager import LightweightModelManager
        
        manager = LightweightModelManager()
        print("✅ LightweightModelManager initialized")
        
        # Load models
        load_results = manager.load_models()
        print(f"📦 Load Results: {load_results}")
        
        # Test parsing
        test_text = """
        John Doe
        Senior Software Engineer at Google
        Mountain View, CA
        Skills: Python, AWS, Docker, Kubernetes
        """
        
        print("\n📄 Testing parsing...")
        result = manager.parse_resume_lightweight(test_text)
        
        print(f"✅ Models Used: {result.models_used}")
        print(f"📊 Overall Confidence: {result.overall_confidence:.2f}")
        print(f"⏱️  Processing Time: {result.total_processing_time:.2f}s")
        
        # Test spaCy skills extraction
        skills = manager.extract_skills(test_text)
        print(f"🛠️  Skills Found: {skills}")
        
        # Test spaCy companies extraction
        companies = manager.extract_companies(test_text)
        print(f"🏢 Companies Found: {companies}")
        
        # Test spaCy job titles extraction
        job_titles = manager.extract_job_titles(test_text)
        print(f"💼 Job Titles Found: {job_titles}")
        
        # Test contact info extraction
        contact_info = manager.extract_contact_info(test_text)
        print(f"📞 Contact Info: {contact_info}")
        
        # Get status
        status = manager.get_status()
        print(f"\n📈 Status: {status}")
        
        print("\n🎉 ML Models Test PASSED!")
        return True
        
    except Exception as e:
        print(f"❌ Test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_ml_models_only()
    sys.exit(0 if success else 1)
