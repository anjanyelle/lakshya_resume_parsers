import sys
import os
# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'backend'))

from app.services.parser.work_experience_parser import WorkExperienceParser
import json

def test_full_resume():
    """Test parsing of the full resume"""
    
    # Full resume text from user
    text = """
PROFESSIONAL EXPERIENCE:
Humana: August 2023 – Current (Location: Louisville, KY)  
Role: Sr. Big Data Engineer
Responsibilities:
•	Designed and deployed agentic retrieval workflows using Python, LangChain, and LangGraph to build context-aware agents ingesting PR metadata, commit metadata, and GitHub history, enabling automated CES scoring and quality metric computation for healthcare pipelines while ensuring HIPAA-compliant audit trails and HL7 interoperability across AWS S3, AWS Lambda, and AWS Glue.
•	Migrated legacy orchestration from Apache Airflow to Dagster across 40+ production pipelines processing healthcare claims, clinical records, and patient data on AWS ECS and AWS EKS, implementing retries, backfills, scheduling, and data quality alerts while exposing metrics, traces, and logs through Power BI and Collibra frameworks.
•	Built production-grade LLM-driven scoring systems using DSPy, integrating prompt optimization, chaining, and context packing to automate healthcare PR-level scoring and quality metrics, leveraging GPT-4, Claude, AWS Sagemaker, and MLflow for model versioning, eval set generation, and feedback loops under HIPAA-compliant governance.
•	Engineered backend services using Python, AWS Lambda, AWS EventBridge, and AWS CDK to ingest PR and commit metadata from GitHub and Jenkins, linking artifacts to compute CES metrics, quality signals, and anomalies while exposing results through RESTful APIs and Power BI dashboards under HIPAA compliance.
•	Developed data modeling frameworks using Pandas, Numpy, and MLLIB to link PRs, commits, branches, and epics for healthcare software delivery metrics, building graph-based relationships across Jira, GitHub, and AWS S3, implementing anomaly detection, role classification, and effort estimation for HIPAA-compliant reporting.
•	Orchestrated large-scale backfills and historical corrections using Dagster and AWS Glue, processing over 10 million commits and clinical record deltas with batching, caching, and DSPy-based score optimization, ensuring data quality alerts, metrics, traces, and logs captured in AWS CloudWatch and Collibra lineage tracking.
•	Implemented SonarQube integration for code-quality scoring, linking static analysis results with GitHub PR metadata and commit history to enrich CES metrics, while building Jira-integrated workflows for epic/work-type classification and automated tagging, ensuring HIPAA-compliant metadata governance across AWS ECS, AWS Lambda, and AWS S3.
•	Designed eval and feedback loops using Python, DSPy, and MLflow for LLM-driven prompt optimization, creating versioned evaluation datasets, collecting feedback from healthcare engineers via Power BI and Jira, closing loops to improve CES scoring accuracy and model explainability under HIPAA and HITECH mandates.
•	Built observability and monitoring solutions using AWS CloudWatch, AWS Lambda, and Dagster asset sensors to track metrics, traces, logs, and data quality alerts across healthcare ETL pipelines, enabling automated alerting for failures, anomaly detection, SLA breaches, and ensuring regulatory audit readiness with Collibra and ERWIN lineage tracking.
•	Developed agentic coding frameworks using LangChain, LangGraph, and DSPy to build retrieval agents that processed Git diffs, code context, and commit metadata, integrating with AWS S3, AWS Glue, and AWS Lambda to improve CES scoring, reduce LLM latency, and maintain HIPAA-compliant healthcare data processing.
•	Constructed end-to-end data pipelines using Dagster, AWS Glue, AWS S3, and AWS RDS to ingest, transform, and load healthcare claims, clinical records, and patient data from HL7 FHIR sources, implementing retries, scheduling, backfills, and data quality alerts with AWS EventBridge triggers and HIPAA-compliant logging.
•	Optimized LLM performance using batching, caching, and DSPy-based prompt optimization for healthcare code quality scoring, leveraging AWS Sagemaker and MLflow to tune prompt chaining, context packing, and eval execution workflows, balancing cost/quality tradeoffs while maintaining HIPAA-compliant model governance and HL7 interoperability.
•	Integrated GitHub, Jenkins, Jira, and SonarQube metadata into unified data models using Python, Pandas, AWS Glue, and ERWIN for entity-relationship design, building graph-based linking across PRs, commits, branches, and epics to support role/work-type classification, epic linking, anomaly detection, and HIPAA-compliant analytics exposure via Power BI.
•	Deployed AWS CDK infrastructure for pipelines and backend services on AWS EC2, AWS EKS, AWS Lambda, and AWS S3, automating provisioning, monitoring, and scaling of Dagster orchestrators, LLM inference endpoints, and AWS Glue jobs with metrics, traces, logs, and data quality alerts ensuring HIPAA and HITECH compliance.
•	Collaborated with healthcare engineering teams to define CES metrics, quality scoring models, and eval sets using Python, Dagster, AWS Lambda, AWS S3, Power BI, and Collibra, translating PR metadata ingestion, commit tracking, and anomaly detection requirements into compliant backend integration, analytics, and data modeling solutions aligned with HIPAA, HITECH, and HL7 standards.
•	Developed and deployed AI/ML pipelines using MLLIB and Numpy to predict patient readmission risk, orchestrated with Airflow for ingestion, transformation, and model retraining, ensuring HIPAA-compliant data handling, HL7 interoperability, and audit trails in alignment with HITECH Act regulations for healthcare systems.
•	Engineered AI/ML clinical decision support using LLMs and MLLIB, processing unstructured EHR data, identifying high-risk patients, and deploying inference infrastructure on AWS EC2 with encryption, role-based access, and logging to meet HIPAA and HITECH security requirements for real-time healthcare workflows.
•	Designed and optimized relational schemas using E/R Studio for patient demographics, encounters, and lab results, ensuring normalization and HL7 FHIR compliance, generating data dictionaries and impact analysis reports for HIPAA audit readiness, enabling collaboration across clinical informatics teams while maintaining secure data exchange practices.
•	Built predictive models for disease progression using MLLIB and Numpy, processing large patient datasets for feature engineering, statistical analysis, and evidence-based treatment plans, implementing de-identification, secure access policies, and documentation to meet HIPAA and HITECH standards while supporting clinical quality improvement initiatives.
•	Implemented conversational AI chatbots using LLMs and AWS EC2 to automate patient triage and scheduling, integrating with EHR systems, ensuring HIPAA privacy and HITECH compliance through secure API gateways, encryption, and access logging while enabling real-time healthcare interaction workflows across multi-site hospital networks.
•	Migrated legacy workloads to AWS EC2, configuring VPCs, security groups, and identity policies to meet HIPAA technical safeguards, encrypt patient data, enforce access controls, maintain audit logs, implement VPN tunnels, multi-factor authentication, and intrusion detection systems while ensuring HITECH breach notification and distributed healthcare compliance.
•	Standardized hospital analytics data modeling using E/R Studio, creating entity-relationship diagrams, documenting normalization rules and referential constraints to support HL7 message exchanges, HIPAA compliance audits, onboarding, and future enhancements for population health management and quality reporting across healthcare IT systems.
•	Performed numerical computation and statistical validation using Numpy on clinical trial data, supporting biostatisticians in patient outcome analysis, treatment efficacy, and adverse event reporting, ensuring HIPAA compliance, documenting methods, validating outputs, and aligning processes with FDA, HITECH, and institutional review board regulations for protected health information.
Environment:AWS Sagemaker, AWS Lambda, Dagster, Jira, Collibra, Numpy, ERWIN, Pandas, MLflow, MLLIB, AWS EC2, AWS RDS, S3, Lambda, DSPy, Jenkins, EventBridge, Git, AWS, AWS S3, LangGraph, AWS CDK, Github, Power BI, AWS EKS, langChain, Glue, Airflow, ECS, SonarQube, Python
Morgan Stanley: October 2020 – July 2023 (Location: New York, NY) 
Role: Sr Data Engineer
Responsibilities:
•	Designed and deployed production-grade data pipelines using Python and Dagster on AWS, ingesting PR metadata, commit metadata, and code quality telemetry from GitHub and Jenkins, integrating AWS Lambda, AWS S3, AWS Glue, and AWS ECS to ensure PCI-DSS-compliant financial workflows, automated retries, backfills, and observability with metrics, traces, and logs.
•	Built retrieval agents using Python and DSPy to extract historical code context, diffs, and commit histories from GitHub, implementing prompt chaining and context packing for LLM optimization, automating score correction workflows, exposing CES and quality metrics via REST APIs, and ensuring SOX and GLBA-compliant secure audit trails across financial pipelines.
•	Migrated orchestration from Apache Airflow to Dagster, enhancing PR/commit linking, branch tracking, and epic linking across Jira, GitHub, and banking systems, integrating AWS EventBridge, AWS SQS, and AWS Lambda to expose CES metrics and quality metrics to Power BI dashboards while maintaining PCI-DSS and SOX compliance.
•	Developed anomaly detection and data quality monitoring using Python, AWS Glue, and AWS CloudWatch, identifying deviations in commit metadata, PR metadata, and code quality signals from SonarQube and PMD, triggering automated alerts, implementing DSPy-based score correction, and maintaining GLBA-compliant secure audit workflows for financial code review processes.
•	Engineered AWS-native pipelines using AWS ECS, AWS Lambda, AWS S3, AWS RDS, and AWS CDK to automate backfills, retries, and scheduling for high-volume financial data ingestion, integrating GitHub webhooks and Jenkins CI/CD pipelines, storing datasets securely in AWS S3 and AWS RDS with PCI-DSS encryption and IAM access controls.
•	Implemented observability and monitoring frameworks using AWS CloudWatch, AWS X-Ray, and Python scripts, tracking metrics, traces, and logs across pipelines, triggering automated notifications through AWS SQS and Slack, ensuring PCI-DSS, SOX, and GLBA compliance while maintaining anomaly detection and continuous reliability of financial data workflows.
•	Built backend services using Python, AWS Lambda, and AWS EKS to ingest PR metadata, commit metadata, and code quality signals from GitHub, Jenkins, SonarQube, and PMD, computing CES and quality metrics, exposing results via REST APIs with JWT authentication and TLS 1.2+, supporting PCI-DSS and SOX compliance.
•	Designed and executed DSPy-based eval sets and feedback loops, collecting user feedback on scoring accuracy, retraining LLM/prompt optimization models stored in AWS S3 and AWS RDS, implementing batching and caching to optimize performance and cost while ensuring GLBA and SOX-compliant secure financial code review workflows.
•	Orchestrated data modeling and analytics workflows using Python, AWS Glue, ERWIN, and E/R Studio to design normalized schemas for PR/commit linking, branch tracking, and epic linking across Jira, GitHub, and banking systems, enabling quality metrics computation, engineering effort analysis, and PCI-DSS-compliant audit-ready reporting for executives via Power BI.
•	Integrated SonarQube and PMD results with Python backend services to compute CES and quality metrics, linking findings to PR metadata, commit metadata, and Jira epics, deploying AWS Lambda functions triggered by AWS EventBridge, storing results in AWS S3 and AWS RDS, ensuring PCI-DSS, SOX, and GLBA compliance.
•	Developed retrieval agent workflows using Python and DSPy to pull code context, diffs, and commit history from GitHub, integrating pipelines with Dagster orchestration, enabling backfills and retries for historical data, exposing CES and quality metrics via JWT-secured APIs, ensuring SOX and GLBA-compliant secure audit logging.
•	Built orchestration and reliability frameworks using Dagster and AWS ECS, implementing AWS Lambda and AWS EventBridge for event-driven ingestion of PR and commit metadata from GitHub and Jenkins, linking artifacts to Jira epics, enabling anomaly detection, data quality alerts, and PCI-DSS, SOX, and GLBA-compliant banking workflows.
•	Engineered LLM/prompt optimization pipelines using DSPy and Python, creating eval sets from historical PR and commit metadata, automating score corrections via DSPy prompt tuning, optimizing LLM call performance through batching, caching, and prompt compression, ensuring secure, auditable, and compliant workflows aligned with GLBA and SOX standards.
•	Designed data quality and observability frameworks using Python, AWS CloudWatch, AWS X-Ray, and Dagster, monitoring metrics, traces, and logs, integrating backend services with SonarQube, PMD, and GitHub, generating enriched datasets for Power BI dashboards, maintaining PCI-DSS, SOX, and GLBA compliance with secure storage in AWS S3 and AWS RDS.
•	Automated artifact linking using Python and AWS Lambda, connecting Jira, GitHub, PR metadata, and commit metadata for epic linking, work-type classification, and traceability, orchestrating pipelines in Dagster, storing datasets in AWS S3 and AWS RDS, implementing anomaly detection, and ensuring PCI-DSS, SOX, and GLBA-compliant financial code review processes.
•	Designed and deployed PCI-DSS-compliant data ingestion frameworks using AWS EKS, orchestrating containerized microservices with Airflow for ETL workflows that processed sensitive cardholder data, implementing end-to-end encryption, audit logging, RBAC, and autoscaling policies to enhance reliability and security for high-volume banking operations.
•	Implemented AWS WAF rules and security policies for AWS EC2-hosted banking applications, mitigating SQL injection, XSS, and DDoS attacks, integrating CloudWatch monitoring, geo-blocking, and rate-limiting configurations, ensuring GLBA compliance, secure customer authentication workflows, and reduced exposure to vulnerabilities across digital banking platforms.
•	Developed infrastructure-as-code templates using AWS CDK in TypeScript to provision AWS EC2, VPCs, security groups, IAM roles, and backup policies for loan origination systems, automating deployments, enforcing least-privilege access, and ensuring PCI-DSS and SOX compliance with version-controlled, repeatable provisioning pipelines.
•	Maintained version control and collaborative workflows using Git and ERWIN, managing database schema changes, branch strategies, CI/CD integration, and schema validation, ensuring audit trail consistency, peer-reviewed modifications, and GLBA-compliant governance across customer account, transaction, and mortgage data models in production banking environments.
•	Configured Airflow DAGs to automate inter-bank settlement reconciliations, orchestrating validation, anomaly detection, and report generation processes, enhancing task retries and dependencies, ensuring timely delivery of regulatory reports, SOX compliance, and SLA adherence, improving reliability for financial data processing and internal audit requirements.
•	Collaborated with data architects using E/R Studio to reverse-engineer banking databases, producing entity-relationship diagrams and data dictionaries, identifying PII and sensitive data elements, assessing downstream dependencies, and supporting GLBA and PCI-DSS protections during schema migrations and core banking modernization initiatives.
•	Provisioned and managed AWS EC2 instances for batch processing of interest calculations, fee assessments, and statement generation, implementing multi-AZ deployments, automated snapshots, CloudWatch alarms, auto-recovery, and capacity planning to ensure high availability, disaster recovery readiness, and regulatory compliance for retail banking operations.
•	Integrated ERWIN metadata repositories with Git, centralizing logical and physical data models across mortgage, credit card, and commercial lending domains, automating model exports to Git, enforcing naming conventions, version control, and change management to ensure GLBA-compliant governance and auditable production deployments in regulated financial services environments.
Environments: Lambda, Jenkins, Airflow, S3, AWS Lambda, SonarQube, Dagster, ERWIN, JWT, E/R studio, ECS, AWS EC2, AWS RDS, Power BI, AWS EKS, AWS WAF, Jira, AWS CDK, DSPy, Python, Glue, AWS S3, Git, AWS, PMD, GIthub, EventBridge, AWS SQS
Delta Airlines: December 2017 – September 2020 (Location: Atlanta, GA) 
Role: Data Engineer / Data Analyst
Responsibilities:
•	Designed and deployed production-grade data pipelines using Python and Apache Airflow to ingest commit metadata and PR metadata from GitHub, integrating AWS Lambda and AWS EventBridge for real-time processing, exposing quality metrics via REST APIs, ensuring SOC 2 audit trails and FAA/IATA compliance across aviation engineering workflows.
•	Built end-to-end data modeling frameworks using Python to link PRs and commits, tracking branch merges to main repositories, integrating AWS Glue and Dagster pipelines for historical backfills, implementing Prometheus and Grafana dashboards for anomaly detection and IOSA-compliant aviation software quality monitoring.
•	Engineered retrieval agents using Python to extract contextual metadata from GitHub, integrating SonarQube outputs into AWS S3 data lakes, computing technical debt and maintainability metrics, and exposing metrics via Power BI, ensuring observability through Prometheus and logs for continuous FAA-compliant quality improvement.
•	Orchestrated migration of legacy workflows using Dagster and Airflow on AWS ECS and AWS EKS, implementing retry logic, scheduling policies, and monitoring frameworks, triggering AWS Lambda via AWS EventBridge, integrating Grafana and AWS SNS notifications to maintain 99.9% pipeline uptime aligned with SOC 2 and IATA standards.
•	Developed analytics platforms using Python, AWS RDS, and Power BI to generate CES metrics, correlating PR and commit metadata with Jira epics, designing schemas in ERWIN and E/R Studio to support graph-like linking, enabling epic-level reporting aligned with FAA documentation and safety-critical software audit readiness.
•	Implemented backend services using Python on AWS Lambda and AWS EC2, processing thousands of daily PRs and commits, integrating Jenkins CI/CD pipelines with PMD static analysis, storing data in AWS S3, ensuring IOSA-compliant traceability, FAA version control governance, and safety-critical code quality monitoring.
•	Built observability frameworks using Prometheus, Grafana, and AWS CloudWatch, tracking Airflow DAG execution times, AWS Glue job success rates, and Lambda invocation patterns, implementing Python scripts and S3 pipelines for audit trail logging, enabling SOC 2 compliance and root-cause analysis of aviation software pipelines.
•	Orchestrated backfills of historical GitHub repository data using Dagster and AWS Glue, reconstructing branch/main tracking histories, implementing Python-based incremental processing, defining Prometheus-based data quality alerts, detecting duplicate PRs, timestamp inconsistencies, and ensuring FAA-compliant anomaly detection for safety-critical aviation releases.
•	Developed eval set creation workflows using Python, integrating Jira and GitHub APIs for feedback-driven quality validation, implementing AWS ElastiCache caching and Lambda batching optimizations, improving pipeline efficiency while maintaining observability in Grafana, supporting IATA-compliant quality scoring and engineering metrics.
•	Designed normalized data schemas for PR/commit linking and epic metadata using ERWIN and E/R Studio, deploying Python services on AWS ECS, storing data in AWS RDS and AWS S3, maintaining FAA-compliant audit trails, supporting aircraft program-specific quality metrics and work-type classification for aviation engineering teams.
•	Established observability standards using Prometheus, Grafana, and AWS CloudWatch, implementing Python scripts to detect anomalies in commit ingestion, backfill failures, or pipeline delays, configuring AWS SNS notifications to ensure rapid alerting, maintaining operational reliability standards for IATA-compliant flight operations and maintenance systems.
•	Integrated SonarQube with Airflow and AWS Glue, ingesting static analysis metrics into AWS S3, mapping code severity to FAA DAL levels, implementing Python logic to generate automated risk scoring, and visualizing defect densities, technical debt, and maintainability indices via Power BI for aviation software compliance.
•	Designed backend services using Python, AWS Lambda, AWS SQS, and AWS EventBridge, implementing asynchronous PR/commit processing, configuring AWS CDK to provision AWS ECS, AWS RDS, and AWS S3, enforcing AWS WAF security policies, and integrating Prometheus alerts for ingestion lag, anomaly detection, and aviation quality monitoring.
•	Built analytics dashboards in Power BI connected to AWS RDS and AWS S3, computing trends in code review turnaround, defect escape rates, and test coverage, aggregating data using Python and AWS Glue, maintaining FAA-compliant documentation, integrating Collibra for data catalog governance and audit readiness for safety-critical systems.
•	Established governance frameworks using Collibra, documenting PR/commit ingestion workflows, data modeling schemas, and quality metric calculations, automating Python scripts integrated with Jenkins CI/CD pipelines to enforce anomaly detection thresholds, trigger AWS SNS alerts, and maintain SOC 2-compliant aviation software engineering metrics.
•	Developed flight operations platforms using DSPy, integrating AWS SQS for asynchronous messaging between microservices handling flight updates, maintenance alerts, and crew notifications, implementing batching strategies for throughput optimization, ensuring FAA Part 121 operational integrity and IATA-compliant timely dissemination of safety-critical information.
•	Built scalable infrastructure-as-code solutions using AWS CDK to provision AWS EKS clusters for aviation safety applications, integrating Git version control, branch protection strategies, and AWS WAF with custom rules to safeguard flight planning APIs, ensuring SOC 2 Type II and IOSA compliance for sensitive operational data.
•	Implemented distributed caching architecture using AWS ElastiCache, optimizing frequently accessed aircraft maintenance records, integrating PMD static analysis in CI/CD pipelines for Java-based aviation systems, ensuring FAA  maintenance approval compliance, and improving response times for pre-flight inspections while maintaining safety-critical coding standards.
•	Configured AWS EC2 Auto Scaling groups to run flight analysis workloads, leveraging DSPy NLP frameworks to process pilot and maintenance reports, deploying multi-AZ instances for failover, supporting FAA SWIM real-time data exchange requirements, and maintaining IATA-compliant operational tracking across flight and baggage systems.
Environments: AWS CDK, Python, ERWIN, AWS EC2, EventBridge, github, SonarQube, PMD, AWS Lambda, Prometheus, AWS EKS, Dagster, Airflow, AWS, DSPy, AWS WAF, AWS S3, ECS, Glue, Jenkins, Lambda, AWS RDS, AWS Glue, S3, E/R studio, Grafana, Power BI, Git, AWS SQS, Collibra, AWS SNS, Jira
Cisco: February 2016 – November 2017 (Location: San Jose, CA) 
Role: Data Engineer / Migration Specialist
Responsibilities:
•	Built a Network Data Integration platform using Azure Cloud, improving enterprise data integration efficiency while enabling seamless data flow across global networking systems by consolidating monitoring telemetry from thousands of devices deployed in international data centers.
•	Developed scalable data ingestion pipelines using Talend ETL and Azure Data Factory, efficiently processing large volumes of network monitoring and security appliance data while ensuring reliable ingestion, transformation, and availability for downstream operational analytics.
•	Executed data migration initiatives transferring configuration data from legacy network management systems to modern SDN platforms, maintaining configuration accuracy and uninterrupted network services throughout the transition to software defined infrastructure.
•	Built complex orchestration workflows using Apache Airflow, coordinating ETL processes across distributed network monitoring systems in multiple global regions while aligning execution schedules with regional compliance and operational time zone requirements.
•	Implemented Azure SQL Database to store structured network performance metrics, optimizing data models and query execution to support rapid access to critical network health indicators for operations and engineering teams.
•	Configured Azure Data Lake Storage for scalable retention of semi structured and unstructured network traffic data, supporting long term security analysis, capacity planning, and cost efficient storage of historical traffic patterns.
•	Integrated diverse network data sources including router logs, switch telemetry, and security appliance alerts into unified monitoring solutions, enabling cross layer correlation and faster troubleshooting across complex global network environments.
•	Implemented data security and privacy controls aligned with international regulations, applying encryption, role based access controls, and data anonymization techniques while handling sensitive network configuration and traffic analysis datasets.
•	Executed migration of legacy network management platforms to modern cloud based monitoring solutions, ensuring adherence to industry standards while improving observability and reducing operational overhead for network operations teams.
•	Developed predictive capacity forecasting models using Azure Databricks, analyzing historical traffic trends to improve bandwidth planning accuracy and support proactive decision making for global network growth requirements.
•	Created real time network anomaly detection solutions using streaming analytics, enabling early identification of security threats and performance degradation by processing high volume network event streams continuously.
•	Designed and implemented data quality frameworks validating global network configuration data, ensuring consistency and correctness of configuration changes prior to deployment across distributed infrastructure environments.
•	Built custom integration APIs enabling connectivity between network management platforms and IT Service Management systems, supporting automated incident creation, updates, and resolution workflows across operational teams.
•	Developed interactive dashboards visualizing global network performance and security posture using business intelligence tools, providing leadership with real time visibility into service levels and infrastructure health.
•	Implemented automated network capacity planning solutions leveraging historical traffic analysis and growth projections, optimizing equipment utilization and supporting informed infrastructure investment decisions across global operations.

Environments: Azure Cloud, Talend ETL, Azure Data Factory (ADF), Apache Airflow, Azure SQL Database, Azure Data Lake Storage, Azure Databricks, Python, Streaming Analytics, SDN Platforms

Flipkart: August 2014 – December 2015 (Location: Bangalore, India) 
Role: ETL Developer
Responsibilities:
•	Built a scalable ETL pipeline using AWS Services, Informatica, and Talend, integrating data from e commerce platforms, inventory systems, and customer databases to create a unified data flow supporting high volume daily transaction processing across multiple online retail channels.
•	Configured Amazon S3 for secure storage of raw, staging, and transformed product catalog datasets, enabling reliable ingestion workflows for large SKU volumes while applying versioning and lifecycle policies to balance accessibility with long term storage cost optimization.
•	Utilized Informatica PowerCenter to extract data from MySQL, PostgreSQL, and MongoDB sources containing customer profiles and purchase history, ensuring accurate extraction, preserved relationships, and consistent processing of high volume customer records.
•	Developed optimized Talend jobs processing CSV and JSON based vendor feeds and marketplace listings, improving data processing efficiency and supporting timely product catalog updates across web and mobile commerce platforms.
•	Implemented complex data transformations using Informatica, performing data cleansing, validation, and standardization on product metadata to improve search accuracy and ensure consistent product taxonomy across multiple vendor sources.
•	Configured Talend Open Studio to perform data integrations between order management and fulfillment systems, streamlining ETL workflows and synchronizing inventory levels across distributed warehouse and fulfillment center operations.
•	Designed AWS Glue jobs to catalog, transform, and load curated sales and inventory data into Amazon Redshift, optimizing storage layouts and enabling efficient analytical queries supporting sales performance and category level insights.
•	Automated ETL job scheduling using AWS Lambda and Amazon CloudWatch Events, improving reliability of time sensitive processes such as daily sales reporting and inventory refreshes through managed execution and dependency handling.
•	Monitored ETL pipeline performance using Amazon CloudWatch, configuring alerts for failures and latency issues in critical data flows supporting order processing and financial reconciliation activities.
•	Connected Tableau to Amazon Redshift to deliver interactive dashboards for real time analysis of sales trends, inventory positions, and customer behavior, enabling merchandising teams to make informed decisions on product placement and promotions  strategies.
Environments: AWS (S3, Glue, Lambda, CloudWatch, Redshift), Informatica PowerCenter, Talend, Talend Open Studio, MySQL, PostgreSQL, MongoDB, CSV/JSON files, Tableau
"""
    
    print("=" * 60)
    print("TESTING FULL RESUME PARSING")
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
    test_full_resume()
