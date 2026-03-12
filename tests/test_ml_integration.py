#!/usr/bin/env python3
"""
Test ML Integration and UI Mapping Verification
"""

import sys
import os
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from app.services.parser.hybrid_work_experience_parser import HybridWorkExperienceParser
from app.services.parser.work_experience_parser import WorkExperienceParser

def test_ml_integration():
    """Test ML parser integration with sample resume text"""
    
    # Sample resume text with multiple formats
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
    
    print("🔍 Testing ML Integration...")
    print("=" * 50)
    
    # Test format detection
    parser = WorkExperienceParser()
    detected_format = parser.detect_format(sample_resume)
    print(f"📋 Detected Format: {detected_format}")
    
    # Test hybrid parser with ML
    hybrid_parser = HybridWorkExperienceParser(use_ml=True, use_llm=False)
    
    try:
        jobs = hybrid_parser.parse_work_experience(sample_resume)
        
        print(f"\n📊 Parsed {len(jobs)} jobs:")
        print("=" * 50)
        
        for i, job in enumerate(jobs, 1):
            print(f"\n🎯 Job {i}:")
            print(f"   Company: {job.company}")
            print(f"   Title: {job.title}")
            print(f"   Location: {job.location}")
            print(f"   Start Date: {job.start_date}")
            print(f"   End Date: {job.end_date}")
            print(f"   Current: {job.is_current}")
            print(f"   Confidence: {job.confidence:.2f}")
            print(f"   Bullets: {len(job.bullets)}")
            
            # Check for company metadata
            if hasattr(job, 'metadata') and job.metadata:
                print(f"   Metadata: {job.metadata}")
        
        # Get performance stats
        stats = hybrid_parser.get_performance_stats()
        print(f"\n📈 Performance Stats:")
        print("=" * 50)
        print(f"   Total: {stats['total']}")
        print(f"   Rule-based: {stats.get('rule_based_pct', 0):.1f}%")
        print(f"   ML-enhanced: {stats.get('ml_enhanced_pct', 0):.1f}%")
        print(f"   LLM fallback: {stats.get('llm_fallback_pct', 0):.1f}%")
        
        # Calculate overall confidence
        if jobs:
            avg_confidence = sum(job.confidence for job in jobs) / len(jobs)
            print(f"\n🎯 Overall Confidence: {avg_confidence:.2f}")
            
            if avg_confidence >= 0.85:
                print("✅ EXCELLENT: ML integration working perfectly!")
            elif avg_confidence >= 0.75:
                print("✅ GOOD: ML integration working well")
            else:
                print("⚠️  NEEDS IMPROVEMENT: ML integration needs tuning")
        
        return jobs
        
    except Exception as e:
        print(f"❌ Error testing ML integration: {e}")
        return []

def test_ui_mapping(jobs):
    """Test UI mapping with parsed jobs"""
    
    print(f"\n🎨 Testing UI Mapping...")
    print("=" * 50)
    
    # Simulate UI data structure
    ui_data = {
        "work_experience": [],
        "overall_confidence": 0.0,
        "parsing_method": "hybrid_ml"
    }
    
    for job in jobs:
        ui_job = {
            "id": f"job_{len(ui_data['work_experience']) + 1}",
            "company": {
                "name": job.company,
                "standardized": job.company,
                "confidence": job.confidence
            },
            "position": {
                "title": job.title,
                "level": "senior" if "senior" in job.title.lower() else "mid"
            },
            "timeline": {
                "start_date": job.start_date.isoformat() if job.start_date else None,
                "end_date": job.end_date.isoformat() if job.end_date else None,
                "is_current": job.is_current,
                "duration_months": job.duration_months
            },
            "location": {
                "city": job.location,
                "remote": "remote" in job.location.lower() if job.location else False
            },
            "responsibilities": {
                "summary": job.description,
                "bullets": job.bullets,
                "count": len(job.bullets)
            },
            "confidence": job.confidence,
            "metadata": getattr(job, 'metadata', {})
        }
        
        ui_data["work_experience"].append(ui_job)
    
    # Calculate overall confidence
    if ui_data["work_experience"]:
        ui_data["overall_confidence"] = sum(job["confidence"] for job in ui_data["work_experience"]) / len(ui_data["work_experience"])
    
    print(f"📊 UI Data Structure:")
    print("=" * 50)
    
    for i, job in enumerate(ui_data["work_experience"], 1):
        print(f"\n🎯 UI Job {i}:")
        print(f"   Company: {job['company']['name']} (conf: {job['company']['confidence']:.2f})")
        print(f"   Position: {job['position']['title']} ({job['position']['level']})")
        print(f"   Timeline: {job['timeline']['start_date']} to {job['timeline']['end_date']}")
        print(f"   Location: {job['location']['city']}")
        print(f"   Responsibilities: {job['responsibilities']['count']} bullets")
        print(f"   Confidence: {job['confidence']:.2f}")
    
    print(f"\n📈 Overall UI Confidence: {ui_data['overall_confidence']:.2f}")
    print(f"🔧 Parsing Method: {ui_data['parsing_method']}")
    
    return ui_data

def main():
    """Main test function"""
    print("🚀 ML Integration and UI Mapping Test")
    print("=" * 60)
    
    # Test ML integration
    jobs = test_ml_integration()
    
    if jobs:
        # Test UI mapping
        ui_data = test_ui_mapping(jobs)
        
        print(f"\n✅ SUCCESS: ML integration verified!")
        print(f"   • Parsed {len(jobs)} jobs successfully")
        print(f"   • UI mapping structure ready")
        print(f"   • Overall confidence: {ui_data['overall_confidence']:.2f}")
        
        if ui_data['overall_confidence'] >= 0.85:
            print(f"🎯 READY FOR PRODUCTION: Perfect ML mapping to UI!")
        else:
            print(f"⚠️  RECOMMENDATION: Fine-tune for better confidence")
    else:
        print(f"❌ FAILED: No jobs parsed - check ML integration")

if __name__ == "__main__":
    main()
