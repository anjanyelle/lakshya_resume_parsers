import sys
import os
# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'backend'))

from app.services.parser.work_experience_parser import WorkExperienceParser
from app.services.parser.section_parser import SectionParser

def test_ramu_gara_parsing():
    """Test parsing of Ramu Gara's resume with Client/Role/Location format"""
    
    # Sample work experience section from Ramu Gara's resume
    resume_text = """
PROFESSIONAL EXPERIENCE:

Client: Morgan Stanley                                                                                                                                                            New York, NY
Role: SR. BIG DATA ENGINEER                                                                                                                                             June 2023 - Current
Responsibilities:

•	Designed and implemented multi-layer data lakehouse architecture using AWS S3, AWS Glue, AWS Redshift, Databricks, establishing Bronze, Silver, Gold medallion layers with Dimensional modeling, Snowflake schema, and Data Vault 2.0 for healthcare and retail analytics workflows.
•	Developed batch and streaming ETL/ELT pipelines using AWS Glue, Databricks, Apache Spark, Kafka, Scala, ingesting real-time patient transactions, inventory updates, and device telemetry into S3, enabling analytics-ready datasets for enterprise decision-making.
•	Established enterprise-grade governance and security controls compliant with GDPR, PCI-DSS, SOX using RBAC, Row-Level Security, Object-Level Security, data masking, encryption, audit logging in AWS Redshift, S3, ALATION.
•	Optimized complex SQL queries and Spark transformations using AWS Redshift, Databricks, Parquet, redesigning Dimensional models with indexing, partitioning, and columnar storage to reduce compute costs and improve analytics performance.
•	Implemented Infrastructure as Code using Terraform, AWS CloudFormation to provision AWS Glue jobs, Databricks workspaces, S3 buckets, Redshift clusters, ensuring consistent, version-controlled deployments across development, staging, and production environments.
•	Integrated CI/CD pipelines using AWS CodePipeline, GitHub Actions, Jenkins, automating deployment of ETL pipelines, Databricks notebooks, and Scala applications with testing, rollback strategies, and Git version control.
•	Built real-time streaming pipelines using Kafka, AWS Kinesis, Databricks Structured Streaming, Scala, capturing device telemetry, patient behavior signals, and operational events with sub-second latency processed into S3 storage layers.
•	Delivered downstream analytics using Power BI, Tableau, AWS Redshift, Databricks, enabling dashboards for inventory, sales trends, patient insights, and operational KPIs using Direct Query and Import modes.
•	Developed centralized data catalog and metadata repository using ALATION, enabling self-service data discovery, tracking data lineage, and enforcing data stewardship across finance, supply chain, marketing, and operations teams.
•	Designed incremental data loading patterns using Change Data Capture, SQL Server, Oracle, Informatica PowerCenter, efficiently replicating transactional data from on-premises systems into AWS S3 and Redshift.
•	Led migration of legacy ETL workflows from Informatica, DataStage, SSIS to cloud-native AWS Glue, Databricks, Airflow, reducing infrastructure costs and improving maintainability of Spark-based pipelines.
•	Implemented data validation and reconciliation frameworks using Scala, Databricks notebooks, comparing source-to-target row counts, column-level checksums, and business rules across Bronze, Silver, and Gold layers to ensure quality standards.
•	Enforced data quality gates in CI/CD pipelines using AWS CodePipeline, preventing deployment of pipelines failing validation thresholds, ensuring downstream analytics and dashboards remain accurate and reliable.
•	Collaborated with data scientists to design feature engineering pipelines using Databricks, Spark MLlib, Scala, Parquet, supporting predictive modeling for customer churn, product recommendations, and operational KPIs with curated Gold-layer datasets.
•	Established monitoring, logging, and alerting using AWS CloudWatch, Databricks metrics, Grafana, Log Analytics, proactively detecting pipeline failures, bottlenecks, and SLA breaches with automated notifications for critical issues.
•	Mentored junior and mid-level engineers through code reviews, enforcing coding standards, Git version control, and adherence to enterprise data modeling guidelines including Dimensional modeling, Snowflake schema, Data Vault principles.
•	Architected multi-region disaster recovery strategy with S3 geo-redundant storage, Redshift failover, Databricks replication, implementing runbooks and conducting quarterly disaster recovery drills for operational continuity.
•	Integrated Microsoft Fabric to unify data engineering, data science, and BI workloads, streamlining governance and cost management while evaluating Fabric capabilities including data warehousing, real-time analytics, and OneLake storage.
•	Designed secure data sharing and access models using RBAC, RLS, OLS, AWS Redshift, Databricks, enforcing least-privilege access and encryption with Transparent Data Encryption and customer-managed keys.
•	Developed custom data ingestion connectors using Apache NiFi, Python, extracting product catalogs, promotions, and supplier information from APIs, FTP servers, and SaaS platforms with error handling and schema validation.
•	Collaborated with enterprise architects to translate business requirements into technical solutions, producing design documents, data flow diagrams, and architecture decision records while participating in Agile sprint planning, stand-ups, and retrospectives.
•	Implemented advanced SQL optimization using AWS Redshift, Databricks, including query plan analysis, materialized views, distribution keys, columnstore indexes, Spark caching, broadcast joins, and adaptive query execution for high-concurrency workloads.
•	Conducted proof-of-concept evaluations for DBT, web scraping frameworks, MongoDB, analyzing feasibility for competitive intelligence, unstructured feedback, and product reviews, providing recommendations to senior leadership for future platform investments.
•	Optimized ETL and analytics workloads by applying Databricks Spark caching, Parquet partitioning, indexing, reducing compute costs and improving operational efficiency across high-volume retail and healthcare datasets.
•	Ensured end-to-end platform reliability, integrating batch and streaming pipelines, governance, monitoring, and analytics frameworks using AWS Glue, Databricks, Redshift, Kinesis, Kafka, Power BI, ALATION, supporting enterprise-scale decision-making across healthcare and retail domains.

Environments: 
AWS S3, AWS Glue, AWS Redshift, Databricks, Apache Spark, Kafka, AWS Kinesis, Scala, SQL, SQL Server, Oracle, Informatica PowerCenter, DataStage, SSIS, Airflow, Terraform, AWS CloudFormation, AWS CodePipeline, GitHub Actions, Jenkins, Python, Power BI, Tableau, ALATION, DBT, MongoDB, Grafana, Log Analytics, Microsoft Fabric, OneLake

Client: Humana                                                                                                                                                                Louisville, KY
Role: SR DATA ENGINEER                                                                                                                             August 2020 - May 2023
Responsibilities:
•	Designed and implemented multi-layer data lakehouse architecture using Azure Cloud, ADLS Gen2, Azure Databricks, Azure Synapse Analytics, establishing Bronze, Silver, Gold medallion layers with Dimensional modeling, Snowflake schema, and Data Vault 2.0 for health analytics workflows.
•	Developed batch and streaming ETL/ELT pipelines using Azure Data Factory, Databricks, Apache Spark, Kafka, Scala, ingesting point-of-care transactions, device telemetry, and patient data into ADLS Gen2, enabling analytics-ready datasets for operational insights.
•	Established enterprise-grade governance and security controls compliant with GDPR, PCI-DSS, SOX, implementing RBAC, Row-Level Security, Object-Level Security, encryption, data masking, audit logging using Azure Synapse Analytics, ALATION for metadata management.
•	Optimized complex SQL queries and Spark transformations using Azure Synapse, Databricks, Parquet, redesigning Dimensional models with indexing, partitioning, and columnar storage strategies to reduce compute costs and improve analytics performance.
•	Implemented Infrastructure as Code using Terraform, ARM templates to provision Azure Data Factory, Databricks workspaces, ADLS storage accounts, Azure Synapse, ensuring consistent, version-controlled deployments across development, staging, and production environments.
•	Integrated CI/CD pipelines using Azure DevOps, GitHub Actions, automating deployment of data pipelines, Databricks notebooks, and Scala applications with testing, rollback strategies, and Git-based version control for continuous delivery.
•	Developed real-time streaming pipelines using Kafka, Azure Event Hubs, Databricks Structured Streaming, Scala, capturing patient telemetry, clinical events, and operational signals with sub-second latency processed into ADLS Gen2 storage layers.
•	Enabled downstream analytics using Power BI, Azure Synapse, Databricks, providing dashboards for patient insights, inventory trends, and operational KPIs with Direct Query and Import modes for near-real-time monitoring.
•	Built centralized data catalog and metadata repository using ALATION, enabling self-service data discovery, documenting data lineage, and enforcing stewardship across clinical, finance, supply chain, and operational teams.
•	Designed incremental data loading patterns using Change Data Capture, SQL Server, Oracle, Informatica PowerCenter, efficiently extracting and replicating transactional healthcare data from on-premises systems into ADLS Gen2 and Azure Synapse Analytics.
•	Led migration of legacy ETL workflows from Informatica, DataStage, SSIS to cloud-native Azure Data Factory, Databricks, Apache Airflow, reducing infrastructure costs and improving maintainability with Spark-based pipelines.
•	Implemented data validation and reconciliation frameworks using Scala, Databricks notebooks, comparing source-to-target row counts, column-level checksums, and business rule validations across Bronze, Silver, and Gold layers to ensure data quality.
•	Enforced data quality gates in CI/CD workflows using Azure DevOps, preventing deployment of pipelines failing validation thresholds and ensuring downstream analytics and dashboards remain accurate and reliable.
•	Collaborated with data scientists to design feature engineering pipelines using Databricks, Spark MLlib, Scala, Parquet, supporting predictive modeling for patient outcomes, resource optimization, and operational KPIs with curated Gold-layer datasets.
•	Established monitoring, logging, and alerting using Azure Monitor, Log Analytics, Grafana, Databricks job metrics, proactively detecting pipeline failures, bottlenecks, SLA breaches, and automating notifications for critical incidents.
•	Mentored junior and mid-level engineers through code reviews, enforcing coding standards, Git version control, and adherence to enterprise data modeling guidelines including Dimensional modeling, Snowflake schema, Data Vault 2.0 principles.
•	Architected multi-region disaster recovery strategy with ADLS Gen2 geo-redundancy, Azure Synapse failover, Databricks replication, implementing runbooks and conducting quarterly disaster recovery drills for business continuity.
•	Integrated Microsoft Fabric to unify data engineering, data science, and BI workloads, streamlining governance, cost management, and evaluating Fabric features for data warehousing, real-time analytics, and OneLake storage integration.
•	Designed secure data sharing and access models using RBAC, Row-Level Security, Object-Level Security, Azure Synapse, Databricks, enforcing least-privilege access with Transparent Data Encryption and customer-managed key encryption.
•	Developed custom data ingestion connectors using Apache NiFi, Python, extracting product catalogs, promotional data, and supplier information from external APIs, FTP servers, and partner SaaS platforms with standardized error handling and validation workflows.
•	Collaborated with enterprise architects to translate healthcare analytics requirements into technical solutions, producing design documents, data flow diagrams, and architecture decision records while participating in Agile sprint planning, stand-ups, and retrospectives.
•	Implemented advanced SQL optimization using Azure Synapse, Databricks, including query plan analysis, materialized views, distribution keys, columnstore indexes, Spark caching, broadcast joins, and adaptive query execution for high-concurrency workloads.
•	Conducted proof-of-concept evaluations for DBT, web scraping frameworks, MongoDB, analyzing competitive intelligence, unstructured patient feedback, and operational metrics, presenting findings and recommendations to senior leadership for future platform enhancements.
•	Optimized ETL and analytics workloads by applying Databricks Spark caching, Parquet partitioning, indexing, reducing compute costs and improving operational efficiency across high-volume healthcare and retail datasets.
•	Ensured end-to-end platform reliability by integrating batch and streaming pipelines, governance, monitoring, and analytics frameworks using Azure Data Factory, Databricks, Azure Synapse, Kafka, Power BI, ALATION, supporting enterprise-scale healthcare decision-making.

Environments: Azure Cloud, ADLS Gen2, Azure Databricks, Azure Synapse Analytics, Azure Data Factory, Apache Spark, Kafka, Azure Event Hubs, Scala, SQL, SQL Server, Oracle, Informatica PowerCenter, DataStage, SSIS, Apache Airflow, Terraform, ARM templates, Azure DevOps, GitHub Actions, Git, Python, Power BI, ALATION, DBT, MongoDB, Grafana, Log Analytics, Microsoft Fabric, OneLake, Apache NiFi
"""
    
    print("=" * 60)
    print("TESTING RAMU GARA RESUME PARSING")
    print("=" * 60)
    
    # Extract work experience section
    work_start = resume_text.find("PROFESSIONAL EXPERIENCE:")
    if work_start == -1:
        print("ERROR: Could not find PROFESSIONAL EXPERIENCE section")
        return
    
    work_text = resume_text[work_start:]
    
    # Test work experience parsing
    work_parser = WorkExperienceParser()
    
    # First test: extract individual jobs
    print("\nTESTING JOB SPLITTING")
    print("-" * 40)
    individual_jobs = work_parser.extract_individual_jobs(work_text)
    print(f"Number of jobs extracted: {len(individual_jobs)}")
    
    for i, job in enumerate(individual_jobs):
        print(f"\n--- Job {i+1} ---")
        print(f"Length: {len(job)} characters")
        print(f"First 200 chars: {job[:200]}")
        
        # Parse individual job
        parsed_jobs = work_parser.parse_experience_section(job)
        if parsed_jobs:
            for j, parsed_job in enumerate(parsed_jobs):
                print(f"\n--- Parsed Job {j+1} ---")
                print(f"Company: {parsed_job.company}")
                print(f"Title: {parsed_job.title}")
                print(f"Location: {parsed_job.location}")
                print(f"Start Date: {parsed_job.start_date}")
                print(f"End Date: {parsed_job.end_date}")
                print(f"Description length: {len(parsed_job.description)}")
                print(f"Bullets count: {len(parsed_job.bullets) if parsed_job.bullets else 0}")
                if parsed_job.bullets:
                    print(f"First bullet: {parsed_job.bullets[0][:100]}...")
        else:
            print("Failed to parse job")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    test_ramu_gara_parsing()
