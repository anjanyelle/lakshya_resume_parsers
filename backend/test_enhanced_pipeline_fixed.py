#!/usr/bin/env python3
"""
Test the fixed enhanced pipeline
"""

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.enhanced_pipeline_with_custom_models import EnhancedResumePipelineWithCustomModels
from app.services.custom_models import custom_models

def test_enhanced_pipeline():
    print("🧪 TESTING FIXED ENHANCED PIPELINE")
    print("=" * 50)
    
    # Test with Rahul's resume text
    rahul_resume = """
## RAHUL VENKATARAMAN
Sr. Data Engineer
LinkedIn: www.linkedin.com/in/rahul-venkataraman  |  Phone: +1 (469)-532-7814  |  rahul.venkataraman@gmail.com  |  Dallas, TX
## PROFESSIONAL SUMMARY
•	10+ years of experience as a Data Engineer designing, building, and optimizing large-scale data pipelines, ETL frameworks, and cloud-native data platforms across healthcare, financial services, retail, telecom, energy, and e-commerce domains.
•	Designed and deployed production-grade data orchestration pipelines using Apache Airflow, Dagster, and AWS Glue on AWS, leveraging ECS, EventBridge, Lambda, and S3 to ingest, transform, and deliver enterprise datasets reliably at scale.
## PROFESSIONAL EXPERIENCE
UnitedHealth Group (Client: Optum Analytics): October 2023 – Current (Location: Eden Prairie, MN (Remote))
Role: Sr. Data Engineer
Responsibilities:
•	Designed and deployed HIPAA-compliant AWS Glue and Apache Spark ETL pipelines ingesting 50M+ daily healthcare claims, member eligibility records, and clinical encounter data from HL7 FHIR APIs and EDI 837/835 feeds into an AWS S3 data lake partitioned by payer, date, and claim type.
JP Morgan Chase & Co.: June 2021 – September 2023 (Location: Columbus, OH)
Role: Sr. Data Engineer
Responsibilities:
•	Built PCI-DSS and SOX-compliant Apache Kafka event streaming pipelines ingesting real-time payment card transactions, wire transfers, and ACH events from 40+ source systems, processing 8M+ daily events into S3 data lake and Redshift for fraud analytics and regulatory capital reporting.
## TECHNICAL SKILLS
Programming Languages: Python, PySpark, Scala, SQL, Bash, Java, HiveQL, R
Big Data & Processing: Apache Spark, PySpark, Spark Streaming, Apache Kafka, Apache Flink, Apache Hive, HDFS, MapReduce, Yarn, Apache NiFi, Sqoop, Flume, Zookeeper
## CERTIFICATIONS
AWS Certified Data Engineer – Associate  –  Amazon Web Services (AWS)  |  Issued: January 2024  |  Credential ID: AWS-DEA-2024-RV9921
AWS Certified Solutions Architect – Associate  –  Amazon Web Services (AWS)  |  Issued: March 2022  |  Credential ID: AWS-SAA-2022-RV7734
## EDUCATION
Bachelor of Technology in Computer Science & Engineering – Osmania University, Hyderabad, India, 2009-2013
"""
    
    print("📋 Custom Models Status:")
    print(f"  Section models: {list(custom_models.section_models.keys())}")
    print(f"  Total models: {len(custom_models.section_models)}")
    
    # Initialize enhanced pipeline
    enhanced_pipeline = EnhancedResumePipelineWithCustomModels()
    
    print("\n🔍 Testing Resume Parsing:")
    result = enhanced_pipeline.parse_resume_complete(rahul_resume, use_ml=True)
    
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
    
    # Check skills
    skills = result.get("skills", [])
    print(f"\n🔧 SKILLS ({len(skills)} entries):")
    for i, skill in enumerate(skills[:5]):  # Show first 5
        print(f"  Skill {i+1}: {skill.get('skill', 'N/A')} ({skill.get('proficiency', 'N/A')})")
    
    # Check certifications
    certifications = result.get("certifications", [])
    print(f"\n🏆 CERTIFICATIONS ({len(certifications)} entries):")
    for i, cert in enumerate(certifications[:3]):  # Show first 3
        print(f"  Cert {i+1}: {cert.get('name', 'N/A')} from {cert.get('issuer', 'N/A')}")
    
    # Check education
    education = result.get("education", [])
    print(f"\n🎓 EDUCATION ({len(education)} entries):")
    for i, edu in enumerate(education):
        print(f"  Edu {i+1}: {edu.get('university', 'N/A')} ({edu.get('date', 'N/A')})")
    
    # Check if result is meaningful
    is_meaningful = bool(basics) or bool(work)
    print(f"\n✅ MEANINGFUL DATA: {'YES' if is_meaningful else 'NO'}")
    
    if is_meaningful:
        print("\n🎉 ENHANCED PIPELINE IS WORKING!")
        print("✅ Perfect JSON structure can be generated!")
    else:
        print("\n❌ ENHANCED PIPELINE NEEDS MORE WORK!")
        print("❌ No meaningful data extracted!")
    
    return result

if __name__ == "__main__":
    test_enhanced_pipeline()
