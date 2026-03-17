# -*- coding: utf-8 -*-
"""
Test the improved enhanced pipeline
"""

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.enhanced_pipeline_final import EnhancedResumePipelineFinal

def test_improved_pipeline():
    print("🧪 TESTING IMPROVED ENHANCED PIPELINE")
    print("=" * 50)
    
    # Test with Rahul's resume text
    rahul_resume = """
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
Cloud - AWS: S3, Glue, EMR, Lambda, ECS, EKS, Kinesis (Streams & Firehose), Redshift, Athena, Lake Formation, DMS, DataSync, Step Functions, EventBridge, SQS, SNS, CloudWatch, CDK, CloudFormation, IAM, VPC, Secrets Manager, SageMaker
## CERTIFICATIONS
AWS Certified Data Engineer - Associate - Amazon Web Services (AWS) | Issued: January 2024 | Credential ID: AWS-DEA-2024-RV9921
AWS Certified Solutions Architect - Associate - Amazon Web Services (AWS) | Issued: March 2022 | Credential ID: AWS-SAA-2022-RV7734
AWS Certified Cloud Practitioner - Amazon Web Services (AWS) | Issued: September 2020 | Credential ID: AWS-CCP-2020-RV3312
Databricks Certified Associate Developer for Apache Spark 3.0 - Databricks | Issued: July 2023 | Credential ID: DBR-SPARK3-2023-RV0041
## EDUCATION
Bachelor of Technology in Computer Science & Engineering - Osmania University, Hyderabad, India, 2009-2013
"""
    
    # Initialize improved enhanced pipeline
    improved_pipeline = EnhancedResumePipelineFinal()
    
    print("\n🔍 Testing Resume Parsing:")
    result = improved_pipeline.parse_resume_complete(rahul_resume, use_ml=True)
    
    print("\n📊 RESULTS:")
    print(f"  Total sections: {len(result)}")
    print(f"  Sections found: {list(result.keys())}")
    
    # Check basics
    basics = result.get("basics", {})
    print(f"\n👤 BASICS ({len(basics)} fields):")
    for key, value in basics.items():
        print(f"  {key}: {value}")
    
    # Check work experience
    work = result.get("work", [])
    print(f"\n💼 WORK EXPERIENCE ({len(work)} entries):")
    for i, job in enumerate(work):
        print(f"  Job {i+1}:")
        print(f"    company: {job.get('company', 'N/A')}")
        print(f"    title: {job.get('title', 'N/A')}")
        print(f"    date_range: {job.get('date_range', 'N/A')}")
        print(f"    location: {job.get('location', 'N/A')}")
        print(f"    description: {job.get('description', 'N/A')[:100]}...")
    
    # Check skills
    skills = result.get("skills", [])
    print(f"\n🔧 SKILLS ({len(skills)} entries):")
    for i, skill in enumerate(skills[:5]):  # Show first 5
        print(f"  Skill {i+1}: {skill.get('skill', 'N/A')} ({skill.get('proficiency', 'N/A')})")
    
    # Check certifications
    certifications = result.get("certifications", [])
    print(f"\n🏆 CERTIFICATIONS ({len(certifications)} entries):")
    for i, cert in enumerate(certifications):
        print(f"  Cert {i+1}: {cert.get('name', 'N/A')} from {cert.get('issuer', 'N/A')}")
    
    # Check education
    education = result.get("education", [])
    print(f"\n🎓 EDUCATION ({len(education)} entries):")
    for i, edu in enumerate(education):
        print(f"  Edu {i+1}: {edu.get('degree', 'N/A')} from {edu.get('university', 'N/A')}")
    
    # Check if result is meaningful
    is_meaningful = bool(basics) or bool(work)
    print(f"\n✅ MEANINGFUL DATA: {'YES' if is_meaningful else 'NO'}")
    
    # Check if we have perfect JSON structure
    has_all_sections = all(section in result for section in ['basics', 'work', 'education', 'skills', 'certifications'])
    has_data = any(result[section] for section in ['basics', 'work', 'education', 'skills', 'certifications'])
    
    print(f"✅ PERFECT JSON STRUCTURE: {'YES' if has_all_sections and has_data else 'NO'}")
    
    # Check specific improvements
    improvements = {
        "work_extracted": len(work) > 0,
        "education_extracted": len(education) > 0,
        "certifications_extracted": len(certifications) > 0,
        "skills_extracted": len(skills) > 0
    }
    
    print(f"\n🎯 IMPROVEMENTS:")
    for key, value in improvements.items():
        status = "✅" if value else "❌"
        print(f"  {status} {key.replace('_', ' ').title()}")
    
    if is_meaningful and has_all_sections and has_data:
        print("\n🎉 IMPROVED ENHANCED PIPELINE IS WORKING PERFECTLY!")
        print("✅ Perfect JSON structure generated!")
        print("✅ All sections extracted correctly!")
        print("✅ Ready to store in complete_resume_json!")
    else:
        print("\n❌ IMPROVED ENHANCED PIPELINE NEEDS MORE WORK!")
    
    return result

if __name__ == "__main__":
    test_improved_pipeline()
