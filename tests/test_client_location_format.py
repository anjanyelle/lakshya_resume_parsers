import sys
import os
# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'backend'))

from app.services.parser.work_experience_parser import WorkExperienceParser
import json

def test_client_location_format():
    """Test parsing of Client/Location/Role format"""
    
    # Client/Location format resume text
    text = """
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

Client: Lowe's                                                                                                                                                                Mooresville, NC
Role: DATA ENGINEER                                                                                                                                       October 2017 - July 2020
Responsibilities:

•	Designed enterprise-grade transportation data architectures using BigQuery, SQL Server, MySQL, Google Cloud Storage, implementing Dimensional modeling and Data Vault 2.0 methodologies to enable regulatory reporting and ensure PCI-DSS and SOX compliance across pipelines.
•	Developed end-to-end ETL/ELT pipelines with Informatica PowerCenter, Apache Airflow, SSIS, Python, Great Expectations, ingesting shipment, inventory, and customer data into BigQuery Bronze, Silver, Gold layers with validation for downstream analytics.
•	Built real-time streaming pipelines using Apache Kafka, Google Pub/Sub, Apache Beam, Google Cloud Dataflow, processing high-volume shipment and e-commerce transactions with sub-second latency, RBAC-based access controls, and automated data quality validations.
•	Implemented batch processing frameworks using Apache Spark, Databricks, SQL, Parquet, transforming daily logistics transactions, optimizing query performance, storage efficiency, and reducing Google Cloud Storage costs for business intelligence workflows.
•	Established security protocols using RBAC, Row-Level Security, data masking, encryption, BigQuery, SQL Server, protecting PII and sensitive logistics data while ensuring compliance with PCI-DSS, SOX, GDPR during ETL/ELT processes.
•	Developed reusable data ingestion frameworks using Python, Shell scripting, Apache Flume, FTP, Apache Airflow, automating extraction from legacy mainframes and partner feeds, ensuring reliable availability of critical shipment and inventory datasets in BigQuery.
•	Designed CI/CD pipelines using Azure DevOps, GitHub Actions, Jenkins, automating testing and deployment of ETL/ELT scripts, enforcing version control and code review standards for Apache Spark and SQL transformations.
•	Implemented Infrastructure as Code using Terraform, provisioning BigQuery datasets, Google Cloud Dataflow jobs, Pub/Sub topics, GCS buckets, ensuring consistent configuration, automated scaling, and disaster recovery for transportation analytics workloads.
•	Collaborated with governance teams to implement metadata management and data lineage solutions using Python, BigQuery, MySQL, SQL Server, documenting end-to-end data flows to support SOX compliance and regulatory reporting for logistics analytics.
•	Built dimensional data models using Star schema, BigQuery SQL to support shipment tracking, customer segmentation, and operational reporting, translating business requirements into aggregated fact tables and Looker dashboards with RBAC and RLS applied.
•	Optimized ETL performance using partitioning, clustering, incremental load patterns, CDC, and in-memory Spark processing with Parquet, reducing batch processing times and improving efficiency for high-volume transportation datasets.
•	Developed data quality validation frameworks using Great Expectations, Python, Apache Airflow, enforcing completeness checks, business rules, and automated alerts to maintain accurate and reliable logistics datasets for downstream analytics.
•	Integrated transportation datasets with predictive analytics and Looker dashboards, providing curated BigQuery datasets, implementing feature engineering pipelines with Apache Spark, SQL, Python to support delivery performance, demand forecasting, and operational insights.
•	Managed NoSQL storage using Cassandra, designing scalable models to handle millions of daily shipment and inventory events, integrating with Apache Spark for distributed processing and JSON/Avro serialization for BigQuery ingestion.
•	Led technical design sessions with architects and stakeholders to define data standards and reusable ETL/ELT frameworks using Apache Airflow, Python, SQL, establishing organizational best practices for transportation data engineering initiatives.
•	Implemented monitoring and logging using Google Cloud Operations, Apache Airflow, Python scripts, tracking job execution, pipeline failures, and SLA adherence, maintaining 99.5% uptime for transportation BigQuery datasets and Looker reporting.
•	Supported production deployments and incident resolution for ETL pipelines, performing root cause analysis for Apache Spark and SQL failures, implementing fixes via CI/CD pipelines using Git and Jenkins to minimize disruption.
•	Conducted code reviews and mentored junior engineers on SQL optimization, Apache Spark, Dimensional modeling, GDPR, PCI-DSS compliance, enforcing peer review and technical documentation standards to improve team productivity and quality of delivery.
•	Developed automated retry and error-handling logic for ETL pipelines using Python, Apache Airflow, Shell scripting, ensuring reliable extraction, transformation, and loading of large-scale shipment, inventory, and customer datasets into BigQuery.
•	Implemented scalable data processing patterns with Apache Spark, BigQuery, Parquet, Python, handling high-volume shipment, inventory, and customer interactions, improving query performance, reporting efficiency, and enabling actionable insights for transportation operations.

Environments: BigQuery, SQL Server, MySQL, Google Cloud Storage, Apache Spark, Databricks, Apache Kafka, Google Pub/Sub, Apache Beam, Google Cloud Dataflow, Apache Airflow, Azure DevOps, Jenkins, GitHub Actions, Git, Python, Shell scripting, Informatica PowerCenter, SSIS, Great Expectations, Looker, Cassandra, Parquet, Terraform, FTP

Client: Paychex                                                                                                                                                         Rochester, NY
Role: DATA ENGINEER                                                                                                                                    December 2015 – September 2017
Responsibilities:
•	Built enterprise-grade network data integration platform on Azure Cloud, consolidating telemetry from globally distributed devices, enabling seamless data flow, centralized analytics, improved monitoring visibility, and operational efficiency across multi-region enterprise network environments.
•	Developed scalable ingestion pipelines using Talend ETL, Azure Data Factory, Python, SQL, processing high-volume network monitoring and security appliance data, performing extraction, transformation, validation, and delivery to analytics-ready stores supporting operational reporting.
•	Executed large-scale data migration from legacy network management systems to SDN platforms, ensuring schema compatibility, data accuracy, rollback readiness, and uninterrupted service during cloud transformation initiatives across global enterprise networks.
•	Built and managed workflow orchestration using Apache Airflow, Azure Data Factory, Talend ETL, coordinating distributed ETL jobs, dependency management, and failure recovery aligned with regional compliance and operational time zones for continuous observability.
•	Implemented optimized relational storage using Azure SQL Database, designing schemas, indexes, and query optimizations to store structured network performance metrics for rapid retrieval by engineering and operations teams.
•	Configured scalable storage with Azure Data Lake Storage, retaining semi-structured and unstructured network telemetry for cost-effective long-term retention, historical trend analysis, capacity planning, and security investigations across global infrastructures.
•	Integrated heterogeneous data sources including router logs, switch telemetry, and firewall alerts using Talend ETL, enabling unified cross-layer correlation, faster root cause analysis, and improved troubleshooting across multi-region network environments.
•	Implemented enterprise-grade security controls using Azure Security, RBAC, encryption, anonymization, ensuring protection of configuration and telemetry data while meeting international privacy compliance standards.
•	Led migration of legacy on-premises monitoring platforms to cloud-native solutions on Azure Cloud, improving observability, scalability, resilience, and reducing operational overhead for global network operations teams.
•	Developed predictive capacity forecasting models using Azure Databricks, Python, Spark, analyzing historical traffic patterns to forecast bandwidth utilization, identify growth trends, and guide proactive infrastructure planning for expanding enterprise networks.
•	Built real-time anomaly detection pipelines using Azure Streaming Analytics, Azure Databricks, Spark, continuously processing event streams to detect performance degradation and potential security threats for proactive operational response.
•	Designed and implemented data quality validation frameworks using Talend ETL, SQL, ensuring completeness, consistency, and correctness of network configuration data prior to deployment, reducing errors and preventing service disruptions across distributed environments.
•	Developed custom integration services using REST APIs, Azure Functions, Python, connecting network monitoring platforms with ITSM systems to automate incident creation, status updates, and resolution workflows for operational support teams.
•	Created interactive executive dashboards using Power BI, Azure SQL Database, Azure Data Lake, visualizing network performance, availability, and security metrics to provide real-time insights for leadership and service-level monitoring.
•	Implemented automated capacity planning solutions using Azure Databricks, Azure Data Lake Storage, combining historical analytics and growth projections to optimize equipment utilization and guide long-term infrastructure investment decisions.
•	Standardized end-to-end data pipelines using Azure Data Factory, Talend ETL, Apache Airflow, ensuring consistent ingestion, transformation, orchestration, and delivery across network telemetry and monitoring data domains.
•	Enhanced operational reliability by implementing monitoring, alerting, and retry mechanisms in Apache Airflow, Azure Cloud, proactively identifying pipeline failures, reducing data latency, and maintaining high availability of mission-critical network analytics workflows.
•	Collaborated with network engineering and operations teams using Azure Cloud, Talend ETL, Azure Data Factory, Databricks, translating monitoring, security, and capacity requirements into scalable, compliant, and analytics-ready data solutions supporting global enterprise networks.

Environments: Azure Cloud, Azure Data Factory, Azure Databricks, Azure SQL Database, Azure Data Lake Storage, Azure Streaming Analytics, Azure Functions, Talend ETL, Apache Airflow, Python, SQL, Spark, REST APIs, Power BI, RBAC

Client: Ceva Logistics                                                                                                                                                     Mumbai, India 
Role: ETL TESTER                                                                                                                                              May 2014 - October 2015
Responsibilities:
•	Built scalable ETL pipelines using AWS Services, Informatica PowerCenter, Talend Open Studio, integrating e-commerce, inventory, and customer data to enable unified daily transaction processing across multiple retail and logistics channels with reliable ingestion and transformation.
•	Configured secure object storage using Amazon S3, managing raw, staging, and curated product catalog datasets with versioning and lifecycle policies, supporting large SKU ingestion workflows, optimizing long-term storage costs, and ensuring data durability.
•	Extracted high-volume customer and transaction data from MySQL, PostgreSQL, MongoDB, Informatica PowerCenter, preserving data relationships and integrity while enabling consistent processing of customer profiles, purchase histories, and behavioral attributes for analytics.
•	Developed optimized vendor ingestion workflows using Talend Open Studio, processing CSV and JSON marketplace feeds to deliver timely product catalog updates, improve data processing efficiency, and maintain synchronized availability across web, mobile, and warehouse platforms.
•	Implemented complex data cleansing and standardization using Informatica PowerCenter, validating product metadata, enforcing taxonomy rules, and resolving data quality issues to improve inventory accuracy, product discoverability, and consistency across multi-vendor logistics datasets.
•	Integrated order management and fulfillment systems using Talend Open Studio, automating ETL workflows to synchronize inventory levels, shipment statuses, and delivery data across distributed warehouses, providing near-real-time visibility into stock availability and order execution.
•	Designed and executed transformation and loading processes using AWS Glue, Amazon Redshift, cataloging curated sales, shipment, and inventory datasets, optimizing schema design, and enabling efficient analytical queries for category performance, delivery tracking, and trend analysis.
•	Automated ETL scheduling and dependency management using AWS Lambda, Amazon CloudWatch Events, ensuring reliable execution of time-sensitive processes such as daily order aggregation, inventory refresh cycles, and shipment reconciliation with minimal manual intervention.
•	Monitored ETL pipeline health using Amazon CloudWatch, configuring alerts for failures, performance degradation, and latency issues, enabling rapid issue resolution and maintaining high data availability for order processing, reconciliation, and downstream reporting.
•	Delivered interactive analytics using Tableau, Amazon Redshift, enabling real-time visibility into sales, inventory positions, shipment status, and customer behavior, supporting data-driven decision-making for merchandising, pricing, promotions, and logistics operations.
•	Developed incremental ETL patterns using AWS Glue, Talend Open Studio, applying CDC techniques to process large-scale transactional datasets efficiently, reducing load times while ensuring accuracy and consistency across multiple retail and warehouse systems.
•	Implemented role-based access and data security protocols using AWS IAM, Amazon S3 encryption, enforcing least-privilege access while safeguarding sensitive customer, order, and supplier data throughout ETL and analytics workflows.
•	Optimized analytical query performance using Amazon Redshift, creating distribution keys, sort keys, and columnar storage strategies to accelerate reporting and BI dashboards across inventory, sales, and delivery datasets.
•	Collaborated with cross-functional teams including merchandising, operations, and IT to define data requirements, design ETL processes using Informatica PowerCenter, Talend Open Studio, and ensure seamless integration with analytics and reporting solutions.
•	Implemented automated data validation frameworks using Python, AWS Glue, verifying source-to-target data consistency, business rule compliance, and completeness checks, improving trust in logistics, sales, and inventory analytics outputs.

Environments: AWS Services, AWS Glue, Amazon Redshift, Amazon S3, AWS Lambda, Amazon CloudWatch, Informatica PowerCenter, Talend Open Studio, Python, MySQL, PostgreSQL, MongoDB, Tableau, CDC, AWS IAM
"""
    
    print("=" * 60)
    print("TESTING CLIENT/LOCATION/ROLE FORMAT")
    print("=" * 60)
    
    work_parser = WorkExperienceParser()
    
    # Parse the entire experience section
    print("\nTESTING FULL PARSING")
    print("-" * 40)
    parsed_jobs = work_parser.parse_experience_section(text)
    
    print(f"\nNumber of parsed jobs: {len(parsed_jobs)}")
    
    # Convert to UI format
    ui_data = []
    for i, job in enumerate(parsed_jobs):
        job_dict = {
            "title": job.title,
            "company": job.company,
            "location": job.location,
            "start_date": job.start_date.isoformat() if job.start_date else None,
            "end_date": job.end_date.isoformat() if job.end_date else None,
            "is_current": job.is_current,
            "description": job.description,
            "bullets": job.bullets,
            "confidence": job.confidence
        }
        ui_data.append(job_dict)
        
        print(f"\n--- Job {i+1} ---")
        print(f"Company: {job.company}")
        print(f"Title: {job.title}")
        print(f"Location: {job.location}")
        print(f"Start Date: {job.start_date}")
        print(f"End Date: {job.end_date}")
        print(f"Is Current: {job.is_current}")
        print(f"Description length: {len(job.description) if job.description else 0}")
        print(f"Bullets count: {len(job.bullets) if job.bullets else 0}")
    
    # Show JSON output that UI would receive
    print("\n" + "=" * 60)
    print("JSON OUTPUT FOR UI:")
    print("=" * 60)
    print(json.dumps({"work_experience": ui_data}, indent=2))

if __name__ == "__main__":
    test_client_location_format()
