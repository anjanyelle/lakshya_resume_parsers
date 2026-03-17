import sys
import os
# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'backend'))

from app.services.parser.work_experience_parser import WorkExperienceParser
import json

def test_company_date_location_format():
    """Test parsing of Company: Date Range (Location: City, State) format"""
    
    # Company: Date Range (Location: City, State) format resume text
    text = """
PROFESSIONAL EXPERIENCE
HCA Healthcare: November 2022 - Current (Location: Nashville, TN) 	
Site Reliability Engineer	
•	Designed and deployed HIPAA-compliant cloud infrastructure on AWS using Terraform and AWS CloudFormation, implementing multi-region deployments with fault-tolerant architectures for EHR systems and patient data processing across development, staging, and production environments with reusable Terraform modules.
•	Established SLOs, SLIs, and error budgets for mission-critical healthcare services, maintained 99.95% uptime for patient-facing applications, developed HIPAA-compliant incident response protocols, and documented post-mortem analyses in Confluence to drive continuous operational improvement and reliability excellence.
•	Built CI/CD pipelines using Jenkins and Git workflows, automated deployments for containerized healthcare microservices with pytest, implemented blue-green deployment strategies, and enforced security scanning and compliance validation using Python and Bash scripting before production releases.
•	Orchestrated Kubernetes clusters on AWS EKS and OpenShift, deployed Docker containers using Helm charts, implemented HIPAA-compliant pod security policies and network segmentation, and maintained cluster health through automated monitoring and capacity planning with Python scripts integrated with AWS CloudWatch.
•	Implemented comprehensive observability systems using Prometheus, Grafana, AWS CloudWatch, and AppDynamics, configured Alertmanager for proactive incident detection, deployed Prometheus exporters across Linux infrastructure, and established custom dashboards tracking SLIs, SLOs, latency, and error rates for real-time visibility.
•	Designed and enforced HIPAA and HITECH security controls, implemented AWS IAM policies and RBAC, configured AWS KMS for secret management and encryption at rest and in transit using SSL/TLS certificates, and established audit logging to CloudWatch Logs for all patient data workflows.
•	Automated operational tasks using Python, Bash, and Go scripts for backup validation, log rotation, certificate renewal, and infrastructure health checks, developed Ansible frameworks for configuration management, and standardized security baselines across AWS cloud infrastructure and on-premise Linux servers.
•	Managed and optimized AWS services including AWS EC2, AWS RDS, AWS Lambda, AWS S3, and AWS Route 53, configured multi-AZ deployments with disaster recovery capabilities, deployed PostgreSQL, MongoDB, and Redis clusters with automated backups, replication, and CloudWatch monitoring.
•	Implemented event-driven architectures using AWS Lambda, AWS SQS/SNS, Kafka, and RabbitMQ for processing healthcare event streams and patient notifications, designed Kafka streaming pipelines for real-time data ingestion, and integrated Pub/Sub messaging patterns to decouple microservices while maintaining HIPAA compliance.
•	Configured load balancing and reverse proxy solutions using Nginx and AWS Route 53 with health checks, implemented SSL/TLS termination, DNS failover, and geo-routing policies, managed Nginx API gateway configurations, and integrated AWS CloudWatch for access logging and performance monitoring supporting troubleshooting.
•	Conducted in-depth troubleshooting and performance optimization of distributed systems, analyzed latency issues and network bottlenecks in Linux environments using AppDynamics and Prometheus, resolved critical Kubernetes pod failures, PostgreSQL database deadlocks, and networking issues applying deep TCP/IP protocol knowledge.
•	Designed disaster recovery and backup strategies for AWS S3, AWS RDS, MongoDB, and Redis, ensured RTO and RPO aligned with HIPAA requirements, automated backup validation and restoration testing using Python scripts integrated with Jenkins to maintain data integrity and patient data security standards.
•	Led incident management processes and facilitated post-mortem analysis sessions using JIRA and Confluence, documented root causes and corrective actions, established incident response playbooks and on-call rotations, and integrated Alertmanager with PagerDuty for escalation during critical production incidents affecting patient care.
•	Enhanced monitoring and logging infrastructure by deploying centralized log aggregation using CloudWatch Logs, implemented retention policies and alerting rules, configured AWS CloudWatch dashboards and custom metrics for AWS Lambda, AWS EKS, and AWS RDS tracking performance, resource utilization, and cost optimization opportunities.
•	Collaborated with development and QA teams to define release management best practices, conducted code reviews and infrastructure design sessions using Git workflows, mentored junior engineers on SRE principles, Terraform module development, and Kubernetes best practices to promote operational excellence across the organization.

Environment: Confluence, Aws Kms, Appdynamics, Aws Cloudwatch, Aws Eks, Aws Ec2, Nginx, AWS S3, Rabbitmq, Aws Route 53, Bash, Jenkins, AWS, Aws Rds, Linux, Openshift, Kafka, Cloudwatch, Mongodb, Pytest, Terraform, Ansible, Kubernetes, Python, Git, Aws Cloud Formation, Alertmanager, Postgresql, Redis, Grafana, Aws Lambda, Aws Iam, Prometheus, Docker, Go, Amazon SQS/SNS, Jira.

American Express: January 2020 - October 2022 (Location: New York, NY) 
Site Reliability Engineer	
	
•	Designed and deployed PCI-DSS-compliant cloud infrastructure on Azure using Terraform and ARM templates for IaC provisioning, implementing fault-tolerant architectures with Azure Kubernetes Service, Azure Virtual Machines, and HAProxy load balancing to achieve 99.95% SLA across multi-region banking transaction systems.
•	Established SRE principles including SLIs, SLOs, and error budgets for banking applications, implementing monitoring frameworks with Prometheus, Grafana, Azure Monitor, and Zabbix to track reliability metrics, while defining incident response workflows that reduced MTTR and improved operational transparency.
•	Built CI/CD pipelines using GitHub Actions and Git workflows for automated deployment of containerized microservices to Kubernetes and OpenShift clusters, incorporating Helm chart management, Python and Bash validation scripts, and automated unittest execution with comprehensive rollback capabilities.
•	Orchestrated distributed systems for real-time payment processing using Docker containers on Azure Kubernetes Service with Helm deployments, configuring event-driven messaging through Azure Service Bus, Kafka, and RabbitMQ with circuit breaker patterns ensuring data integrity across microservices communication.
•	Implemented enterprise observability using ELK Stack, Splunk, CloudWatch, Prometheus, and Alertmanager for centralized logging and metric collection, enabling proactive detection of performance bottlenecks and latency issues in banking transactions while maintaining audit controls aligned with regulatory requirements.
•	Hardened security across Linux infrastructure by configuring Azure Active Directory role-based authentication, managing secrets through Azure Key Vault with automated rotation, deploying Azure Firewall and Azure VPN with segmented subnets, and enforcing PCI-DSS compliance including vulnerability scanning and privileged access audit logging.
•	Automated operational tasks through Python and Bash scripting including backup orchestration to Azure Blob Storage, health checks for Azure SQL Database, MySQL, MongoDB, and Redis instances, certificate renewal workflows, and Terraform state validation to eliminate configuration drift across environments.
•	Deployed serverless architectures using Azure Functions for event-driven fraud detection and compliance reporting, integrating Azure Service Bus and Pub/Sub messaging patterns to improve scalability, while optimizing function performance to maintain sub-second response times for customer-facing transaction validation services.
•	Conducted troubleshooting and root cause analysis of distributed systems failures, resolving networking bottlenecks, database connection issues in PostgreSQL and MySQL, Redis cache invalidation, Kubernetes orchestration failures, and cross-region Azure latency using systematic diagnostic methodologies including distributed tracing.
•	Led incident management processes including real-time coordination, stakeholder communication, and comprehensive post-mortem analysis documentation for Sev1 and Sev2 incidents, facilitating blameless retrospectives that identified systemic weaknesses and drove implementation of preventive controls and monitoring enhancements strengthening site reliability.
•	Optimized performance of high-throughput banking applications through database query tuning in MySQL and Azure SQL Database, Redis caching refinement, Kafka consumer rebalancing, and Azure Monitor profiling with Python instrumentation, ensuring consistent sub-100ms response times for payment authorization workflows.
•	Maintained hybrid cloud and on-premise environments integrating legacy banking systems with Azure infrastructure through Azure VPN gateways, configuring networking topologies with Azure Firewall, and synchronizing MongoDB clusters with Azure Blob Storage for disaster recovery aligned with PCI-DSS mandates.
•	Implemented comprehensive disaster recovery strategies across Azure regions, designing automated failover for Azure Kubernetes Service workloads, Azure SQL Database geo-replication, and stateful recovery procedures, conducting quarterly drills validating RTO/RPO targets and testing Azure Blob Storage restoration processes per regulatory requirements.
•	Developed custom Prometheus exporters in Python for banking-specific metrics including transaction rates and gateway latency, visualizing data through Grafana dashboards, configuring Alertmanager routing to PagerDuty, and establishing alert tuning practices minimizing false positives while ensuring rapid incident response for customer-facing operations.
Environment: Azure, Terraform, ARM Templates, Azure Kubernetes Service (AKS), Azure Virtual Machines, HAProxy, Prometheus, Grafana, Azure Monitor, Zabbix, GitHub Actions, Git, Kubernetes, OpenShift, Helm, Docker, Python, Bash, Azure Service Bus, Kafka, RabbitMQ, ELK Stack (Elasticsearch, Logstash, Kibana), Splunk, Amazon CloudWatch, Alertmanager, Azure Active Directory (AAD), Azure Key Vault, Azure Firewall, Azure VPN Gateway, Azure Blob Storage, Azure SQL Database, MySQL, PostgreSQL, MongoDB, Redis, Azure Functions, PagerDuty.
Best Buy: March 2017 - December 2019 (Location: Richfield, MN) 
Cloud DevOps Engineer

•	Designed and deployed scalable cloud infrastructure on Google Cloud Platform (GCP) using Compute Engine, Google Kubernetes Engine (GKE), Cloud SQL, and Cloud Storage for retail e-commerce applications. Implemented infrastructure as code with Terraform to automate provisioning across environments while maintaining GDPR and PCI-DSS compliance for transaction security.
•	Established comprehensive SLIs, SLOs, and error budgets for retail services ensuring 99.95% uptime, monitored using Prometheus for metrics collection, Grafana for visualization, and Cloud Monitoring for resource tracking. Enabled proactive identification and resolution of performance bottlenecks and latency issues affecting customer checkout workflows during peak periods.
•	Built CI/CD pipelines using GitLab CI/CD integrated with Git workflows to automate deployments for containerized microservices across Kubernetes clusters, reducing deployment time significantly. Developed automation scripts in Python and Bash for infrastructure provisioning, Terraform state management, Docker image builds, and Helm chart deployments.
•	Orchestrated Google Kubernetes Engine (GKE) clusters running Docker containers for 40+ microservices supporting retail operations including product catalog and shopping cart systems. Implemented Helm charts for standardized deployments, configured Envoy service mesh for traffic management, and established pod autoscaling policies based on CPU and memory metrics.
•	Designed comprehensive observability systems using Prometheus for time-series metrics, Grafana dashboards for real-time visualization, Cloud Logging for centralized aggregation, and Loki for log querying. Configured intelligent alert routing through Slack and MS Teams with escalation policies tied to SLO thresholds, reducing mean time to resolution.
•	Managed GCP resources including VPC network design, Cloud DNS configuration, Google Cloud Storage buckets, Cloud SQL for PostgreSQL and MySQL databases, and Cloud Functions for serverless processing. Optimized cloud infrastructure costs through rightsizing recommendations and lifecycle policies while maintaining high availability across critical retail services and applications.
•	Implemented robust security controls using Cloud IAM for role-based access control, GCP Secret Manager for centralized secret management of API keys and database credentials, ensuring GDPR and PCI-DSS compliance. Configured access controls with least privilege principles, established audit logging, and implemented network security policies including firewall rules and VPN tunnels.
•	Built event-driven systems leveraging Google Pub/Sub for asynchronous messaging supporting real-time inventory updates and order processing workflows across the retail platform. Integrated Kafka for high-throughput event streaming between legacy on-premise systems and cloud-native microservices, ensuring data consistency across distributed systems and financial transactions.
•	Performed deep troubleshooting and performance optimization of distributed applications running on Linux systems, analyzing networking bottlenecks and database query patterns in PostgreSQL, MongoDB, and Redis. Resolved critical production incidents including memory leaks and connection pool exhaustion through systematic incident response procedures and detailed root cause analysis.
•	Configured and optimized PostgreSQL and MySQL databases on Cloud SQL with read replicas and automated backups, implemented MongoDB clusters for product catalog storage, and Redis for session management. Enhanced database performance through query optimization, index tuning, and connection pooling, ensuring sub-second response times for critical retail operations.
•	Developed serverless architectures using Cloud Functions triggered by Pub/Sub events and Google Cloud Storage changes to process order confirmations and send customer notifications without managing infrastructure. Implemented event-driven patterns for decoupled system communication, reducing operational complexity and enabling independent scaling while maintaining cost efficiency through pay-per-execution pricing.
•	Established comprehensive CI/CD best practices including Git branching strategies and deployment strategies such as blue-green deployments within GitLab CI/CD pipelines for retail applications. Integrated Selenium for automated end-to-end testing of critical user journeys including checkout flows, ensuring code quality before production releases while maintaining deployment frequency targets.

Environment: Terraform, Python, Linux, Bash, puppet, Kubernetes, Selenium, PostgreSQL, Docker, Prometheus, mesos, GCP, Redis, Git, Grafana, Google Kubernetes Engine, MongoDB, GitLab CI/CD, Kafka, Envoy, Cloud SQL, GCP Secret Manager, Google Pub/Sub, loki, Google Cloud Storage, Cloud Functions, Compute Engine, Pub/Sub.

Progressive: December 2015 - February 2017 (Location: Mayfield Village, OH) 	
DevOps Engineer

•	Designed and managed cloud solutions across AWS and Azure platforms, successfully deploying secure and scalable applications using critical services including AWS EC2, S3, RDS, Azure Virtual Machines, Blob Storage, and Azure SQL Database.
•	Enhanced Software Development Life Cycle (SDLC) by implementing integration with Jenkins, GitHub Actions, and Azure DevOps for CI/CD pipelines, which automated build and deployment processes and reduced release cycles by 25%.
•	Managed software artifact repositories using JFrog/Nexus Artifactory to ensure efficient storage, version control, and distribution across multiple environments.
•	Streamlined administrative tasks with Groovy scripts in AWS, reducing manual efforts by 20% and generating Agile metrics in JIRA to drive data-driven decisions for team performance and productivity optimization.
•	Administered MySQL and MongoDB databases on AWS RDS and Azure Cosmos DB, maintaining high availability, performing critical performance tuning, and implementing automated backup strategies for scalable and secure data management.
•	Implemented robust access management by configuring Identity and Access Management (IAM) roles and policies in AWS and Azure, deploying SSL certificates for encryption, and enforcing Role-Based Access Control (RBAC) to ensure fine-grained security controls.
•	Utilized AWS Key Management Service (KMS) and Azure Key Vault for comprehensive key management, developing disaster recovery strategies and network security configurations to guarantee system security and regulatory compliance.
•	Created and automated infrastructure management scripts using Shell and Python to efficiently handle resources across AWS and Azure environments, reducing manual intervention by 40% and enabling seamless cloud operations.
•	Implemented comprehensive multi-cloud observability and performance monitoring through Datadog and New Relic, developing custom dashboards to track critical AWS metrics including CPU utilization, memory consumption, and latency, while using AWS CloudWatch for real-time monitoring and alerting to ensure proactive issue resolution and optimal system performance.

Environment: Aws, Azure, CI/CD, Git, Jfrog Artifact, JIRA, Ansible playbook, Jenkins pipeline, DevOps methodologies, MySQL, MongoDB, AWS RDS, AWS CloudWatch, IAM, New Relic, Datadog, Shell scripting, Python.

Mastek: June 2014 - October 2015 (Location: Mumbai, India) 
Linux Administrator / System Engineer	

•	Administered and automated Linux/Unix environments, specifically Red Hat Enterprise Linux (RHEL), using Bash and Python scripts to enhance operational efficiency by 25%, streamlining system management and reducing manual intervention.
•	Managed complex system configurations, including Logical Volume Management (LVM) setups, to optimize storage and backup processes, successfully reducing system downtime by 30% through strategic volume management and efficient data organization.
•	Configured and maintained critical network services including DHCP, DNS, and FTP, while implementing robust security protocols such as SSL/TLS and IPSec to ensure secure and reliable network operations across infrastructure.
•	Implemented high availability solutions using Red Hat Clusters and HAProxy, significantly improving system uptime and minimizing service interruptions by 40%, ensuring continuous operational reliability.
•	Developed automated backup strategies and scheduled cron jobs for comprehensive disaster recovery, maintaining data integrity and enabling quick system recovery during potential failures. Implemented extensive system hardening techniques that strengthened security infrastructure and reduced system vulnerabilities by 40%.
•	Performed advanced kernel parameter tuning to optimize system performance, increasing reliability and responsiveness in high-demand computing environments.
•	Managed user and group permissions with SSH key authentication, implementing fine-grained access controls to secure server environments and protect critical system resources.
•	Executed regular system maintenance by patching and updating Linux servers using RPM, YUM, and APT package management tools, maintaining system stability and proactively reducing potential security vulnerabilities.
•	Configured Apache and Nginx web servers to ensure scalable, secure, and efficient service delivery for mission-critical applications, optimizing web infrastructure performance.
•	Integrated Oracle databases with Linux environments, providing comprehensive database administration and performance optimization. Deployed and managed virtual environments using VMware and KVM, improving resource utilization and scalability across multiple data centers.

Environment: Red Hat Enterprise Linux, Bash, Python, Logical Volume Manager, Red Hat Cluster Servers, Oracle, MySQL, DNS, DHCP, FTP.
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
    test_company_date_location_format()
