import sys
import os
# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'backend'))

from app.services.parser.work_experience_parser import WorkExperienceParser
import json

def test_company_date_format():
    """Test parsing of Company: Date Range (Location: City, State) format"""
    
    # Company: Date Range format resume text
    text = """
PROFESSIONAL EXPERIENCE:
UnitedHealth Group: November 2022 - Current (Location: Minnetonka, MN)   
Role: SR. BIG DATA ENGINEER
Responsibilities:
•	Built enterprise-grade healthcare ingestion pipelines in Palantir Foundry using Python and PySpark, integrating claims, eligibility, and provider datasets from AWS S3, relational sources, and APIs to support analytics, reporting, and regulatory compliance workflows.
•	Developed ontology-driven healthcare data products by modeling members, encounters, providers, and claims in Foundry Ontology, establishing authoritative datasets with lineage, provenance, and governed semantics aligned to clinical and operational reporting standards.
•	Executed multi-layer ETL pipelines through Foundry Code Workbooks and Pipelines, applying incremental and snapshot strategies with automated backfills to ensure reliable historical reconstruction during eligibility restatements and claims reprocessing cycles.
•	Improved data quality by implementing constraints, reconciliation checks, and anomaly detection within Foundry, proactively identifying claim volume variances and schema drifts before downstream actuarial and quality reporting consumers were impacted.
•	Applied advanced SQL and PySpark transformations to normalize healthcare codes, join high-cardinality datasets, and produce analytics-ready materializations optimized for performance and governed reuse across multiple care management domains.
•	Optimized runtime performance by tuning partitioning, caching, and shuffle behavior using Parquet layouts and Foundry materialization strategies, reducing pipeline runtimes while maintaining auditability and reproducibility for regulated healthcare analytics.
•	Structured RBAC and object-level permissions within Foundry, enforcing HIPAA-aligned access controls, masking sensitive attributes, and integrating enterprise identity providers to ensure compliant data access across analytics and operational teams.
•	Established operational SLAs and SLOs for critical healthcare pipelines, configuring schedules, alerts, and health checks to ensure near-continuous data availability for care quality dashboards and regulatory submissions.
•	Coordinated with data scientists to expose ontology-backed datasets to Foundry Workshop applications, enabling analytics teams to explore population health metrics while preserving governed definitions and consistent metric logic.
•	Implemented idempotent processing and checkpointing patterns in PySpark transforms, ensuring safe retries and predictable recovery during upstream feed delays or partial ingestion failures common in healthcare data exchanges.
•	Devised cost-aware pipeline designs by aligning AWS EMR-backed compute usage with workload characteristics, balancing performance needs against budget constraints without compromising data freshness or reliability.
•	Executed Git-based CI/CD workflows for Foundry repositories, introducing unit and integration tests for transformations to reduce regression risk during frequent schema and logic enhancements.
•	Led incident response efforts for data quality and availability issues, conducting root cause analyses and documenting corrective actions to prevent recurrence and strengthen platform resilience.
•	Produced detailed architecture diagrams and runbooks documenting ingestion patterns, ontology design decisions, and operational dependencies to support audit reviews and cross-team knowledge transfer.
•	Enhanced security posture by collaborating with compliance teams to implement policy tags, PII handling rules, and audit logging across Foundry datasets supporting sensitive member information.
•	Guided junior engineers through Foundry best practices, reviewing code, mentoring on PySpark optimization, and reinforcing governance-first design principles within healthcare analytics pipelines.
•	Streamlined onboarding of new healthcare domains by templatizing ingestion and enrichment workflows, enabling faster delivery of analytics-ready datasets without sacrificing data quality or governance rigor.
•	Integrated near real-time eligibility feeds using AWS Kinesis, materializing curated datasets within Foundry to support timely operational insights for care coordination teams.
•	Validated downstream metric accuracy by performing reconciliation analysis with actuarial and reporting teams, resolving discrepancies through targeted transformation adjustments and ontology refinements.
•	Strengthened platform observability by instrumenting runtime metrics and pipeline logs, enabling proactive monitoring of data latency, failures, and throughput across healthcare ingestion workflows.
•	Partnered with enterprise architects to align Foundry implementations with broader cloud and data platform strategies, ensuring scalability, security, and long-term maintainability across UnitedHealth Group analytics initiatives.
Environment: Palantir Foundry, Foundry Ontology, Foundry Pipelines, Foundry Code Workbooks, Python, PySpark, SQL, AWS S3, AWS EMR, AWS Kinesis, Parquet, Delta Lake, Git, CI/CD, RBAC, HIPAA Compliance, REST APIs, JSON, CloudWatch.

Wells Fargo: January 2020 - October 2022 (Location: San Francisco, CA) 
ROLE: SR DATA ENGINEER
Responsibilities:
•	Constructed enterprise banking data pipelines in Palantir Foundry leveraging Python and SQL, ingesting transactional, customer, and risk datasets from Azure Data Lake, relational systems, and secure APIs for analytics and regulatory reporting.
•	Designed ontology models representing accounts, transactions, customers, and products within Foundry Ontology, enabling consistent semantic definitions and governed reuse across fraud, compliance, and financial reporting use cases.
•	Executed ELT transformations using PySpark and Foundry Code Workbooks, standardizing raw banking feeds into curated layers optimized for downstream consumption by analytics and visualization teams.
•	Improved data validation processes by implementing volume checks, schema enforcement, and reconciliation logic in Foundry pipelines, reducing manual investigation cycles during month-end and quarter-close reporting.
•	Optimized query performance through advanced SQL window functions, bucketing strategies, and materialization tuning, supporting analyst-driven exploration of high-volume transaction datasets without excessive compute overhead.
•	Integrated event-driven ingestion patterns using Azure Event Hubs, materializing near real-time transaction streams into Foundry-curated datasets supporting fraud detection and operational monitoring workflows.
•	Established CI/CD pipelines using Git and Azure DevOps, enabling controlled promotion of Foundry code repositories across environments with automated testing and peer review checkpoints.
•	Applied RBAC and data segmentation controls in Foundry, ensuring sensitive financial attributes were accessible only to authorized roles in alignment with internal security and regulatory requirements.
•	Collaborated with risk and compliance teams to document data lineage, contracts, and audit artifacts, supporting regulatory examinations and internal model governance processes.
•	Tuned Spark runtime configurations on Azure Databricks-backed infrastructure to balance performance and cost during peak transaction processing windows.
•	Exposed ontology-backed datasets to internal reporting tools and Foundry Workshop applications, enabling self-service analytics while preserving governed metric definitions.
•	Led data quality incident investigations, identifying root causes related to upstream feed delays or schema changes, and implementing corrective pipeline logic to restore data accuracy.
•	Streamlined ingestion onboarding by creating reusable templates for relational and API-based banking sources, accelerating delivery timelines for new analytics initiatives.
•	Partnered with data scientists to prepare feature-ready datasets supporting credit risk and fraud modeling, ensuring consistency between analytical assumptions and production data definitions.
•	Implemented snapshot and backfill strategies for historical transaction corrections, enabling accurate restatement of financial metrics without disrupting downstream consumers.
•	Enhanced observability by integrating pipeline telemetry with Azure Monitor, supporting proactive alerting and faster incident response across critical banking data products.
•	Documented architecture decisions, operational runbooks, and recovery procedures to support on-call rotations and cross-team collaboration.
•	Mentored junior engineers on Foundry development patterns, SQL optimization, and secure data handling practices within regulated banking environments.
•	Supported cloud interoperability by coordinating selective ingestion from GCP Cloud Storage sources, validating cross-cloud data consistency within Foundry-curated datasets.
Environments: Palantir Foundry, Foundry Ontology, Foundry Code Workbooks, Python, PySpark, SQL, Azure Data Lake, Azure Databricks, Azure Event Hubs, Azure DevOps, Git, Parquet, Delta Lake, RBAC, REST APIs, JSON, GCP Cloud Storage, Azure Monitor.
Honeywell: March 2017 - December 2019 (Location: Charlotte, NC) 
ROLE: DATA ENGINEER / DATA ANALYST
Responsibilities:
•	Built foundational manufacturing data pipelines using Palantir Foundry, ingesting production, sensor, and quality datasets from GCP Cloud Storage, on-prem systems, and industrial APIs to support operational analytics initiatives.
•	Developed early ontology models capturing assets, production lines, sensors, and events within Foundry Ontology, establishing consistent semantics for manufacturing performance and reliability analytics.
•	Executed batch-oriented ETL processes using Python and SQL, transforming raw manufacturing feeds into structured, analytics-ready datasets aligned with engineering and operations reporting needs.
•	Applied PySpark transformations to cleanse, normalize, and enrich time-series sensor data, enabling downstream analysis of equipment utilization and anomaly detection.
•	Implemented partitioning and file layout strategies using Parquet to improve query performance for large historical manufacturing datasets stored in cloud environments.
•	Collaborated with operations engineers to validate data accuracy against shop-floor systems, resolving discrepancies through targeted transformation logic and source-system feedback loops.
•	Structured basic governance controls in Foundry, defining dataset ownership, access permissions, and documentation to support secure data sharing across engineering and analytics teams.
•	Introduced incremental ingestion patterns to reduce reprocessing overhead during frequent production updates, improving pipeline efficiency and operational stability.
•	Supported early adoption of Foundry Code Workbooks by documenting transformation standards and reusable patterns for manufacturing data onboarding.
•	Assisted in monitoring pipeline health through logs and basic alerts, enabling faster identification of ingestion failures during production shifts.
•	Optimized Spark jobs by tuning memory usage and partition counts on GCP Dataproc, balancing performance with cost efficiency for batch workloads.
•	Exposed curated manufacturing datasets to internal dashboards and analytics tools, supporting visibility into throughput, yield, and downtime metrics.
•	Documented data models, transformation logic, and operational assumptions to support knowledge transfer across geographically distributed engineering teams.
•	Partnered with IT and security teams to ensure cloud-based data pipelines aligned with enterprise access control and compliance requirements.
•	Participated in agile ceremonies, contributing to sprint planning, backlog refinement, and iterative delivery of data platform enhancements.
•	Gained hands-on experience with Git-based version control, supporting collaborative development and controlled promotion of Foundry pipelines.
•	Laid the groundwork for later large-scale Foundry implementations by building strong fundamentals in data modeling, pipeline reliability, and cross-team collaboration within manufacturing environments.
Environments: Palantir Foundry, Foundry Ontology, Python, PySpark, SQL, GCP Cloud Storage, GCP Dataproc, Parquet, Git, REST APIs, JSON, Time-Series Data, Batch ETL, RBAC, Linux, Agile Scrum, Monitoring Logs, Manufacturing Systems.
Equifax: February 2016 - February 2017 (Location: Atlanta, GA) 
ROLE: DATA ENGINEER / MIGRATION SPECIALIST
Responsibilities:
•	Built robust Clinical Data Integration platform using Azure Cloud, improving data integration efficiency. Reduced integration time for financial data sources by 65% while maintaining data integrity.
•	Developed and managed data ingestion pipelines using Talend ETL and Azure Data Factory (ADF) from clinical sources. Processed over 2TB of consumer credit data daily with high reliability.
•	Executed data migration projects transferring patient records from legacy systems to new EHR platforms, ensuring data accuracy. Successfully migrated 50 million consumer records with zero data loss.
•	Created and built complex workflows using Apache Airflow orchestrating ETL processes across distributed data systems. Implemented automated error handling reducing manual intervention by 85%.
•	Applied Azure SQL Database for structured data storage, optimizing query performance and reducing response times. Improved query performance by 70% through advanced indexing strategies.
•	Established Azure Data Lake Storage for scalable storage of semi-structured and unstructured clinical data. Created hierarchical data organization enabling analysts to access credit information 3x faster.
•	Connected disparate clinical data sources including laboratory results and patient demographics into unified EHR system. Integrated 12 different financial data sources creating a comprehensive 360-degree consumer view.
•	Applied data security and privacy measures complying with HIPAA regulations while working with FHIR and OMOP data models. Implemented encryption and masking protocols exceeding financial industry compliance requirements.
•	Managed migration of legacy healthcare systems to Epic following HL7 and FHIR standards while minimizing downtime. Completed critical financial system migration with only 4 hours of downtime during non-peak hours.
•	Built and refined predictive models using Azure Databricks, improving demand forecasting accuracy through machine learning techniques. Achieved 87% accuracy in credit risk scoring models, enhancing decision-making processes.
•	Implemented real-time data validation frameworks ensuring high data quality across all ingestion pipelines. Reduced data quality incidents by 78% through automated validation checks.
•	Designed and deployed a master data management solution standardizing consumer information across multiple systems. Eliminated data redundancy, reducing storage costs by 25%.
•	Created comprehensive data lineage documentation, improving data governance and regulatory compliance. Enabled audit teams to trace data origins, reducing compliance verification time by 60%.
•	Optimized batch processing jobs, reducing nightly processing window from 8 hours to 3 hours. Implemented parallel processing techniques, increasing throughput by 175%.
•	Built custom monitoring dashboards providing real-time visibility into data pipeline health and performance. Reduced mean time to resolution for pipeline failures from hours to minutes.

Environments: Azure Cloud, Talend ETL, Azure Data Factory (ADF), Apache Airflow, Azure SQL Database, Azure Data Lake Storage, HIPAA Compliance, FHIR, OMOP, HL7, Epic, Azure Databricks, Machine Learning, Data Validation, Master Data Management, Data Lineage, Batch Processing, Real-time Monitoring, Data Migration, Data Integration, Data Security, Encryption, Data Masking, Predictive Modeling, Risk Scoring, Parallel Processing, ETL Ororchestration, Error Handling, Indexing Strategies, Query Optimization, Hierarchical Data Organization, System Integration, Compliance Verification, Data Governance, Pipeline Monitoring, Semi-structured Data, Unstructured Data, Data Standardization, Distributed Systems, Automated Validation, Performance Optimization, Financial Data Processing, Consumer Credit Data, Data Redundancy Management, Audit Traceability.

Inno Minds: May 2014 - December 2015 (Location: Pune, India) 
ROLE: ETL DEVELOPER
Responsibilities:
•	Created scalable ETL pipeline using AWS services, Informatica, and Talend, combining data from relational databases, NoSQL databases, and flat files. Processed over 500GB of daily manufacturing data from 12 different source systems with high accuracy.
•	Set up AWS S3 storing raw, staging, and transformed data securely and efficiently, creating smooth ingestion workflows. Implemented bucket policies and encryption ensuring regulatory compliance while maintaining fast access to production data.
•	Used Informatica PowerCenter extracting data from MySQL, PostgreSQL, and MongoDB databases, ensuring accurate extraction. Developed custom connectors for legacy manufacturing systems reducing integration complexity by 40%.
•	Created Talend jobs processing and extracting data from CSV and JSON files, reducing data processing time. Optimized parallel processing capabilities decreasing batch window from 6 hours to under 2 hours.
•	Used Informatica performing complex data transformations for data cleansing, enrichment, and quality checks. Implemented advanced mapping logic reducing data quality issues by 75% in production reporting.
•	Set up Talend Open Studio handling simple data transformations and integrations, streamlining ETL workflows. Created reusable components library accelerating development time for new integrations by 60%.
•	Built AWS Glue jobs cataloging and loading transformed data into Redshift, optimizing data storage for analytics. Implemented partitioning strategies improving query performance by 300% for manufacturing analytics.
•	Set up automated ETL job scheduling using AWS Lambda and CloudWatch Events, improving job reliability. Created self-healing pipelines automatically retrying failed jobs reducing manual interventions by 90%.
•	Used AWS CloudWatch monitoring ETL job performance and setting up alerts for failures and anomalies. Developed custom metrics dashboard providing real-time visibility into data processing efficiency.
•	Connected Tableau to AWS Redshift creating interactive dashboards and visualizations for real-time data analysis. Delivered executive dashboards showing manufacturing KPIs, enabling data-driven decisions that improved production efficiency by 22%.

Environments: AWS S3, AWS Glue, AWS Lambda, AWS CloudWatch, AWS Redshift, Informatica PowerCenter, Talend Open Studio, Tableau, MySQL, PostgreSQL, MongoDB, ETL Pipelines, Data Transformation, Data Integration, Data Cleansing, Data Enrichment, Data Quality, Batch Processing, Parallel Processing, Data Extraction, Data Loading, Relational Databases, NoSQL Databases, CSV Processing, JSON Processing, Data Cataloging, Job Scheduling, Performance Monitoring, Data Visualization
"""
    
    print("=" * 60)
    print("TESTING COMPANY: DATE RANGE (LOCATION: CITY, STATE) FORMAT")
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
    test_company_date_format()
