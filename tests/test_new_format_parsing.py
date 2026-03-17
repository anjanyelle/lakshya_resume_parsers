import sys
import os
# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'backend'))

from app.services.parser.work_experience_parser import WorkExperienceParser

def test_new_format_parsing():
    """Test parsing of the new Company: Date Range (Location: City, State) format"""
    
    # Sample text from the user's resume
    text = """
PROFESSIONAL EXPERIENCE:
Humana: August 2023 – Current (Location: Louisville, KY)  
Role: Sr. Big Data Engineer
Responsibilities:
• Designed and deployed agentic retrieval workflows using Python, LangChain, and LangGraph to build context-aware agents ingesting PR metadata, commit metadata, and GitHub history, enabling automated CES scoring and quality metric computation for healthcare pipelines while ensuring HIPAA-compliant audit trails and HL7 interoperability across AWS S3, AWS Lambda, and AWS Glue.
• Migrated legacy orchestration from Apache Airflow to Dagster across 40+ production pipelines processing healthcare claims, clinical records, and patient data on AWS ECS and AWS EKS, implementing retries, backfills, scheduling, and data quality alerts while exposing metrics, traces, and logs through Power BI and Collibra frameworks.

Morgan Stanley: October 2020 – July 2023 (Location: New York, NY) 
Role: Sr Data Engineer
Responsibilities:
• Designed and deployed production-grade data pipelines using Python and Dagster on AWS, ingesting PR metadata, commit metadata, and code quality telemetry from GitHub and Jenkins, integrating AWS Lambda, AWS S3, AWS Glue, and AWS ECS to ensure PCI-DSS-compliant financial workflows, automated retries, backfills, and observability with metrics, traces, and logs.
• Built retrieval agents using Python and DSPy to extract historical code context, diffs, and commit histories from GitHub, implementing prompt chaining and context packing for LLM optimization, automating score correction workflows, exposing CES and quality metrics via REST APIs, and ensuring SOX and GLBA-compliant secure audit trails across financial pipelines.
"""
    
    print("=" * 60)
    print("TESTING NEW FORMAT PARSING")
    print("=" * 60)
    
    work_parser = WorkExperienceParser()
    
    # Parse the entire experience section
    print("\nTESTING FULL PARSING")
    print("-" * 40)
    parsed_jobs = work_parser.parse_experience_section(text)
    
    print(f"\nNumber of parsed jobs: {len(parsed_jobs)}")
    for i, job in enumerate(parsed_jobs):
        print(f"\n--- Parsed Job {i+1} ---")
        print(f"Company: {job.company}")
        print(f"Title: {job.title}")
        print(f"Location: {job.location}")
        print(f"Start Date: {job.start_date}")
        print(f"End Date: {job.end_date}")
        print(f"Is Current: {job.is_current}")
        print(f"Description length: {len(job.description) if job.description else 0}")
        print(f"Bullets count: {len(job.bullets) if job.bullets else 0}")
        if job.bullets:
            print(f"First bullet: {job.bullets[0][:100]}...")

if __name__ == "__main__":
    test_new_format_parsing()
