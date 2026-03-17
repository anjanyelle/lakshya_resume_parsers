# -*- coding: utf-8 -*-
"""
Check work experience data mapping
"""

import sys
sys.path.append('app')
from app.services.enhanced_pipeline_final import EnhancedResumePipelineFinal

def check_work_mapping():
    print('🔍 WORK EXPERIENCE DATA MAPPING CHECK')
    print('=' * 60)
    
    # Full resume text
    rahul_resume = '''
## RAHUL VENKATARAMAN
Sr. Data Engineer
LinkedIn: www.linkedin.com/in/rahul-venkataraman  |  Phone: +1 (469)-532-7814  |  rahul.venkataraman@gmail.com  |  Dallas, TX
## PROFESSIONAL SUMMARY
•	10+ years of experience as a Data Engineer designing, building, and optimizing large-scale data pipelines, ETL frameworks, and cloud-native data platforms across healthcare, financial services, retail, telecom, energy, and e-commerce domains.
## PROFESSIONAL EXPERIENCE
UnitedHealth Group (Client: Optum Analytics): October 2023 - Current (Location: Eden Prairie, MN (Remote))
Role: Sr. Data Engineer
Responsibilities:
•	Designed and deployed HIPAA-compliant AWS Glue and Apache Spark ETL pipelines ingesting 50M+ daily healthcare claims, member eligibility records, and clinical encounter data from HL7 FHIR APIs and EDI 837/835 feeds into an AWS S3 data lake partitioned by payer, date, and claim type.
•	Built real-time streaming pipelines using AWS Kinesis Data Streams and Apache Kafka, processing prior authorization events and pharmacy benefit transactions with sub-500 ms latency, triggering downstream Lambda enrichment functions and Redshift Streaming Ingestion for live dashboards.
JP Morgan Chase & Co.: June 2021 - September 2023 (Location: Columbus, OH)
Role: Sr. Data Engineer
Responsibilities:
•	Built PCI-DSS and SOX-compliant Apache Kafka event streaming pipelines ingesting real-time payment card transactions, wire transfers, and ACH events from 40+ source systems, processing 8M+ daily events into S3 data lake and Redshift for fraud analytics and regulatory capital reporting.
•	Designed Snowflake data warehouse on AWS with multi-cluster configurations, implementing data vault 2.0 modeling for customer 360, account hierarchy, and transaction history, creating role-based access controls for 1,500+ analytics consumers across risk, compliance, and business intelligence teams.
'''

    # Initialize pipeline
    pipeline = EnhancedResumePipelineFinal()

    # Parse work experience
    work_entries = pipeline._extract_work_experience(rahul_resume)

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

if __name__ == "__main__":
    check_work_mapping()
