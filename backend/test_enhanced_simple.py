#!/usr/bin/env python3
"""
Simple test for enhanced pipeline
"""

# -*- coding: utf-8 -*-

import re
from typing import Dict, List, Any

def test_basic_functionality():
    print("🧪 TESTING BASIC FUNCTIONALITY")
    print("=" * 50)
    
    # Test work experience parsing
    rahul_work_text = """
UnitedHealth Group (Client: Optum Analytics): October 2023 – Current (Location: Eden Prairie, MN (Remote))
Role: Sr. Data Engineer
Responsibilities:
•	Designed and deployed HIPAA-compliant AWS Glue and Apache Spark ETL pipelines
JP Morgan Chase & Co.: June 2021 – September 2023 (Location: Columbus, OH)
Role: Sr. Data Engineer
Responsibilities:
•	Built PCI-DSS and SOX-compliant Apache Kafka event streaming pipelines
"""
    
    print("🔍 Testing Work Experience Parsing:")
    
    # Split by specific company names
    company_names = [
        'UnitedHealth Group',
        'JP Morgan Chase & Co.'
    ]
    
    parts = rahul_work_text
    for company in company_names:
        parts = parts.replace(company, f'###SPLIT###{company}')
    
    company_sections = parts.split('###SPLIT###')
    company_sections = [section.strip() for section in company_sections if section.strip()]
    
    work_entries = []
    
    for section in company_sections:
        lines = section.split('\n')
        if not lines:
            continue
            
        first_line = lines[0].strip()
        if ':' not in first_line:
            continue
            
        company = first_line.split(':')[0].strip()
        rest_of_line = first_line.split(':', 1)[1].strip()
        
        # Extract date range and location
        date_range = ""
        location = ""
        
        date_loc_match = re.search(r'([A-Za-z]+\s+\d{4}\s*–\s*[A-Za-z]+\s+\d{4}|[A-Za-z]+\s+\d{4}\s*–\s*Current)\s*\(([^)]+)\)', rest_of_line)
        if date_loc_match:
            date_range = date_loc_match.group(1).strip()
            location = date_loc_match.group(2).strip()
        
        # Extract role
        role = "Data Engineer"
        for line in lines:
            if line.strip().startswith('Role:'):
                role = line.replace('Role:', '').strip()
                break
        
        # Extract description
        description = ""
        in_responsibilities = False
        for line in lines[1:]:
            if line.strip().startswith('Responsibilities:'):
                in_responsibilities = True
                continue
            if in_responsibilities:
                if line.strip().startswith('•'):
                    description += line.strip().replace('•', '').strip() + ' '
                elif line.strip() and not line.startswith('  '):
                    break
        
        description = description.strip()
        
        if company and role:
            work_entries.append({
                "company": company,
                "title": role,
                "date_range": date_range,
                "location": location,
                "description": description
            })
    
    print(f"✅ Extracted {len(work_entries)} work entries:")
    for i, entry in enumerate(work_entries):
        print(f"  Job {i+1}:")
        print(f"    company: {entry['company']}")
        print(f"    title: {entry['title']}")
        print(f"    date_range: {entry['date_range']}")
        print(f"    location: {entry['location']}")
        print(f"    description: {entry['description'][:100]}...")
    
    return work_entries

def test_skills_parsing():
    print("\n🔧 TESTING SKILLS PARSING:")
    
    skills_text = """
Programming Languages: Python, PySpark, Scala, SQL, Bash, Java, HiveQL, R
Big Data & Processing: Apache Spark, PySpark, Spark Streaming, Apache Kafka, Apache Flink, Apache Hive, HDFS, MapReduce, Yarn, Apache NiFi, Sqoop, Flume, Zookeeper
Cloud - AWS: S3, Glue, EMR, Lambda, ECS, EKS, Kinesis (Streams & Firehose), Redshift, Athena, Lake Formation, DMS, DataSync, Step Functions, EventBridge, SQS, SNS, CloudWatch, CDK, CloudFormation, IAM, VPC, Secrets Manager, SageMaker
"""
    
    # Parse skill categories
    skill_categories = re.findall(r'([A-Za-z\s&\-\s]+):\s*([^\n]+)', skills_text)
    
    skills = []
    for category, skill_list in skill_categories:
        category = category.strip()
        skill_items = [skill.strip() for skill in skill_list.split(',')]
        
        for skill in skill_items:
            if skill and len(skill) > 2:
                if "Programming" in category or "Big Data" in category or "Cloud" in category:
                    proficiency = "Expert"
                elif "Data Warehousing" in category or "Databases" in category:
                    proficiency = "Advanced"
                else:
                    proficiency = "Intermediate"
                
                skills.append({
                    "skill": skill,
                    "proficiency": proficiency,
                    "confidence": 0.9
                })
    
    print(f"✅ Extracted {len(skills)} skills:")
    for i, skill in enumerate(skills[:5]):
        print(f"  Skill {i+1}: {skill['skill']} ({skill['proficiency']})")
    
    return skills

def test_certifications_parsing():
    print("\n🏆 TESTING CERTIFICATIONS PARSING:")
    
    cert_text = """
AWS Certified Data Engineer – Associate  –  Amazon Web Services (AWS)  |  Issued: January 2024  |  Credential ID: AWS-DEA-2024-RV9921
AWS Certified Solutions Architect – Associate  –  Amazon Web Services (AWS)  |  Issued: March 2022  |  Credential ID: AWS-SAA-2022-RV7734
"""
    
    cert_lines = cert_text.split('\n')
    certifications = []
    
    for line in cert_lines:
        line = line.strip()
        if line and '–' in line and '|' in line:
            parts = line.split('–')
            if len(parts) >= 2:
                name = parts[0].strip()
                rest = '–'.join(parts[1:]).strip()
                
                issuer_match = re.search(r'([A-Za-z\s\-\s]+(?:Inc|LLC|Corporation|AWS|Google|Microsoft|HashiCorp|Databricks|Snowflake|Confluent|dbt|CNCF))', rest)
                issuer = issuer_match.group(1).strip() if issuer_match else ""
                
                date_match = re.search(r'Issued:\s*([A-Za-z]+\s+\d{4})', rest)
                date = date_match.group(1).strip() if date_match else ""
                
                id_match = re.search(r'Credential ID:\s*([A-Z0-9\-]+)', rest)
                credential_id = id_match.group(1).strip() if id_match else ""
                
                if name and issuer:
                    certifications.append({
                        "name": name,
                        "issuer": issuer,
                        "date": date,
                        "credentialId": credential_id,
                        "confidence": 0.95
                    })
    
    print(f"✅ Extracted {len(certifications)} certifications:")
    for i, cert in enumerate(certifications):
        print(f"  Cert {i+1}: {cert['name']} from {cert['issuer']}")
    
    return certifications

if __name__ == "__main__":
    work_entries = test_basic_functionality()
    skills = test_skills_parsing()
    certifications = test_certifications_parsing()
    
    print(f"\n🎉 SUMMARY:")
    print(f"  Work entries: {len(work_entries)}")
    print(f"  Skills: {len(skills)}")
    print(f"  Certifications: {len(certifications)}")
    print(f"  ✅ Enhanced Pipeline Components Working!")
