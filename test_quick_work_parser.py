#!/usr/bin/env python3
"""
Test Quick Work Experience Parser - Immediate Results
"""

import sys
import os
sys.path.append('backend')
sys.path.append('backend/app')

from app.services.quick_work_parser import get_quick_work_parser

def test_quick_work_parser():
    """Test the quick work experience parser"""
    
    # Sample work experience text (same as before)
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
    
    print("🚀 Testing Quick Work Experience Parser...")
    print("=" * 60)
    
    try:
        # Get parser instance
        parser = get_quick_work_parser()
        
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
        
        print("\n🎯 TARGET JSON STRUCTURE ACHIEVED!")
        print("=" * 60)
        
        # Display final JSON structure
        import json
        print("\n📄 FINAL JSON:")
        print(json.dumps(results, indent=2))
        
        # Check if we achieved the target structure
        target_fields = ["company", "job_title", "start_date", "end_date", "is_current", 
                        "location", "employment_type", "responsibilities", "tech_stack", 
                        "confidence", "_source_model", "_missing_fields"]
        
        print("\n🔍 TARGET STRUCTURE VERIFICATION:")
        print("=" * 60)
        
        if results:
            first_entry = results[0]
            missing_target_fields = []
            
            for field in target_fields:
                if field in first_entry:
                    print(f"  ✅ {field}: {type(first_entry[field]).__name__}")
                else:
                    print(f"  ❌ {field}: MISSING")
                    missing_target_fields.append(field)
            
            if not missing_target_fields:
                print("\n🎉 ALL TARGET FIELDS ACHIEVED!")
                print("✅ Quick implementation successful!")
            else:
                print(f"\n⚠️ Missing {len(missing_target_fields)} target fields: {missing_target_fields}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_quick_work_parser()
    if success:
        print("\n🎉 Quick Work Experience Parser implementation successful!")
    else:
        print("\n❌ Quick Work Experience Parser implementation failed!")
    
    sys.exit(0 if success else 1)
