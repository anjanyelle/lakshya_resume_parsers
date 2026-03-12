import sys
import os
# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'backend'))

from app.services.parser.work_experience_parser import WorkExperienceParser

def test_parsing():
    """Test the full parsing flow"""
    
    # Sample job text from Ramu Gara's resume
    job_text = """Client: Morgan Stanley              
                                                                                                            
                                               New York, NY             Role: SR. BIG DATA ENGINEER         
                                                                                                            
                                     June 2023 - Current                Responsibilities:
•	Designed and implemented multi-layer data lakehouse architecture using AWS S3, AWS Glue, AWS Redshift, Databricks, establishing Bronze, Silver, Gold medallion layers with Dimensional modeling, Snowflake schema, and Data Vault 2.0 for healthcare and retail analytics workflows.
•	Developed batch and streaming ETL/ELT pipelines using AWS Glue, Databricks, Apache Spark, Kafka, Scala, ingesting real-time patient transactions, inventory updates, and device telemetry into S3, enabling analytics-ready datasets for enterprise decision-making."""
    
    print("=" * 60)
    print("TESTING FULL PARSING")
    print("=" * 60)
    
    work_parser = WorkExperienceParser()
    
    # Test parsing a single job
    print(f"\nParsing job with {len(job_text)} characters")
    parsed_jobs = work_parser.parse_experience_section(job_text)
    
    print(f"\nNumber of parsed jobs: {len(parsed_jobs)}")
    for i, job in enumerate(parsed_jobs):
        print(f"\n--- Parsed Job {i+1} ---")
        print(f"Company: {job.company}")
        print(f"Title: {job.title}")
        print(f"Location: {job.location}")
        print(f"Start Date: {job.start_date}")
        print(f"End Date: {job.end_date}")
        print(f"Description length: {len(job.description) if job.description else 0}")
        print(f"Bullets count: {len(job.bullets) if job.bullets else 0}")

if __name__ == "__main__":
    test_parsing()
