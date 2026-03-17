import sys
sys.path.append('backend')
from app.services.parser.work_experience_parser import WorkExperienceParser

# Test the parser with the resume text
parser = WorkExperienceParser()
resume_text = """Humana: August 2023 - Current (Location: Louisville, KY)
Role: Sr. Big Data Engineer
Responsibilities:
- Designed and deployed agentic retrieval workflows using Python, Lang Chain, and Lang Graph to build context-aware agents ingesting PR metadata, commit metadata, and Git Hub history, enabling automated CES scoring and quality metric computation for healthcare pipelines while ensuring HIPAA-compliant audit trails and HL 7 interoperability across AWS S 3, AWS Lambda, and AWS Glue.

Morgan Stanley: October 2020 - July 2023 (Location: New York, NY)
Role: Sr Data Engineer
- Designed and deployed production-grade data pipelines using Python and Dagster on AWS, ingesting PR metadata, commit metadata, and code quality telemetry from Git Hub and Jenkins, integrating AWS Lambda, AWS S 3, AWS Glue, and AWS ECS to ensure PCI-DSS-compliant financial workflows, automated retries, backfills, and observability with metrics, traces, and logs.

Delta Airlines: December 2017 - September 2020 (Location: Atlanta, GA)
Role: Data Engineer / Data Analyst
- Designed and deployed production-grade data pipelines using Python and Apache Airflow to ingest commit metadata and PR metadata from Git Hub, integrating AWS Lambda and AWS Event Bridge for real-time processing, exposing quality metrics via REST AP Is, ensuring SOC 2 audit trails and FAA/IATA compliance across aviation engineering workflows.

Cisco: February 2016 - November 2017 (Location: San Jose, CA)
Role: Data Engineer / Migration Specialist
- Built a Network Data Integration platform using Azure Cloud, improving enterprise data integration efficiency while enabling seamless data flow across global networking systems by consolidating monitoring telemetry from thousands of devices deployed in international data centers.

Flipkart: August 2014 - December 2015 (Location: Bangalore, India)
Role: ETL Developer
- Built a scalable ETL pipeline using AWS Services, Informatica, and Talend, integrating data from e commerce platforms, inventory systems, and customer databases to create a unified data flow supporting high volume daily transaction processing across multiple online retail channels."""

# Test extract_individual_jobs
job_blocks = parser.extract_individual_jobs(resume_text)
print(f'Extracted {len(job_blocks)} job blocks')
for i, block in enumerate(job_blocks):
    print(f'Job {i+1}: {block[:50]}...')

# Test full parsing
jobs = parser.parse_experience_section(resume_text)
print(f'\nParsed {len(jobs)} jobs:')
for i, job in enumerate(jobs):
    print(f'Job {i+1}: {job.company} - {job.title}')
