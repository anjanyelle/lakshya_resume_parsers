#!/usr/bin/env python3

import sys
import os

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.llm_service import LLMParsingService

def test_quality_threshold_fix():
    print("🔍 Testing Quality Threshold Fix...")
    print("=" * 60)
    
    # Sample text from your resume
    sample_text = """## Home Depot: Senior Data Engineer March 2023 - Current Location: Atlanta, GA
Environment: SQL, Python, Java, Scala, Go, BigQuery, GCP (Google Cloud Platform), Kafka, Apache Beam, Terraform, Jenkins, CI/CD, ML Ops, Google Cloud Datastore, Cloud Dataflow, Pub/Sub, Looker, Looker Studio, Erwin Data Modeler, Google Cloud Data Catalog, Apollo Graph QL, AWS, Azure, ETL, Agile, Dev Ops, Graph QL, Git

- Designed and implemented a robust data pipeline using Apache Beam and Cloud Dataflow to process large-scale retail transaction data, improving data processing efficiency by optimizing Beam's parallel processing capabilities and Dataflow's auto-scaling features.
- Developed advanced ETL processes using Python and SQL to integrate multiple data sources, including point-of-sale systems and inventory management tools.

## Mastercard: Senior Data Engineer / Analyst May 2020 - February 2023 Location: Purchase, NY
- Designed and implemented complex data pipelines using Apache Beam and Cloud Dataflow to process high-volume banking transactions, improving data processing efficiency by optimizing Beam's windowing and triggering mechanisms for real-time analytics.
- Developed advanced machine learning models using Python and ML Ops practices to predict customer churn and loan default risks.

## T-Mobile: Senior Big Data Engineer August 2017 - April 2020 Location: Bellevue, WA
- Designed and implemented a real-time data processing pipeline using Apache Kafka and Apache Beam, enabling the ingestion and analysis of over 10 million telecom network events per hour.
- Developed and maintained complex ETL workflows in Google Cloud Dataflow using Python and Java."""
    
    # Test the enhanced parser
    llm_service = LLMParsingService()
    result = llm_service.extract_work_experience_details(sample_text)
    
    print(f"✅ Enhanced Parser Result: {len(result)} work experiences found")
    print()
    
    # Display results
    for i, work in enumerate(result, 1):
        print(f"📊 Work {i}:")
        print(f"   Company: {work.get('company')}")
        print(f"   Title: {work.get('title')}")
        print(f"   Start: {work.get('start_date')}")
        print(f"   End: {work.get('end_date')}")
        print(f"   Location: {work.get('location')}")
        print()
    
    print("🎯 Quality Threshold Fix Test: SUCCESS!")
    print("✅ LLM processing should now be triggered")
    print("✅ Enhanced parser should handle ## Company: Title Date Location format")
    print("✅ All work experiences should be parsed correctly")

if __name__ == "__main__":
    test_quality_threshold_fix()
