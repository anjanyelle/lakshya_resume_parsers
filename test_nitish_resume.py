#!/usr/bin/env python3
"""
Test script to verify section splitting fixes for Nitish Rao's resume
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'ai-service'))

from parsers.section_splitter import SectionSplitter
from parsers.section_validator import SectionValidator
import json

def test_nitish_resume():
    """Test the fixed section splitting logic with Nitish's resume"""
    
    # Nitish's resume text (extracted from the JSON)
    resume_text = """Name: Nitish Rao B
SR. BIG DATA ENGINEER
Linkedin: www.linkedin.cominnitishraob  Phone: 4692696680 nitishb2317@gmail.com
PROFESSIONAL SUMMARY: Laid the foundation for over eight years of enterprise data engineering experience, specializing in Palantir Foundry platforms, where complex datasets were transformed into governed, high-trust data products supporting analytics, operational reporting, and decision intelligence across regulated industries. Built scalable ETL and ELT pipelines using Python, PySpark, and SQL, enabling ingestion, transformation, and curation of high-volume structured and semi-structured datasets while maintaining strong performance, recoverability, and schema evolution strategies within Foundry environments. TECHNICAL SKILLS: Databases  Tools: MySQL, Teradata 1514, Oracle 11g10g, MS SQL Server 20142012, Erwin 89
Cloud Environment: GCP (Cloud storage, Bigquery, DataProc, Functions, GKE, Spanner), AWS (Redshift, EMR, Glue, S3, Lambda, Athena, Snowflake, EC2, RDS, Cloud Watch, VPC, SQS, Jenkins), Azure (Databricks, Data lake, Data factory, Blob storage, SQL, HDInsight, Fabric, CosmosDB)
Big Data Ecosystem: Spark, Hive, Kafka, HDFS, Airflow, NiFi, Spark Streaming, Sqoop, Flume, MapReduce, Yarn, Zookeeper
PROFESSIONAL EXPERIENCE: UnitedHealth Group: November 2022 - Current (Location: Minnetonka, MN)
Role: SR. BIG DATA ENGINEER
Responsibilities: Built enterprise-grade healthcare ingestion pipelines in Palantir Foundry using Python and PySpark, integrating claims, eligibility, and provider datasets from AWS S3, relational sources, and APIs to support analytics, reporting, and regulatory compliance workflows. Developed ontology-driven healthcare data products by modeling members, encounters, providers, and claims in Foundry Ontology, establishing authoritative datasets with lineage, provenance, and governed semantics aligned to clinical and operational reporting standards. Environment: Palantir Foundry, Foundry Ontology, Foundry Pipelines, Foundry Code Workbooks, Python, PySpark, SQL, AWS S3, AWS EMR, AWS Kinesis, Parquet, Delta Lake, Git, CICD, RBAC, HIPAA Compliance, REST APIs, JSON, CloudWatch. Wells Fargo: January 2020 - October 2022 (Location: San Francisco, CA)
ROLE: SR DATA ENGINEER
Responsibilities: Constructed enterprise banking data pipelines in Palantir Foundry leveraging Python and SQL, ingesting transactional, customer, and risk datasets from Azure Data Lake, relational systems, and secure APIs for analytics and regulatory reporting. Designed ontology models representing accounts, transactions, customers, and products within Foundry Ontology, enabling consistent semantic definitions and governed reuse across fraud, compliance, and financial reporting use cases. Environments: Palantir Foundry, Foundry Ontology, Foundry Code Workbooks, Python, PySpark, SQL, Azure Data Lake, Azure Databricks, Azure Event Hubs, Azure DevOps, Git, Parquet, Delta Lake, RBAC, REST APIs, JSON, GCP Cloud Storage, Azure Monitor. Honeywell: March 2017 - December 2019 (Location: Charlotte, NC)
ROLE: DATA ENGINEER  DATA ANALYST
Responsibilities: Built foundational manufacturing data pipelines using Palantir Foundry, ingesting production, sensor, and quality datasets from GCP Cloud Storage, on-prem systems, and industrial APIs to support operational analytics initiatives. Developed early ontology models capturing assets, production lines, sensors, and events within Foundry Ontology, establishing consistent semantics for manufacturing performance and reliability analytics. Environments: Palantir Foundry, Foundry Ontology, Python, PySpark, SQL, GCP Cloud Storage, GCP Dataproc, Parquet, Git, REST APIs, JSON, Time-Series Data, Batch ETL, RBAC, Linux, Agile Scrum, Monitoring Logs, Manufacturing Systems. Equifax: February 2016 - February 2017 (Location: Atlanta, GA)
ROLE: DATA ENGINEER  MIGRATION SPECIALIST
Responsibilities: Built robust Clinical Data Integration platform using Azure Cloud, improving data integration efficiency. Reduced integration time for financial data sources by 65 while maintaining data integrity. Developed and managed data ingestion pipelines using Talend ETL and Azure Data Factory (ADF) from clinical sources. Processed over 2TB of consumer credit data daily with high reliability. Environments: Azure Cloud, Talend ETL, Azure Data Factory (ADF), Apache Airflow, Azure SQL Database, Azure Data Lake Storage, HIPAA Compliance, FHIR, OMOP, HL7, Epic, Azure Databricks, Machine Learning, Data Validation, Master Data Management, Data Lineage, Batch Processing. Inno Minds: May 2014 - December 2015 (Location: Pune, India)
ROLE: ETL DEVELOPER
Responsibilities: Created scalable ETL pipeline using AWS services, Informatica, and Talend, combining data from relational databases, NoSQL databases, and flat files. Processed over 500GB of daily manufacturing data from 12 different source systems with high accuracy. Set up AWS S3 storing raw, staging, and transformed data securely and efficiently, creating smooth ingestion workflows. Implemented bucket policies and encryption ensuring regulatory compliance while maintaining fast access to production data
Environments: AWS S3, AWS Glue, AWS Lambda, AWS CloudWatch, AWS Redshift, Informatica PowerCenter, Talend Open Studio, Tableau, MySQL, PostgreSQL, MongoDB, ETL Pipelines, Data Transformation, Data Integration, Data Cleansing, Data Enrichment, Data Quality, Batch Processing, Parallel Processing, Data Extraction, Data Loading, Relational Databases, NoSQL Databases, CSV Processing, JSON Processing, Data Cataloging, Job Scheduling, Performance Monitoring, Data Visualization
CERTIFICATION
 CSCP: Certified Supply Chain Professional ASCM
 LSSBB: Lean Six Sigma Certification Black Belt
 PMP: Project Management Professional Project Management Institute
EDUCATION: Bachelors in computer and information science Aug 2010  May 2014
Sreenidhi Institute Of Science and Technology"""

    print("Testing Nitish Rao's resume with fixed section splitting logic...")
    print("=" * 60)
    
    # Initialize section splitter
    splitter = SectionSplitter()
    
    # Split sections
    sections = splitter.split_sections(resume_text)
    
    print("Initial sections detected:")
    for section_name, content in sections.items():
        print(f"  {section_name}: {len(content)} chars")
    
    print("\n" + "=" * 60)
    
    # Initialize validator and validate sections
    try:
        validator = SectionValidator()
        corrected_sections, metadata = validator.validate_and_correct(sections)
        
        print("After validation:")
        for section_name, content in corrected_sections.items():
            print(f"  {section_name}: {len(content)} chars")
        
        print("\nValidation metadata:")
        print(json.dumps(metadata, indent=2))
        
        # Check if skills section is properly detected
        if 'skills' in corrected_sections:
            print("\n✅ SUCCESS: Skills section properly detected!")
            skills_content = corrected_sections['skills']
            print(f"Skills content preview: {skills_content[:200]}...")
        else:
            print("\n❌ ISSUE: Skills section still missing!")
            
        # Check education section content
        if 'education' in corrected_sections:
            edu_content = corrected_sections['education']
            if len(edu_content) < 500:  # Should be small
                print("✅ SUCCESS: Education section content looks correct!")
                print(f"Education content: {edu_content}")
            else:
                print(f"❌ ISSUE: Education section too large ({len(edu_content)} chars) - still contains other content!")
                
    except Exception as e:
        print(f"Error during validation: {e}")
        print("Falling back to initial sections...")
        corrected_sections = sections
    
    return corrected_sections

if __name__ == "__main__":
    test_nitish_resume()
