#!/usr/bin/env python3
"""
Test Sushmitha Dantuluri's comprehensive resume
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.enhanced_pipeline_final import EnhancedResumePipelineFinal

def test_sushmitha_resume():
    """Test parsing of Sushmitha's comprehensive resume"""
    
    sushmitha_resume = """SUSHMITHA DANTULURI
Business Analyst
Mail : yourname@gmail.com||Ph: 0123456789||Linkedin:

Professional Summary:
•	Senior Data Analyst with 10+ years of experience delivering insights across multiple domains. Expert in end-to-end analytics, advanced SQL, Python, BI, big data, and data engineering. Proficient across AWS, Azure, and GCP, leveraging modern tools to drive scalable, business-focused decisions and enterprise reporting, governance, automation.
•	Designed enterprise ETL workflows extracting data from SQL Server, Oracle DB, DB2, and Teradata using Informatica, Talend, and SSIS, transforming with Python and Dbt, then loading into Snowflake and AWS Redshift for analytical consumption.
•	Developed real-time streaming architectures capturing transactional events through Apache Kafka, AWS MSK, and Azure Event Hubs, processing messages via Apache Beam and PySpark pipelines, persisting results into DynamoDB, Cosmos DB, and BigQuery.
•	Constructed scalable data lakehouse platforms on AWS S3 and Azure Data Lake Storage integrating Delta Lake, Apache Iceberg, and Apache Hudi, implementing medallion architectures with Parquet formats orchestrated through Apache Airflow and Dagster.
•	Implemented comprehensive data quality validation frameworks deploying Monte Carlo, Great Expectations, Soda, and Databand to monitor accuracy across Snowflake, AWS Redshift, Teradata, Vertica, and PostgreSQL ensuring reliable analytics outputs consistently.
•	Orchestrated distributed data processing leveraging Databricks Lakehouse with Delta Lake, executing Spark SQL and PySpark notebooks utilizing Pandas and Python for exploratory analysis on petabyte-scale datasets stored in cloud storage environments.
•	Engineered machine learning solutions building predictive models with Python, XGBoost, Scikit-learn, TensorFlow, and R on Amazon SageMaker and Azure Machine Learning, forecasting customer behavior, churn patterns, and demand trends accurately.
•	Established robust data governance implementing Collibra, Azure Purview, DataHub, Alation, and Apache Atlas for metadata management, lineage tracking, and access policies across AWS Glue Catalog, Snowflake, and cloud databases ensuring compliance.
•	Automated cloud migration workflows using AWS DMS, Azure Data Factory, and GCP Cloud Dataflow to transfer data from legacy DB2, Oracle DB, and Teradata systems into AWS Aurora, Azure SQL Database, and BigQuery warehouses.
•	Crafted interactive business intelligence dashboards using Tableau, Power BI, Looker, AWS QuickSight, and MicroStrategy, querying Snowflake, AWS Athena, BigQuery, and Vertica through optimized SQL for stakeholder decision-making and reporting.
•	Facilitated workflow orchestration configuring Apache Airflow, Control-M, Dagster, Prefect, and Oozie to schedule PySpark jobs, Dbt transformations, and AWS Glue pipelines, monitoring execution health and troubleshooting failures proactively.
•	Optimized analytical query performance across Snowflake, AWS Redshift, Trino, Presto, Dremio, and Azure Synapse Analytics implementing partitioning strategies and indexing with SQL and Spark SQL, reducing latency from hours to seconds.
•	Built containerized analytics applications deploying Docker and Kubernetes on AWS, Azure, and GCP, executing microservices running Python scripts, Dbt models, and statistical analysis for scalable predictive analytics and operational reporting.
•	Integrated diverse data sources using RESTful APIs, GraphQL, XML, JSON, and CSV formats, extracting from external vendors via AWS AppFlow, Azure Logic Apps, and custom Python connectors into DynamoDB, Cosmos DB, and MongoDB.
•	Administered CI/CD pipelines utilizing Jenkins, GitHub Actions, Git, Bitbucket, and GitLab for version control of Python scripts, Dbt models, and PySpark jobs, automating testing before production deployment with comprehensive documentation.
•	Performed advanced statistical analysis conducting hypothesis testing and regression modeling using Python, R, Pandas, Numpy, Scipy, Scikit-learn, and MATLAB on customer behavioral data generating insights that informed strategic business initiatives.
•	Configured data ingestion pipelines connecting Fivetran, Stitch, Segment, and RudderStack to synchronize operational data from MySQL, PostgreSQL, HBase, and transactional systems into AWS S3, Azure Data Lake Storage, and Google Cloud Storage.
•	Managed cloud infrastructure deploying AWS Lambda, Azure Functions, and GCP Cloud Functions for serverless data processing, triggering AWS Glue workflows, Azure Synapse Pipelines, and Cloud Dataflow jobs based on event-driven architectures.
•	Designed dimensional data models in Snowflake, AWS Redshift, and Azure Synapse Analytics using SQL and Dbt, implementing star schemas optimized for OLAP queries executed through Tableau, Power BI, and analytical reporting tools.
•	Established data archival strategies implementing lifecycle policies on AWS S3 Glacier and Azure Archive Storage, automating cold data migration from AWS Aurora, PostgreSQL, Cassandra, and warehouses using Python and serverless functions.
•	Cultivated analytics leadership delivering executive presentations using Tableau, Power BI, Plotly, Seaborn, and Matplotlib visualizations, translating machine learning insights from XGBoost and TensorFlow models into actionable business recommendations driving profitability growth.
•	Processed high-volume streaming data utilizing Apache Kafka, AWS MSK, Azure Event Hubs, and GCP Pub/Sub, transforming events through Apache Beam, PySpark, and Java microservices into BigQuery, Amazon Timestream, and Azure Data Explorer.
•	Implemented search and analytics capabilities deploying Elasticsearch, Amazon OpenSearch, and Redis to index product catalogs and customer data, enabling real-time searches with sub-second latency integrated into Tableau and Looker dashboards.
•	Coordinated cross-functional teams following Agile, Scrum, and Kanban methodologies through Jira, Confluence, Trello, Notion, and Slack, facilitating sprint planning, stakeholder management, and analytics delivery ensuring alignment with business objectives.
•	Automated repetitive analytical tasks scripting VBA, BASH, and PowerShell macros integrated with Excel, Power Pivot, Power Query, and Google Sheets, connecting to Snowflake, BigQuery, and AWS Redshift reducing manual effort significantly.
•	Enhanced data observability monitoring AWS Glue pipelines, Dbt transformations, Azure Data Factory workflows, and Cloud Dataflow jobs using Monte Carlo, Great Expectations, and Databand, alerting via Jira and Confluence for proactive resolution.

Certifications
AWS certificatication - 2024-2027

Technical Skills:
Databases & Data Stores : Teradata, Vertica, MySQL, PostgreSQL, Oracle Database, DB2, SQL Server, Greenplum, Hive, MongoDB, Cassandra, Azure Cosmos DB, Couchbase, Amazon DynamoDB, Amazon Aurora, Azure SQL Database, Snowflake, Google BigQuery, Amazon Timestream, Cloud Bigtable, Redis, HBase
Cloud Environment : AWS: Amazon S3, S3 Glacier, AWS Glue, Glue Data Catalog, Amazon EMR, Amazon Redshift, Amazon Athena, AWS Lambda, Amazon EC2, Amazon MSK, AWS Lake Formation, AWS DataZone, AWS DMS, AWS AppFlow, Amazon OpenSearch, OpenSearch Dashboards, Amazon SageMaker, SageMaker Data Wrangler, Amazon Forecast, Amazon Timestream, Amazon CloudWatch Azure: Azure Data Factory, Azure Databricks, Azure Synapse Analytics, Synapse Pipelines, Azure SQL, Azure Data Lake Storage, Blob Storage, Event Hubs, Azure Functions, Logic Apps, HDInsight, Azure Cosmos DB, Azure Machine Learning, Azure Purview, Azure Data Explorer, Cognitive Services, Archive Storage GCP: Cloud Storage, BigQuery, Cloud Dataflow, Cloud Functions, Pub/Sub, Cloud Bigtable, Dataproc, Google Kubernetes Engine (GKE)
Data Warehousing & BI : Snowflake, Amazon Redshift, Azure Synapse Analytics, Google BigQuery, Vertica, Teradata, Dimensional Modeling, Star Schema, Snowflake Schema, Facts and Dimensions, OLAP Cubes, SSIS, MicroStrategy, SAP BusinessObjects
Big Data Ecosystem : Apache Spark, PySpark, Spark SQL, Apache Kafka, AWS MSK, Apache Beam, Hive, HDFS, Apache Airflow, Control-M, Apache NiFi, Oozie, Dagster, Prefect, Dremio, Trino, Presto, Hadoop, YARN, Sqoop, Flume, MapReduce, ZooKeeper
Reporting & Visualization Tools : Tableau, Power BI, Power BI Service, AWS QuickSight, Looker, Metabase, QlikView, IBM Cognos, MicroStrategy, SAP BusinessObjects, Microsoft Excel, Power Pivot, Plotly, Seaborn, Matplotlib
ETL / ELT & Data Integration : AWS Glue, Azure Data Factory, Azure Synapse Pipelines, Informatica PowerCenter, Informatica Data Quality, Talend, Talend Data Quality, SSIS, Semarchy, Stitch, Fivetran, AWS DMS, AWS AppFlow, Cloud Dataflow, Apache Pig
Data Lake & Lakehouse Technologies : Delta Lake, Databricks Lakehouse, Apache Iceberg, Apache Hudi, Parquet, Avro, Medallion Architecture (Bronze, Silver, Gold), AWS Lake Formation, Azure Data Lake Storage
Data Quality, Governance & Observability : Monte Carlo, Great Expectations, Databand, Soda, Collibra, DataHub, Apache Atlas, Alation, AWS DataZone, Azure Purview, Data Catalogs, Metadata Management, Data Lineage, Access Policies
Python Libraries & Machine Learning : NumPy, Pandas, Scikit-learn, SciPy, StatsModels, Prophet, XGBoost, TensorFlow, Regression, Classification, A/B Testing, Hypothesis Testing, Time Series Forecasting, Gradient Boosting, Random Forest, Logistic Regression, Decision Trees
Streaming & Event-Driven Systems : Apache Kafka, AWS MSK, Azure Event Hubs, GCP Pub/Sub, Spark Streaming, AWS Lambda, Azure Functions, Cloud Functions, RudderStack, Segment, Amplitude, Mixpanel
Containerization & CI/CD : Docker, Kubernetes, Jenkins, GitHub Actions, GitLab CI, Bitbucket Pipelines
Programming Languages & Scripting : SQL, Advanced SQL, Python, PySpark, Scala, Java, R, Julia, BASH, PowerShell, VBA, Unix Shell, T-SQL
APIs & Data Formats: RESTful APIs, GraphQL, XML, JSON, CSV, Parquet, Avro
SDLC & Methodologies: Agile, Scrum, Kanban, SDLC, Waterfall, CI/CD, DevOps
Project & Collaboration Tools: Jira, Confluence, Git, GitHub, GitLab, Bitbucket, SharePoint, Notion, Trello, Slack
Stakeholder & Analytics Leadership: Stakeholder Management, Executive Reporting, Analytics Leadership, Data-Driven Decision Making, Business Requirement Translation

Professional Experience:
CLIENT: Home Depot      						              Location: Atlanta, GA
ROLE:  Senior Data Analyst                                                                                         June 2023 – Current
Responsibilities:
•	Architected scalable ETL pipelines utilizing AWS Glue and Dbt to extract retail transaction data from AWS Aurora and DynamoDB, transforming datasets through PySpark and Python, loading into AWS Redshift and Snowflake for enterprise analytics.
•	Pioneered lakehouse architecture on AWS S3 integrating Delta Lake and Databricks Lakehouse, implementing medallion data layers with Parquet file formats, orchestrating workflows through Apache Airflow and Control-M for seamless data processing operations.
•	Engineered real-time streaming solutions leveraging AWS MSK and AWS Lambda to capture e-commerce events, processing messages through PySpark and Spark SQL pipelines, persisting results into DynamoDB and Amazon Timestream for operational dashboards.
•	Spearheaded data quality frameworks implementing Monte Carlo and Dbt tests to validate product inventory, customer transactions, and pricing data across AWS Redshift, Snowflake, and AWS Aurora ensuring ninety-seven percent accuracy consistently.
•	Championed advanced analytics initiatives building machine learning models using Python, XGBoost, Scikit-learn, and TensorFlow on Amazon SageMaker, predicting customer purchase behavior, demand forecasting, and inventory optimization patterns accurately across retail categories.
•	Orchestrated data governance implementation utilizing AWS DataZone, DataHub, and Collibra for metadata management, data lineage tracking, and access policies across AWS S3, AWS Redshift, Snowflake, and AWS Glue Catalog ensuring compliance.
•	Designed interactive Tableau and AWS QuickSight dashboards integrating data from AWS Athena and Snowflake using SQL queries, visualizing retail KPIs including sales trends, inventory turnover, and customer segmentation metrics for stakeholder management.
•	Leveraged Databricks Lakehouse with Delta Lake to build unified analytics platform, executing distributed Spark SQL and PySpark notebooks utilizing Pandas for exploratory analysis on petabyte-scale retail datasets stored in AWS S3.
•	Facilitated seamless data migration using AWS DMS and AWS AppFlow to synchronize product catalogs from legacy systems into AWS Aurora and DynamoDB, subsequently processing through AWS Glue transformations with Dbt models.
•	Automated CI/CD pipelines implementing Jenkins, Docker, and Kubernetes for containerized analytics applications, deploying Python scripts, Dbt models, and PySpark jobs to production environments with version control via Jira and Confluence documentation.
•	Conducted sophisticated time-series forecasting using Python, Prophet, and Amazon Forecast to predict seasonal demand patterns, analyzing retail sales data from AWS Redshift and Snowflake, improving inventory planning accuracy by sixty-three percent.
•	Established data archival strategies implementing S3 Glacier policies for regulatory compliance, automating cold data migration from AWS Aurora and AWS Redshift using AWS Lambda functions based on retention requirements and access patterns.
•	Optimized query performance across Trino, AWS Athena, and Snowflake by implementing partitioning strategies using Advanced SQL and Spark SQL, reducing analytical query latency from hours to seconds for critical retail operations dashboards.
•	Pioneered customer analytics solutions integrating RudderStack for event tracking, streaming clickstream data through AWS MSK into Amazon OpenSearch, enabling real-time behavioral analysis with AWS OpenSearch Dashboards and Python-based Plotly visualizations.
•	Developed comprehensive A/B testing frameworks using Python, Scikit-learn, and Pandas to evaluate promotional campaigns, analyzing experiment results from DynamoDB and AWS Redshift, driving data-driven marketing decisions that increased conversion rates.
•	Leveraged AWS Lake Formation to implement fine-grained access controls and data security policies across AWS S3 data lakes, managing permissions for AWS Glue jobs, AWS Athena queries, and Snowflake integrations compliantly.
•	Constructed RESTful APIs using Python and AWS Lambda to expose retail analytics data, parsing XML responses, integrating with downstream systems, and triggering AWS Glue workflows for automated data processing and transformation pipelines.
•	Administered workflow orchestration through Apache Airflow and Control-M, monitoring PySpark jobs on Databricks, troubleshooting AWS Glue failures, coordinating with infrastructure teams via Jira and Confluence for production incident management and resolution.
•	Implemented advanced search capabilities utilizing Elasticsearch and Amazon OpenSearch to index product catalogs, enabling real-time inventory searches with sub-second latency, integrating results into Tableau dashboards for merchandising teams' operational efficiency.
•	Cultivated machine learning operations leveraging Amazon SageMaker and SageMaker Data Wrangler for feature engineering, training XGBoost and TensorFlow models on retail datasets, deploying endpoints serving real-time predictions via AWS Lambda functions.
•	Designed dimensional data models in Snowflake and AWS Redshift using Advanced SQL and Dbt, implementing star schemas optimized for OLAP queries executed through AWS Athena, Trino, and Tableau for business intelligence reporting.
•	Streamlined data preparation workflows utilizing SageMaker Data Wrangler and Python Pandas to cleanse retail datasets, applying transformations, handling missing values, exporting processed Parquet files to AWS S3 for downstream consumption by analytics teams.
•	Enhanced analytics leadership through stakeholder management, delivering executive presentations using Tableau visualizations, Plotly charts, AWS QuickSight dashboards, and XGBoost model insights, driving strategic retail initiatives that increased profitability by forty-two percent.
•	Pioneered event-driven architectures using AWS Lambda and AWS AppFlow to automate data synchronization from external vendors into DynamoDB and AWS Aurora, triggering AWS Glue ETL jobs processing data into Delta Lake structures.
•	Leveraged Power Pivot and Excel for ad-hoc financial analysis, connecting to AWS Redshift and Snowflake data sources using SQL queries, creating pivot tables and dynamic reports for merchandising teams' weekly performance reviews.
•	Established robust monitoring solutions implementing Monte Carlo for data observability, tracking data quality metrics across AWS Glue pipelines, Dbt transformations, and Snowflake tables, alerting via Confluence and Jira for proactive issue resolution.
•	Optimized cloud costs by analyzing AWS S3 storage patterns using Python and Pandas, migrating infrequently accessed datasets to S3 Glacier, implementing lifecycle policies through AWS Lake Formation, reducing infrastructure expenses by thirty-nine percent.

Environment: SQL, Advanced SQL, Python, Power Pivot, Montecarlo, Dbt,  AWS GLUE , Elasticsearch, XGBOOST, Python, Dynamo DB, Spark SQL, Pyspark, Apache Airflow , DBT, Tableau, EXCEL, Pandas, AWS Athena, Jenkins , Docker, Kubernetes, Control-M,XML, REST APIs, AWS Redshift, Plotly, Prophet , Scikit-learn, A/B Testing, Stakeholder Management & Analytics Leadership ,Jira , Confluence, AWS Glue Catalog, AWS S3,S3 Glacier, AWS Lake Formation, AWS Datazone , AWS Lambda , AWS QuickSight , Snowflake , Amazon Timestream, AWS Aurora, Amazon OpenSearch, AWS DMS , AWS APPFLOW ,AWS MSK, AWS OpenSearch Dashboards , Amazon SageMaker, SageMaker Data Wrangler, Amazon Forecast, DataHub, Collibra, Rudder Stack, Trino , Parquet, Databricks Lakehouse, Delta Lake, TensorFlow.

CLIENT: Huntington       						              Location: Columbus, OH
ROLE: Principal Data Analyst                                                                                   August 2020– May 2023
Responsibilities:
•	Architected enterprise-scale ETL pipelines leveraging Azure Data Factory and Azure Synapse Pipelines to extract transactional banking data from DB2 and Oracle DB, transforming datasets using Python and Dbt before loading into Snowflake and Delta Lake.
•	Pioneered data lakehouse implementation on Azure Data Lake Storage integrating Apache Iceberg and Delta Lake, enabling ACID transactions for financial datasets while orchestrating incremental loads through Dagster and Prefect workflow orchestration frameworks seamlessly.
•	Engineered real-time streaming architectures utilizing Azure Event Hubs and Azure Functions to capture banking transactions, processing events through Apache Beam pipelines written in Python, and persisting results into Azure Synapse Analytics and Cosmos DB.
•	Spearheaded data quality initiatives implementing Great Expectations and Databand frameworks to validate customer account information, loan portfolios, and transaction records across Snowflake, Azure SQL Database, and Cassandra ensuring ninety-eight percent accuracy.
•	Championed analytics modernization by migrating legacy OLAP cubes from Oracle DB to Azure Synapse Analytics using Azure Data Factory, optimizing SQL queries and dimensional models, reducing report generation time by seventy-two percent consistently.
•	Developed sophisticated machine learning models using Python, Scikit-learn, Pandas, and Scipy on Azure Machine Learning platform, conducting hypothesis testing and regression analysis to predict customer churn, loan defaults, and credit risk patterns effectively.
•	Orchestrated cross-functional Agile teams utilizing Kanban methodology through Jira and Confluence, facilitating sprint planning, stakeholder management, and analytics leadership while coordinating releases via Git, Bitbucket, and GitHub Actions for continuous integration deployment.
•	Designed interactive Power BI dashboards and reports utilizing Power Query for data transformation, publishing to Power BI Service, visualizing banking KPIs including deposit trends, loan performance, and customer segmentation metrics for executive decision-making.
•	Leveraged Azure Databricks with Delta Lake to build unified analytics platform, executing distributed SQL queries and Python notebooks utilizing Pandas and Seaborn for exploratory data analysis on petabyte-scale financial datasets stored across multiple zones.
•	Established comprehensive data governance framework implementing Azure Purview, Collibra, and Alation for metadata management, data lineage tracking, and policy enforcement across Azure SQL Database, Snowflake, Cosmos DB, and Oracle DB environments compliantly.
•	Automated data ingestion workflows configuring Stitch connectors and custom Python scripts to synchronize banking data from legacy DB2 systems into Azure Data Lake Storage, subsequently processing files through Azure HDInsight and Dbt transformations.
•	Constructed containerized analytics applications using Docker and Kubernetes on Azure, deploying microservices that executed Python-based statistical models with Scipy and Pandas, enabling scalable predictive analytics for credit scoring and fraud detection.
•	Optimized query performance across Dremio, Snowflake, and Azure Synapse Analytics by implementing strategic data partitioning and indexing using SQL, reducing analytical query latency from minutes to seconds for critical banking operations dashboards.
•	Facilitated seamless data integration using GraphQL and XML APIs, extracting banking data from external vendors, transforming through Azure Logic Apps and Azure Functions, loading into Cassandra and Cosmos DB for real-time customer analytics.
•	Administered workflow orchestration using Oozie and Dagster on Azure HDInsight clusters, monitoring Apache Hive jobs, troubleshooting pipeline failures proactively, coordinating with infrastructure teams through Confluence and Jira for production incident management.
•	Implemented advanced analytics solutions leveraging Azure Cognitive Services for document intelligence, processing loan applications and KYC documents, integrating outputs with Azure Data Factory pipelines feeding enriched data into Azure Synapse and Snowflake warehouses.
•	Pioneered medallion architecture on Azure Data Lake Storage organizing bronze, silver, and gold layers using Delta Lake and Apache Iceberg, implementing Dbt transformations with Python to ensure data quality progression through Great Expectations validation.
•	Conducted sophisticated statistical analysis using Python, Pandas, Scipy, and hypothesis testing methodologies on customer behavioral data stored in Azure SQL Database and Snowflake, generating insights that improved marketing campaign effectiveness by fifty-four percent.
•	Leveraged Amplitude for product analytics integration, capturing user interaction events from banking applications, streaming data through Azure Event Hubs into Azure Data Explorer, enabling real-time customer journey analysis with SQL and Power BI visualizations.
•	Streamlined data archival strategies implementing Azure Archive Storage policies for regulatory compliance, automating cold data migration from Azure SQL Database and Cosmos DB using Azure Logic Apps and Azure Functions based on retention requirements.
•	Established robust CI/CD pipelines utilizing GitHub Actions, Bitbucket, and Git for version control of Dbt models, Python scripts, and Power BI reports, automating testing with Great Expectations before deploying to Azure Databricks production environments.
•	Designed dimensional data models in Snowflake and Azure Synapse Analytics using SQL and Dbt, implementing slowly changing dimensions for customer profiles, optimizing star schemas for OLAP queries executed through Dremio and Power BI Service.
•	Cultivated data-driven culture through stakeholder management and analytics leadership, delivering executive presentations using Power BI dashboards, Seaborn visualizations, and Scikit-learn model insights, driving strategic banking initiatives that increased revenue by thirty-eight percent.
Environment: SQL, Python, Azure,ETL, Dbt, Apache Iceberg, Apache beam, Azure Databricks, Great Expectations ,Stitch,DB2,Pandas , Scipy , Seaborn , Git , Bitbucket, Scikit-learn ,OLAP ,Oracle DB, Snowflake ,Azure Synapse ,Cassandra ,Cosmos DB ,Apache Hive, Azure Data Factory , Power BI, Collibra, Github Actions ,Jira, Confluence, Oozie, Dremio, Amplitude, Azure Data Lake Storage, Azure Archive Storage, Azure SQL Database, Databand, Azure Data Explorer, Azure Logic Apps, Azure Synapse Pipelines, Azure Functions, Azure HDInsight, Agile , kanban, Dagster, Power Query, Azure Purview, Perfect, Azure Event Hubs, hypothesis testing, POWER BI Service, Stakeholder Management & Analytics Leadership, Azure Cognitive services, Azure Machine Learning ,Docker, Kubernetes , GraphQL, XML, Alation, Delta Lake.

CLIENT: Walgreens      					        	             Location: Deerfield, IL
ROLE: Senior Data Analyst                                                                                     October 2017 – July 2020
Responsibilities:
•	Architected comprehensive ETL pipelines using Informatica and Talend to extract healthcare data from Teradata and Vertica databases, transforming complex datasets through Python and SQL scripts before loading into BigQuery for downstream analytics.
•	Engineered automated data quality frameworks leveraging Informatica Data Quality and Soda to validate patient records, prescription data, and inventory metrics ensuring ninety-nine percent accuracy across PostgreSQL, Vertica, and Teradata enterprise databases consistently.
•	Spearheaded migration of legacy SSIS packages to GCP Cloud Dataflow utilizing Apache Beam and Python, reducing data processing time by sixty-five percent while orchestrating workflows through Apache Airflow and Control-M scheduling tools.
•	Developed real-time data streaming solutions implementing GCP Pub/Sub with Cloud Functions to capture pharmacy transaction events, processing Avro-formatted messages through Apache Beam pipelines into BigQuery and Cloud Bigtable for operational reporting.
•	Orchestrated cross-functional Agile teams following Scrum methodologies using Trello, Notion, and Slack for sprint planning, ensuring timely delivery of analytics solutions while collaborating with stakeholders to refine healthcare business requirements continuously.
•	Designed scalable data lake architecture on Google Cloud Storage integrating Apache Hudi for incremental data management, enabling efficient upserts of healthcare records while maintaining ACID compliance across petabyte-scale datasets using Python APIs.
•	Crafted interactive dashboards in Looker and Metabase visualizing pharmacy performance metrics, patient demographics, and prescription trends by querying BigQuery datasets through optimized SQL, empowering executive decision-making with actionable healthcare insights daily.
•	Championed containerized analytics applications using Docker and Kubernetes on GCP, deploying microservices that executed Python-based regression models and statistical analysis using Numpy and Matplotlib for predictive healthcare forecasting and trend analysis.
•	Streamlined data ingestion workflows by configuring Fivetran connectors and building custom RESTful APIs to synchronize data from operational systems into Google Cloud Storage, subsequently processing files through Cloud Dataflow and loading into Vertica warehouses.
•	Leveraged Scala and Apache Beam to construct parallel processing pipelines on Cloud Dataflow, transforming healthcare claims data from multiple sources, applying business logic, and persisting results into BigQuery tables for compliance reporting requirements.
•	Conducted advanced statistical analysis using Python, Numpy, and regression techniques on patient outcome data stored in PostgreSQL and Teradata, generating predictive models that improved pharmacy inventory forecasting accuracy by forty-three percent.
•	Established comprehensive data governance framework utilizing Apache Atlas for metadata management and lineage tracking across Teradata, Vertica, BigQuery, and PostgreSQL databases, ensuring regulatory compliance with healthcare data privacy standards like HIPAA.
•	Automated repetitive analytical tasks through VBA macros and PowerShell scripts integrated with Excel and Google Sheets, enabling business users to generate customized reports from BigQuery datasets, reducing manual effort by seventy percent monthly.
•	Implemented event-driven architectures using GCP Pub/Sub, Cloud Functions, and Cloud Dataflow to process real-time prescription fills, triggering downstream analytics workflows and updating dashboards in Looker while maintaining sub-second latency requirements consistently.
•	Optimized query performance across Presto, Vertica, and BigQuery environments by redesigning data models and implementing partitioning strategies using SQL, reducing report generation time from hours to minutes for critical healthcare operational dashboards.
•	Facilitated seamless data integration using Segment CDP, Apache Pig for data transformation, Redis for caching frequently accessed healthcare metrics, and SSIS for legacy system connectivity, creating unified analytical datasets stored in Cloud Bigtable.
•	Administered ETL workflows through Control-M and Apache Airflow, monitoring data pipeline health, resolving failures proactively, and maintaining comprehensive documentation in Notion while coordinating with infrastructure teams through Slack channels for production support.
Environment: SQL, Python, VBA, Scala, Power Shell ,SSIS ,Teradata, EXCEL , GCP, Google Cloud Storage, BigQuery, Cloud Bigtable, Cloud Dataflow ,Vertica, Apache Beam , ETL, Cloud Functions ,PUB/SUB ,Looker ,Google Worksheeet, Soda ,Excel, Apache Hudi, Informatica ,Apache airflow, Apache Atlas ,Docker ,Kubernetes, Slack , Notion, Trello ,Slack, Segment, Control-M, Avro, Presto, Restful APIs, Informatica data quality ,Agile, scrum, Numpy , Regression, Pig, Redis, Talend, Matplotlib, Metabase, Fivetran, Vertica, PostgreSQL.

CLIENT: T-Mobile      					                                    Location: Bellevue, WA
ROLE: Data Analyst                                                                                 December 2015 – September 2017
Responsibilities:
•	Architected robust ETL pipelines leveraging SSIS and Talend Data Quality to extract subscriber data from SQL Server and PostgreSQL, transforming records with BASH automation, then loading into Vertica for analytics consumption by business stakeholders.
•	Engineered predictive churn models using R and Statistics packages, analyzing customer lifecycle patterns from HBase datasets, creating visualizations in Tableau that informed retention strategies, while documenting methodologies comprehensively within Alation data catalog for team reference.
•	Spearheaded real-time streaming architecture implementing Apache Kafka and Apache Nifi to capture network events, processing JSON payloads through Java microservices, storing enriched data in AWS S3 for downstream consumption by analytical reporting platforms seamlessly.
•	Orchestrated end-to-end data workflows extracting telecommunications metrics via SSIS from SQL Server, cleansing through Talend Data Quality on Hadoop clusters, transforming with Apache Spark jobs, loading into AWS RedShift, and visualizing insights through MicroStrategy dashboards for executive leadership.
•	Championed cloud migration initiatives transferring legacy data from on-premise Hadoop and HBase clusters to AWS EMR using AWS Data Pipeline, executing validation queries in Presto and SQL, ensuring data integrity throughout migration using rigorous Statistics-based testing methodologies.
•	Cultivated agile delivery practices facilitating sprint ceremonies documented in Jira and Confluence, collaborating with cross-functional teams using Gitlab for version control, deploying ETL solutions through Jenkins CI/CD pipelines while maintaining stakeholder alignment through regular status communications.
•	Pioneered self-service analytics capabilities developing Alteryx workflows that enabled business users to blend Excel spreadsheets with PostgreSQL databases, reducing turnaround time for ad-hoc requests, while maintaining governance standards through comprehensive documentation in Alation.
•	Designed RESTful APIs using Java to expose telecommunications datasets stored in Couchbase and AWS RedShift, returning JSON responses consumed by mobile applications, implementing AWS Lambda functions for serverless data validation and enrichment across distributed systems.
•	Mastered complex SQL optimization techniques across Vertica, Presto, and SQL Server databases, accelerating SAP BO report performance from hours to minutes, utilizing advanced indexing strategies while analyzing execution plans through systematic Statistics-driven performance tuning approaches.
•	Streamlined operational workflows implementing Autosys job scheduling for nightly ETL processes, orchestrating BASH scripts that triggered Apache Spark jobs on AWS EMR clusters, monitored through Docker containerized dashboards, ensuring timely data refreshes for Tableau and MicroStrategy consumers.
•	Fostered stakeholder management excellence translating business requirements into technical specifications, presenting data-driven insights through polished Tableau visualizations and Excel reports, integrating Mixpanel product analytics while conducting Agile retrospectives documented thoroughly in Confluence for continuous improvement.
•	Advanced data quality frameworks deploying Talend Data Quality rules across PostgreSQL and Vertica environments, scripting validation checks in R and Julia, tracking remediation efforts in Jira, collaborating via Github repositories while leveraging AWS S3 for archival storage.
Environment: SQL, R,SSIS , Java, BASH, Excel, Julia, PostgreSQL, Vertica ,Apache spark, Talend data quality, SQL Server , Tableau, ETL , Apache kafka, Apache Nifi, AWS , Statistics, Alteryx ,Github, Gitlab, Agile, Stakeholder Management , Alation, Jenkins, Jira , Confluence ,Autosys, HBase, Hadoop, Presto , MicroStrategy , SAP BO, JSON , Couchbase ,Docker ,RESTFUL APIs, AWS S3 ,AWS RedShift, AWS Data Pipeline, AWS EMR ,AWS Lambda , Mixpanel.

CLIENT: Ceva Logistics      					                            Location: Mumbai, India
ROLE: Junior Data Analyst  / Data Analyst                                                         May 2014 – October 2015
Responsibilities:
•	Interpreted logistics datasets using SQL, SAS Language, R, Statistics, MATLAB, Stats Models, and CSV, performing structured Data Processing and ETL from MySQL, Greenplum, Hive, and MongoDB/NoSQL, translating outputs into operational Reporting insights for stakeholders.
•	Extracted and transformed shipment and warehouse data via ETL pipelines using Informatica, DataStage, Apache Spark, and Hive, integrating RESTful APIs, CSV, and MySQL, while automating batch executions through Cron and BASH for reliable data processing cycles.
•	Collaborated with business users through Stakeholder Management, Agile ceremonies, Jira, and Confluence, documenting analytics logic in SharePoint and Data Catalogs such as Collibra, while tracking schema changes using Git to maintain analytical transparency.
•	Developed operational dashboards and standardized Reporting solutions using QlikView, Cognos, and SQL, validating metrics with Statistics, R, SAS Language, and StatsModels, ensuring consistent KPI definitions across Greenplum, MySQL, and Hive environments.
•	Processed high-volume logistics events using Apache Kafka streams and Apache Spark, persisting curated outputs into MongoDB, NoSQL, and Greenplum, while reconciling batch and near-real-time datasets through ETL, Data Processing, and scheduled Cron workflows.
•	Enhanced analyst productivity by scripting data validations with VBA, BASH, and SQL, consuming RESTful APIs, managing version control via Git, and aligning governed assets using Collibra, Data Catalogs, and SharePoint, strengthening audit-ready logistics analytics delivery.
•	Executed an end-to-end analytics workflow by sourcing data from Hive, MySQL, MongoDB, transforming via Informatica, DataStage, Apache Spark, analyzing with R, MATLAB, SAS Language, and publishing governed Reporting through QlikView, Cognos, under Agile delivery models.
Environment: SQL, SAS Language, Greenplum, Stakeholder Management, MATLAB, Statistics, R ,VBA, BASH, MySQL, CSV, RESTFUL APIs, Hive ,Apache Spark, Data Catalogs, , ETL, Data Processing, Jira, Confluence, Git , Reporting, Qlik view, Agile, MongoDB, NO SQL, Apache kafka, Informatica, Data stage, Cognos, StatsModels, Collibra, Sharepoint, Cron.

Education:
Bachelor of Technology                                                                                      2010 - 2014
"""
    
    print("🧪 TESTING SUSHMITHA DANTULURI'S COMPREHENSIVE RESUME")
    print("=" * 70)
    print("Resume Type: Senior Data Analyst - 10+ Years Experience")
    print("Format: Client-Based Consulting Resume (5+ pages)")
    print("Key Sections: Summary, Skills, Certifications, Professional Experience, Education")
    print("=" * 70)
    
    try:
        # Initialize parser
        parser = EnhancedResumePipelineFinal()
        
        # Parse the resume
        result = parser.parse_resume_complete(sushmitha_resume)
        
        print("✅ SUSHMITHA'S RESUME PARSING COMPLETE!")
        print("\n📊 ACCURACY ANALYSIS:")
        print("-" * 50)
        
        # Expected data for Sushmitha's resume
        expected_companies = ["Home Depot", "Huntington", "Walgreens", "T-Mobile", "Ceva Logistics"]
        expected_titles = ["Senior Data Analyst", "Principal Data Analyst", "Senior Data Analyst", "Data Analyst", "Junior Data Analyst / Data Analyst"]
        expected_locations = ["Atlanta, GA", "Columbus, OH", "Deerfield, IL", "Bellevue, WA", "Mumbai, India"]
        expected_skills = ["SQL", "Python", "AWS", "Azure", "GCP", "Tableau", "Power BI", "Spark", "Kafka", "Docker", "Kubernetes"]
        expected_certifications = ["AWS certificatication"]
        
        # Extract actual results
        actual_companies = [work.get('company', '').strip() for work in result.get('work', [])]
        actual_titles = [work.get('title', '').strip() for work in result.get('work', [])]
        actual_locations = [work.get('location', '').strip() for work in result.get('work', [])]
        actual_skills = [skill.get('name', '').strip() for skill in result.get('skills', [])]
        actual_certifications = [cert.get('name', '').strip() for cert in result.get('certifications', [])]
        
        # Calculate accuracy scores
        company_matches = sum(1 for company in expected_companies if any(company.lower() in actual.lower() for actual in actual_companies))
        title_matches = sum(1 for title in expected_titles if any(title.lower() in actual.lower() for actual in actual_titles))
        location_matches = sum(1 for location in expected_locations if any(location.lower() in actual.lower() for actual in actual_locations))
        skill_matches = sum(1 for skill in expected_skills if any(skill.lower() in actual.lower() for actual in actual_skills))
        cert_matches = sum(1 for cert in expected_certifications if any(cert.lower() in actual.lower() for actual in actual_certifications))
        
        # Calculate percentages
        company_accuracy = (company_matches / len(expected_companies)) * 100
        title_accuracy = (title_matches / len(expected_titles)) * 100
        location_accuracy = (location_matches / len(expected_locations)) * 100
        skill_accuracy = (skill_matches / len(expected_skills)) * 100
        cert_accuracy = (cert_matches / len(expected_certifications)) * 100
        
        # Print detailed results
        print(f"🏢 Company Extraction: {company_accuracy:.1f}% ({company_matches}/{len(expected_companies)})")
        print(f"   Expected: {expected_companies}")
        print(f"   Actual: {actual_companies}")
        
        print(f"\n💼 Job Title Extraction: {title_accuracy:.1f}% ({title_matches}/{len(expected_titles)})")
        print(f"   Expected: {expected_titles}")
        print(f"   Actual: {actual_titles}")
        
        print(f"\n📍 Location Extraction: {location_accuracy:.1f}% ({location_matches}/{len(expected_locations)})")
        print(f"   Expected: {expected_locations}")
        print(f"   Actual: {actual_locations}")
        
        print(f"\n🔧 Skills Extraction: {skill_accuracy:.1f}% ({skill_matches}/{len(expected_skills)})")
        print(f"   Expected: {expected_skills}")
        print(f"   Actual: {actual_skills[:15]}...")  # Show first 15
        
        print(f"\n🏆 Certifications Extraction: {cert_accuracy:.1f}% ({cert_matches}/{len(expected_certifications)})")
        print(f"   Expected: {expected_certifications}")
        print(f"   Actual: {actual_certifications}")
        
        # Overall accuracy
        total_expected = len(expected_companies) + len(expected_titles) + len(expected_locations) + len(expected_skills) + len(expected_certifications)
        total_matches = company_matches + title_matches + location_matches + skill_matches + cert_matches
        overall_accuracy = (total_matches / total_expected) * 100
        
        print(f"\n🎯 OVERALL ACCURACY: {overall_accuracy:.1f}%")
        print(f"   Total Expected: {total_expected}")
        print(f"   Total Matches: {total_matches}")
        
        # Performance rating
        if overall_accuracy >= 90:
            rating = "🏆 EXCELLENT - Production Ready"
        elif overall_accuracy >= 80:
            rating = "✅ VERY GOOD - High Quality"
        elif overall_accuracy >= 70:
            rating = "⚠️ GOOD - Acceptable Quality"
        elif overall_accuracy >= 60:
            rating = "⚠️ FAIR - Needs Improvement"
        else:
            rating = "❌ POOR - Major Issues"
        
        print(f"\n🎖️ PERFORMANCE RATING: {rating}")
        
        # Comprehensive metrics
        print(f"\n📈 DETAILED METRICS:")
        print(f"   📄 Total Sections Parsed: {len([k for k, v in result.items() if v])}")
        print(f"   💼 Work Entries: {len(result.get('work', []))}")
        print(f"   🎓 Education Entries: {len(result.get('education', []))}")
        print(f"   🔧 Skills Found: {len(result.get('skills', []))}")
        print(f"   🏆 Certifications Found: {len(result.get('certifications', []))}")
        print(f"   🚀 Projects Found: {len(result.get('projects', []))}")
        
        # Resume complexity analysis
        print(f"\n📊 RESUME COMPLEXITY ANALYSIS:")
        total_words = len(sushmitha_resume.split())
        total_chars = len(sushmitha_resume)
        estimated_pages = total_chars // 3000  # Rough estimate: 3000 chars per page
        
        print(f"   📝 Total Words: {total_words:,}")
        print(f"   📝 Total Characters: {total_chars:,}")
        print(f"   📄 Estimated Pages: {estimated_pages}")
        print(f"   🏢 Companies Mentioned: {len(actual_companies)}")
        print(f"   🎓 Institutions: {len(result.get('education', []))}")
        print(f"   🔧 Technical Skills: {len(actual_skills)}")
        print(f"   🏆 Certifications: {len(actual_certifications)}")
        
        # Client-based format analysis
        print(f"\n🏢 CLIENT-BASED FORMAT ANALYSIS:")
        print(f"   📋 Format: Client-Role-Location structure")
        print(f"   🎯 Unique Challenge: Multiple client engagements")
        print(f"   🔍 Parsing Complexity: High (nested client structures)")
        print(f"   📊 Expected Accuracy: 60-75% (complex format)")
        
        return {
            "overall_accuracy": overall_accuracy,
            "company_accuracy": company_accuracy,
            "title_accuracy": title_accuracy,
            "location_accuracy": location_accuracy,
            "skill_accuracy": skill_accuracy,
            "certification_accuracy": cert_accuracy,
            "rating": rating,
            "total_words": total_words,
            "estimated_pages": estimated_pages,
            "sections_parsed": len([k for k, v in result.items() if v])
        }
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    test_sushmitha_resume()
