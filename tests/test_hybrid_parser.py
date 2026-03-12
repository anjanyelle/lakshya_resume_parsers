#!/usr/bin/env python3
"""
Test Hybrid Work Experience Parser
"""

import sys
import os
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'backend'))

from app.services.parser.hybrid_work_experience_parser import HybridWorkExperienceParser
import json

def test_hybrid_parser():
    """Test hybrid parser with various resume formats"""
    
    print("🧪 Testing Hybrid Work Experience Parser")
    print("=" * 60)
    
    # Initialize hybrid parser
    parser = HybridWorkExperienceParser(use_ml=True, use_llm=False)  # Disable LLM for testing
    
    # Test cases
    test_cases = [
        {
            'name': 'Your Format - Company Date Location',
            'text': '''PROFESSIONAL EXPERIENCE
HCA Healthcare: November 2022 - Current (Location: Nashville, TN)
Site Reliability Engineer
• Designed and deployed HIPAA-compliant cloud infrastructure
• Maintained 99.95% uptime

American Express: January 2020 - October 2022 (Location: New York, NY)
Site Reliability Engineer
• Built PCI-DSS compliant systems
• Led infrastructure team'''
        },
        {
            'name': 'Client Role Location',
            'text': '''PROFESSIONAL EXPERIENCE
Client: Nike | Location: Beaverton, OR
Role: Senior Developer | Jan 2022 - Current
• Developed e-commerce platform
• Led team of 5 developers

Client: Adidas | Location: Portland, OR
Role: Full Stack Developer | Mar 2020 - Dec 2021
• Built mobile applications
• Implemented CI/CD'''
        },
        {
            'name': 'Company Client Pipe',
            'text': '''PROFESSIONAL EXPERIENCE
Cigna Health (Client: Express Scripts) | 2022 - Present | Bloomfield, CT
Principal QA Automation Architect
• Built enterprise testing framework
• Reduced test execution time

Goldman Sachs (Client: Marcus) | 2019 - 2022 | New York, NY
Lead QA Engineer
• Designed testing strategies
• Mentored junior engineers'''
        },
        {
            'name': 'Header Format',
            'text': '''PROFESSIONAL EXPERIENCE
## HCA Healthcare: November 2022 - Current (Location: Nashville, TN)
Site Reliability Engineer
• Deployed cloud infrastructure
• Ensured system reliability

## American Express: January 2020 - October 2022 (Location: New York, NY)
Site Reliability Engineer
• Maintained trading systems
• Optimized performance'''
        },
        {
            'name': 'Mixed Format Challenge',
            'text': '''PROFESSIONAL EXPERIENCE
Apple Inc: January 2020 - Present (Location: Cupertino, CA)
Senior Software Engineer
• Developed iOS applications
• Led mobile team

Client: Microsoft | Location: Redmond, WA
Role: Software Engineer | Jun 2018 - Dec 2019
• Built Windows features
• Collaborated with product teams

Google (Client: Alphabet) | 2017 - 2018 | Mountain View, CA
Software Engineer
• Worked on search algorithms
• Improved system performance'''
        }
    ]
    
    total_tests = len(test_cases)
    passed_tests = 0
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 Test {i}/{total_tests}: {test_case['name']}")
        print("-" * 40)
        
        try:
            # Parse using hybrid parser
            jobs = parser.parse_work_experience(test_case['text'])
            
            if jobs:
                print(f"✅ Found {len(jobs)} jobs")
                
                # Show parsed jobs
                for j, job in enumerate(jobs, 1):
                    print(f"\n   Job {j}:")
                    print(f"     Company: {job.company}")
                    print(f"     Title: {job.title}")
                    print(f"     Location: {job.location}")
                    print(f"     Dates: {job.start_date} - {job.end_date}")
                    print(f"     Current: {job.is_current}")
                    print(f"     Confidence: {job.confidence:.2f}")
                    if hasattr(job, 'metadata') and job.metadata:
                        print(f"     Metadata: {job.metadata}")
                
                passed_tests += 1
            else:
                print("❌ No jobs found")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    # Performance statistics
    print("\n" + "=" * 60)
    print("📊 Performance Statistics")
    print("=" * 60)
    
    stats = parser.get_performance_stats()
    print(f"Total parses: {stats['total']}")
    print(f"Rule-based: {stats['rule_based']} ({stats.get('rule_based_pct', 0):.1f}%)")
    print(f"ML-enhanced: {stats['ml_enhanced']} ({stats.get('ml_enhanced_pct', 0):.1f}%)")
    print(f"LLM fallback: {stats['llm_fallback']} ({stats.get('llm_fallback_pct', 0):.1f}%)")
    
    # Summary
    print(f"\n📈 Test Summary:")
    print(f"Passed: {passed_tests}/{total_tests} ({passed_tests/total_tests*100:.1f}%)")
    
    if passed_tests == total_tests:
        print("🎉 All tests passed!")
    else:
        print("⚠️ Some tests failed")
    
    return passed_tests == total_tests

def test_ml_training():
    """Test ML model training"""
    
    print("\n🤖 Testing ML Model Training")
    print("-" * 40)
    
    try:
        from app.services.parser.ml_work_experience_parser import MLWorkExperienceParser
        
        # Initialize ML parser
        ml_parser = MLWorkExperienceParser()
        
        # Check if models are trained
        if ml_parser.is_trained:
            print("✅ ML models already trained")
        else:
            print("🧠 Training ML models...")
            ml_parser._train_models()
            
            if ml_parser.is_trained:
                print("✅ ML models trained successfully")
            else:
                print("❌ ML model training failed")
                return False
        
        # Test prediction
        test_text = "Company: Apple | Location: Cupertino, CA\nRole: Software Engineer | 2020 - Present"
        predictions = ml_parser.parse_work_experience(test_text)
        
        if predictions:
            print(f"✅ ML prediction successful: {len(predictions)} jobs")
            for pred in predictions:
                print(f"   Company: {pred.company} (confidence: {pred.confidence:.2f})")
        else:
            print("⚠️ ML prediction returned no results")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing ML: {e}")
        return False

def main():
    """Main test function"""
    
    print("🚀 Hybrid Parser Test Suite")
    print("=" * 60)
    
    # Change to backend directory
    os.chdir(Path(__file__).resolve().parent.parent / 'backend')
    
    success = True
    
    # Test ML training
    if not test_ml_training():
        success = False
    
    # Test hybrid parser
    if not test_hybrid_parser():
        success = False
    
    if success:
        print("\n🎉 All tests completed successfully!")
        print("\n📋 Next Steps:")
        print("1. Enable LLM fallback for complete coverage")
        print("2. Test with real resume files")
        print("3. Monitor performance in production")
        print("4. Collect feedback for model improvement")
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
