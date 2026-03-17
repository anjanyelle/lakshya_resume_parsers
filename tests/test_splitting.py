import sys
import os
# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'backend'))

from app.services.parser.work_experience_parser import WorkExperienceParser

def test_splitting():
    """Test just the splitting logic"""
    
    # Sample text from Ramu Gara's resume
    text = """
PROFESSIONAL EXPERIENCE:

Client: Morgan Stanley                                                                                                                                                            New York, NY
Role: SR. BIG DATA ENGINEER                                                                                                                                             June 2023 - Current
Responsibilities:
•	Designed and implemented multi-layer data lakehouse architecture using AWS S3, AWS Glue, AWS Redshift, Databricks

Client: Humana                                                                                                                                                                Louisville, KY
Role: SR DATA ENGINEER                                                                                                                             August 2020 - May 2023
Responsibilities:
•	Designed and implemented multi-layer data lakehouse architecture using Azure Cloud, ADLS Gen2, Azure Databricks, Azure Synapse Analytics
"""
    
    print("=" * 60)
    print("TESTING JOB SPLITTING ONLY")
    print("=" * 60)
    
    work_parser = WorkExperienceParser()
    
    # Test splitting
    jobs = work_parser._split_merged_jobs(text)
    
    print(f"\nNumber of jobs split: {len(jobs)}")
    for i, job in enumerate(jobs):
        print(f"\n--- Job {i+1} ---")
        print(f"Length: {len(job)} characters")
        print(f"First 300 chars:\n{job[:300]}")

if __name__ == "__main__":
    test_splitting()
