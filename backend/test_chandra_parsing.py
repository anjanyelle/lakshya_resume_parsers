#!/usr/bin/env python3
"""
Test Chandra Shyam's resume parsing
"""

import sys
sys.path.append('app')
from app.services.enhanced_pipeline_final import EnhancedResumePipelineFinal

def test_chandra_parsing():
    print('🧪 TESTING CHANDRA SHYAM PARSING')
    print('=' * 60)
    
    # Chandra Shyam's resume text
    chandra_resume = '''
Name: Chandra Shyam
LinkedIn: www.linkedin.com/in/chandra-shyam | Phno: +1 (341)- 203- 5403 | shyamchandra1912@gmail.com
Sr. Big Data Engineer
PROFESSIONAL SUMMARY:
•	Designed and deployed production-grade agentic retrieval systems using Python and DSPy to build intelligent agents that automatically pull PR metadata, commit history, and diffs from Git repositories, integrating LLM-driven evaluation frameworks while implementing prompt chaining and context packing techniques for accurate CES metric computation.
•	Built and maintained robust data orchestration pipelines using Dagster and Apache Airflow on AWS, leveraging ECS, EventBridge, Lambda, and S3 to ingest PR metadata, commit records, and branch tracking information, implementing backfill procedures, retries, and monitoring systems to ensure high reliability and data quality across engineering workflows.
PROFESSIONAL EXPERIENCE:
Humana: August 2023 – Current (Location: Louisville, KY)  
Role: Sr. Big Data Engineer
Responsibilities:
•	Designed and deployed agentic retrieval workflows using Python, LangChain, and LangGraph to build context-aware agents ingesting PR metadata, commit metadata, and GitHub history, enabling automated CES scoring and quality metric computation for healthcare pipelines while ensuring HIPAA-compliant audit trails and HL7 interoperability across AWS S3, AWS Lambda, and AWS Glue.
•	Migrated legacy orchestration from Apache Airflow to Dagster across 40+ production pipelines processing healthcare claims, clinical records, and patient data on AWS ECS and AWS EKS, implementing retries, backfills, scheduling, and data quality alerts while exposing metrics, traces, and logs through Power BI and Collibra frameworks.
Morgan Stanley: October 2020 – July 2023 (Location: New York, NY) 
Role: Sr Data Engineer
Responsibilities:
•	Designed and deployed production-grade data pipelines using Python and Dagster on AWS, ingesting PR metadata, commit metadata, and code quality telemetry from GitHub and Jenkins, integrating AWS Lambda, AWS S3, AWS Glue, and AWS ECS to ensure PCI-DSS-compliant financial workflows, automated retries, backfills, and observability with metrics, traces, and logs.
•	Built retrieval agents using Python and DSPy to extract historical code context, diffs, and commit histories from GitHub, implementing prompt chaining and context packing for LLM optimization, automating score correction workflows, exposing CES and quality metrics via REST APIs, and ensuring SOX and GLBA-compliant secure audit trails across financial pipelines.
Delta Airlines: December 2017 – September 2020 (Location: Atlanta, GA) 
Role: Data Engineer / Data Analyst
Responsibilities:
•	Designed and deployed production-grade data pipelines using Python and Apache Airflow to ingest commit metadata and PR metadata from GitHub, integrating AWS Lambda and AWS EventBridge for real-time processing, exposing quality metrics via REST APIs, ensuring SOC 2 audit trails and FAA/IATA compliance across aviation engineering workflows.
•	Built end-to-end data modeling frameworks using Python to link PRs and commits, tracking branch merges to main repositories, integrating AWS Glue and Dagster pipelines for historical backfills, implementing Prometheus and Grafana dashboards for anomaly detection and IOSA-compliant aviation software quality monitoring.
Cisco: February 2016 – November 2017 (Location: San Jose, CA) 
Role: Data Engineer / Migration Specialist
Responsibilities:
•	Built a Network Data Integration platform using Azure Cloud, improving enterprise data integration efficiency while enabling seamless data flow across global networking systems by consolidating monitoring telemetry from thousands of devices deployed in international data centers.
•	Developed scalable data ingestion pipelines using Talend ETL and Azure Data Factory, efficiently processing large volumes of network monitoring and security appliance data while ensuring reliable ingestion, transformation, and availability for downstream operational analytics.
Flipkart: August 2014 – December 2015 (Location: Bangalore, India) 
Role: ETL Developer
Responsibilities:
•	Built a scalable ETL pipeline using AWS Services, Informatica, and Talend, integrating data from e commerce platforms, inventory systems, and customer databases to create a unified data flow supporting high volume daily transaction processing across multiple online retail channels.
•	Configured Amazon S3 for secure storage of raw, staging, and transformed product catalog datasets, enabling reliable ingestion workflows for large SKU volumes while applying versioning and lifecycle policies to balance accessibility with long term storage cost optimization.
EDUCATION:
•	Bachelor of Technology in Computer Science & Engineering at Koneru Lakshmaiah University 2010-2014
'''
    
    # Initialize pipeline
    pipeline = EnhancedResumePipelineFinal()
    
    # Parse work experience
    work_entries = pipeline._extract_work_experience(chandra_resume)
    
    print(f'Total entries: {len(work_entries)}')
    print()
    
    for i, work in enumerate(work_entries):
        print(f'📋 Job {i+1}:')
        print(f'  Company: {work.get("company", "N/A")}')
        print(f'  Title: {work.get("title", "N/A")}')
        print(f'  Date Range: {work.get("date_range", "N/A")}')
        print(f'  Location: {work.get("location", "N/A")}')
        print(f'  Description: {work.get("description", "N/A")[:100]}...')
        print()
    
    # Check what's missing
    print('🎯 MAPPING ANALYSIS:')
    for i, work in enumerate(work_entries):
        missing = []
        if not work.get('date_range'): missing.append('date_range')
        if not work.get('location'): missing.append('location')
        if not work.get('description'): missing.append('description')
        
        if missing:
            print(f'  Job {i+1}: Missing {missing}')
        else:
            print(f'  Job {i+1}: ✅ All fields mapped')
    
    # Test education parsing
    print('\n🎓 EDUCATION PARSING:')
    education_entries = pipeline._extract_education(chandra_resume)
    print(f'Total education entries: {len(education_entries)}')
    for i, edu in enumerate(education_entries):
        print(f'  Edu {i+1}: {edu}')

if __name__ == "__main__":
    test_chandra_parsing()
