# -*- coding: utf-8 -*-
"""
Debug work experience parsing
"""

import re

def debug_work_parsing():
    print("🔍 DEBUGGING WORK EXPERIENCE PARSING")
    print("=" * 50)
    
    # Test with Rahul's work section
    rahul_work_text = """
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
"""
    
    print("📄 Original Work Text:")
    print(rahul_work_text[:200] + "...")
    
    # Test section detection
    work_section_match = re.search(r'(?:PROFESSIONAL EXPERIENCE|EXPERIENCE|WORK EXPERIENCE)[\s:\-]*(.*?)(?=\n\n[A-Z]|\n##|\Z)', rahul_work_text, re.IGNORECASE | re.DOTALL)
    
    if work_section_match:
        work_text = work_section_match.group(1).strip()
        print(f"\n✅ Work section found: {len(work_text)} chars")
        print(f"First 100 chars: {work_text[:100]}...")
        
        # Test company name detection
        company_names = [
            'UnitedHealth Group',
            'JP Morgan Chase & Co.',
            'Walmart Global Tech',
            'AT&T',
            'Exxon Mobil Corporation',
            'Infosys Limited'
        ]
        
        print(f"\n🔍 Testing company name detection:")
        for company in company_names:
            if company in work_text:
                print(f"  ✅ Found: {company}")
            else:
                print(f"  ❌ Missing: {company}")
        
        # Test splitting
        parts = work_text
        for company in company_names:
            parts = parts.replace(company, f'###SPLIT###{company}')
        
        company_sections = parts.split('###SPLIT###')
        company_sections = [section.strip() for section in company_sections if section.strip()]
        
        print(f"\n📊 Split into {len(company_sections)} sections:")
        for i, section in enumerate(company_sections):
            print(f"  Section {i+1}: {section[:100]}...")
        
        # Test alternative patterns
        print(f"\n🔍 Testing alternative patterns:")
        alt_patterns = [
            r'([A-Z][a-z\s]+(?:Group|Corporation|Inc|LLC|Ltd|Co|Tech|Global|Health|Financial|Retail|Telecom|Energy|Services))\s*:',
            r'([A-Z][a-z]+\s+[A-Z][a-z]+\s+(?:Chase|Morgan|Walmart|AT&T|Exxon|Infosys))\s*:'
        ]
        
        for i, pattern in enumerate(alt_patterns):
            matches = re.findall(pattern, work_text)
            print(f"  Pattern {i+1}: Found {len(matches)} matches")
            for match in matches:
                print(f"    - {match}")
    
    else:
        print("❌ No work section found!")
    
    # Test with full resume text
    print(f"\n🔍 Testing with full resume text:")
    full_resume = """
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
## TECHNICAL SKILLS
Programming Languages: Python, PySpark, Scala, SQL, Bash, Java, HiveQL, R
Big Data & Processing: Apache Spark, PySpark, Spark Streaming, Apache Kafka, Apache Flink, Apache Hive, HDFS, MapReduce, Yarn, Apache NiFi, Sqoop, Flume, Zookeeper
"""
    
    work_section_match = re.search(r'(?:PROFESSIONAL EXPERIENCE|EXPERIENCE|WORK EXPERIENCE)[\s:\-]*(.*?)(?=\n\n[A-Z]|\n##|\Z)', full_resume, re.IGNORECASE | re.DOTALL)
    
    if work_section_match:
        work_text = work_section_match.group(1).strip()
        print(f"✅ Found work section in full resume: {len(work_text)} chars")
        print(f"First 100 chars: {work_text[:100]}...")
    else:
        print("❌ No work section found in full resume!")

if __name__ == "__main__":
    debug_work_parsing()
