#!/usr/bin/env python3
"""
Test violation counts to understand why education is chosen
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'ai-service'))

from parsers.section_validator import SectionValidator

def test_violations():
    """Test violation counts for 'other' section"""
    
    # The actual 'other' section content from Nitish's resume
    other_content = """Name: Nitish
Rao B
SR.
BIG DATA ENGINEER
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
Environments: AWS S3, AWS Glue, AWS Lambda, AWS CloudWatch, AWS Redshift, Informatica PowerCenter, Talend Open Studio, Tableau, MySQL, PostgreSQL, MongoDB, ETL Pipelines, Data Transformation, Data Integration, Data Cleansing, Data Enrichment, Data Quality, Batch Processing, Parallel Processing, Data Extraction, Data Loading, Relational Databases, NoSQL Databases, CSV Processing, JSON Processing, Data Cataloging, Job Scheduling, Performance Monitoring, Data
Visualization"""

    print("Testing violation counts...")
    
    # Initialize validator
    validator = SectionValidator()
    
    # Get entity profile
    profile = validator.get_entity_profile(other_content)
    
    # Test all section types
    section_types = ['experience', 'education', 'skills', 'summary', 'projects', 'certifications']
    
    print(f"Entity profile: {profile}")
    print("\nViolation counts:")
    
    for section_type in section_types:
        expected = validator.get_expected_fingerprint(section_type)
        violations = validator._count_fingerprint_violations(profile, expected)
        print(f"  {section_type}: {violations} violations")
    
    return profile

if __name__ == "__main__":
    test_violations()
