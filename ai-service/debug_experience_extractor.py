#!/usr/bin/env python3
"""
Debug script to test experience extraction directly
"""

import sys
import os
import re

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from parsers.experience_extractor import extract_experience

def debug_experience_extraction():
    """Debug experience extraction with your data"""
    
    # Your exact experience text
    experience_text = """Senior Data Engineer
Home Depot
Atlanta, GA
March 2023 - Present

Environment: Python, Java, SQL, Hadoop, HDFS, MapReduce, Hive, Spark, Snowflake, Apache NiFi, Great Expectations, Apache Ranger, ERStudio, Apache Airflow, Apache Flink, Apache Kafka Streams, Collibra, dbt, Docker

- Designed multi-account AWS landing zone
- Implemented secure VPC peering and network segmentation
- Designed Kubernetes (EKS) clusters for container workloads"""
    
    print("=== DEBUG EXPERIENCE EXTRACTION ===")
    print(f"Input text length: {len(experience_text)} chars")
    print(f"Input text preview:\n{experience_text[:200]}...")
    
    # Check for years pattern
    year_pattern = re.compile(r'\b(?:19|20)\d{2}\b')
    has_years = year_pattern.search(experience_text)
    print(f"\n📅 Years pattern found: {bool(has_years)}")
    if has_years:
        years = year_pattern.findall(experience_text)
        print(f"   Years found: {years}")
    
    # Test the extraction
    print(f"\n🔍 Testing extract_experience function:")
    try:
        experiences = extract_experience(experience_text)
        print(f"✅ Extraction successful: {len(experiences)} experiences found")
        
        for i, exp in enumerate(experiences, 1):
            print(f"\n  Experience {i}:")
            for key, value in exp.items():
                print(f"    {key}: {value}")
                
    except Exception as e:
        print(f"❌ Extraction failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Test with different formats
    test_formats = [
        "Senior Data Engineer | Home Depot | March 2023 - Present",
        "Senior Data Engineer at Home Depot (March 2023 - Present)",
        "Senior Data Engineer\nHome Depot\nMarch 2023 - Present",
        "Title: Senior Data Engineer\nCompany: Home Depot\nDates: March 2023 - Present"
    ]
    
    print(f"\n🧪 Testing different formats:")
    for i, test_format in enumerate(test_formats, 1):
        print(f"\n  Format {i}: {test_format}")
        try:
            result = extract_experience(test_format)
            print(f"    Result: {len(result)} experiences")
            if result:
                for key, value in result[0].items():
                    if value:
                        print(f"      {key}: {value}")
        except Exception as e:
            print(f"    Error: {e}")

if __name__ == "__main__":
    debug_experience_extraction()
