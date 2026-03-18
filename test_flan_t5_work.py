#!/usr/bin/env python3
"""
Test Flan-T5 Work Experience Extractor
"""

import sys
import os
sys.path.append('backend')
sys.path.append('backend/app')

from app.services.enhanced_work_parser import get_enhanced_work_parser

def test_flan_t5_extractor():
    """Test the Flan-T5 work experience extractor"""
    
    # Sample work experience text
    work_text = """
    PROFESSIONAL EXPERIENCE
    
    T-Mobile | Data Analyst
    December 2015 - September 2017
    Bellevue, WA
    Contract/Consulting
    
    Responsibilities:
    - Architected ETL pipelines using SSIS and Talend Data Quality to extract subscriber data
    - Engineered predictive churn models using R analyzing customer lifecycle patterns
    - Developed automated reporting dashboards using SQL and Tableau
    - Collaborated with cross-functional teams to optimize data workflows
    
    Technologies: SQL, R, SSIS, Java, Tableau, Python
    
    Google | Senior Data Engineer
    October 2017 - Present
    Mountain View, CA
    Full-time
    
    Responsibilities:
    - Led data engineering initiatives for Google Cloud Platform
    - Designed and implemented scalable data processing pipelines
    - Mentored junior engineers and established best practices
    - Reduced data processing costs by 40% through optimization
    
    Technologies: Python, Java, Spark, GCP, BigQuery, Kafka
    """
    
    print("🚀 Testing Flan-T5 Work Experience Extractor...")
    print("=" * 60)
    
    try:
        # Get parser instance
        parser = get_enhanced_work_parser()
        
        # Parse work experience
        results = parser.parse_work_experience(work_text)
        
        print(f"✅ Successfully parsed {len(results)} work experience entries!")
        print("\n📋 RESULTS:")
        print("=" * 60)
        
        for i, entry in enumerate(results):
            print(f"\n📌 ENTRY {i+1}:")
            print(f"  Company: {entry.get('company', 'N/A')}")
            print(f"  Job Title: {entry.get('job_title', 'N/A')}")
            print(f"  Start Date: {entry.get('start_date', 'N/A')}")
            print(f"  End Date: {entry.get('end_date', 'N/A')}")
            print(f"  Is Current: {entry.get('is_current', False)}")
            print(f"  Location: {entry.get('location', 'N/A')}")
            print(f"  Employment Type: {entry.get('employment_type', 'N/A')}")
            print(f"  Confidence: {entry.get('confidence', 0.0):.2f}")
            print(f"  Source Model: {entry.get('_source_model', 'N/A')}")
            print(f"  Missing Fields: {entry.get('_missing_fields', [])}")
            
            if entry.get('responsibilities'):
                print(f"  Responsibilities ({len(entry['responsibilities'])}):")
                for j, resp in enumerate(entry['responsibilities'][:3]):
                    print(f"    {j+1}. {resp}")
                if len(entry['responsibilities']) > 3:
                    print(f"    ... and {len(entry['responsibilities']) - 3} more")
            
            if entry.get('tech_stack'):
                print(f"  Tech Stack: {', '.join(entry['tech_stack'])}")
            
            if entry.get('_flagged_for_review'):
                print("  ⚠️ FLAGGED FOR REVIEW")
        
        print("\n🎯 TARGET JSON STRUCTURE ACHIEVED!")
        print("=" * 60)
        
        # Display final JSON structure
        import json
        print("\n📄 FINAL JSON:")
        print(json.dumps(results, indent=2))
        
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_flan_t5_extractor()
    if success:
        print("\n🎉 Flan-T5 implementation successful!")
    else:
        print("\n❌ Flan-T5 implementation failed!")
    
    sys.exit(0 if success else 1)
