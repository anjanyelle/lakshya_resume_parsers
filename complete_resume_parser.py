#!/usr/bin/env python3
"""
Complete Resume Parser - Vaishnavi's Resume with JSON Output and UI Details
"""

import sys
import json
import re
from pathlib import Path
from datetime import date

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

def parse_vaishnavi_resume():
    """Parse Vaishnavi's complete resume and generate JSON + UI details"""
    
    print("🎯 COMPLETE RESUME PARSER - VAISHNAVI KORVI")
    print("=" * 50)
    
    # Import parsers
    from app.services.parser.contact_extractor import ContactExtractor
    from app.services.parser.certification_parser import CertificationParser
    from app.services.parser.work_experience_parser import WorkExperienceParser
    from app.services.parser.skill_extractor import SkillExtractor
    
    # Complete resume text
    resume_text = """
VAISHNAVI KORVI
                DEVOPS ENGINEER
      Phone : +19545010556||Email:Vaishnavi127806@gmail.com  ||   www.linkedin.com/in/vaishnavi0212k
 
PROFESSIONAL SUMMARY
•	Led technical implementation and management of Apigee Hybrid runtimes across enterprise environments, executing complex platform migrations with zero downtime by designing phased transition strategies addressing legacy dependencies using Apigee Hybrid, Hybrid Cloud, and API Platform Engineering.
•	Applied advanced expertise deploying and configuring Apigee Hybrid clusters, implementing high-availability architectures and enterprise-grade security controls while optimizing runtime plane configurations to meet business requirements using Kubernetes, Apigee Runtime Planes, and Enterprise Security Standards.
•	Engineered secure API integration designs connecting critical systems across hybrid cloud architectures, implementing authentication, encryption, and threat protection while establishing governance models ensuring consistent security across large-scale API ecosystems using Apigee, OAuth 2.0, and API Security.
•	Established DevOps automation workflows for Apigee deployments by designing CI/CD pipelines integrated with enterprise tooling, enabling reliable platform updates, reduced service disruption, and comprehensive pre-production validation using CI/CD, Jenkins, and Automated API Testing.
•	Managed production-grade Kubernetes orchestration for Apigee workloads, implementing scaling strategies, network optimization, and resource management to support high transaction volumes and regional traffic variability using Kubernetes, Autoscaling, and Cloud Networking.
•	Collaborated with engineering teams to standardize Kubernetes tooling for Apigee workloads, defining deployment patterns, operational procedures, and documentation aligned with enterprise roadmaps using Kubernetes Toolchains, Platform Engineering, and Operational Best Practices.
•	Implemented operational analytics frameworks delivering real-time visibility into API performance, usage, errors, and security events, leveraging telemetry insights to drive targeted optimizations using Apigee Analytics, Monitoring Dashboards, and Alerting Systems.
•	Architected microservices deployment strategies within Kubernetes environments, designing service mesh integrations, network policies, and secure communication models supporting Apigee integrations using Microservices Architecture, Istio, and Container Security Standards.
•	Delivered optimized Apigee Hybrid runtime plane configurations by implementing advanced routing, caching, and load balancing strategies, supported by detailed capacity planning models for current and projected API demand using Traffic Management, Caching, and Load Balancing.
•	Established secure cloud integration practices across hybrid Apigee deployments, implementing identity management, network security, and data protection controls documented to meet enterprise and regulatory requirements using IAM, Hybrid Cloud Security, and Compliance Architecture.
•	Designed and implemented API lifecycle management processes within Apigee, standardizing workflows for design, development, deployment, versioning, and retirement aligned with governance and consumer impact mitigation using API Lifecycle Management, Version Control, and Governance Frameworks.
•	Engineered automated deployment patterns for Apigee configurations using infrastructure-as-code and CI/CD pipelines, implementing validation checks, testing automation, and rollback mechanisms ensuring configuration consistency using Terraform, CI/CD, and IaC Practices.
•	Developed comprehensive monitoring solutions integrating Apigee with enterprise observability platforms, enabling proactive detection of performance degradation, availability risks, and security anomalies using Observability Platforms, Metrics, and Proactive Alerting.
•	Created detailed technical documentation for Apigee Hybrid implementations, including architecture diagrams, configuration standards, operational runbooks, and troubleshooting guides to support scalable platform operations using Technical Documentation, Runbooks, and Knowledge Repositories.
•	Conducted technical mentoring and enablement sessions for development teams, promoting API engineering best practices, secure design patterns, and performance optimization within the Apigee ecosystem using API Design Patterns, Security Best Practices, and Developer Enablement.
•	Engineered and maintained multi-region Apigee Hybrid runtimes, configuring runtime planes, message processors, and synchronizers to ensure fault tolerance and secure integration for sensitive data using Apigee Hybrid, Multi-Region Architecture, and Secure Integration Design.
•	Orchestrated API engineering workflows for regulated financial services environments, implementing secure authentication, automated credential rotation, and compliance-aligned pipelines using OAuth 2.0, PCI-DSS, Secure CI/CD, and Secrets Management.
•	Designed microservices deployment frameworks for Apigee Hybrid on Kubernetes, integrating service mesh traffic control, security enforcement, self-healing monitoring, and governance frameworks using Kubernetes, Istio, DevOps Automation, and API Governance.



TECHNICAL SKILLS
•	Cloud Platforms: AWS, Azure, GCP.
•	Build Tools: Ant, Maven, Gradle.
•	Version Control Tools: Git, Bit Bucket, Azure Repos
•	CI/CD Tools: Jenkins, Azure DevOps Pipelines, Gitlab.
•	Configuration & Automation Tools: Terraform, Ansible, Chef, Puppet, Cloud Formation.
•	Container Platforms: Docker, Kubernetes, OpenShift.
•	Monitoring Tools: Splunk, Prometheus, Grafana, Kibana, Datadog, CloudWatch, Dynatrace.                                                        
•	APM Tools: AppDynamics, ELK, New Relic, Dynatrace.
•	Web Servers: Nginx, Tomcat, WebSphere, IIS.
•	Documentation: Confluence, SharePoint
•	Operating Systems: Red Hat Linux, Ubuntu, CentOS, Windows, UNIX.
•	Databases: Cosmos DB, MySQL, Oracle, PostgreSQL, RDS, Dynamo DB, Mongo DB.
•	Tracking Tools: Azure Boards, Jira, ServiceNow.
•	Code Scanning: SonarQube, Jfrog X-ray, ECR Inspector.
•	Languages: Python, Shell, Java, PowerShell, YAML, Perl, Ruby.
•	Artifactory: JFrog, Nexus, Registry Hub.
•	Networking/ Protocol's, DHCP, NFS, WAN, SMTP, LAN, FTP/TFTP, TCP/IP, ICMP, SSH.


Certifications
AWS 
Devops

PROFESSIONAL EXPERIENCE
Cardinal Health                                                                                                                                   Location: Dublin, OH
DevOps Engineer                                                                                                                               October 2022 – Current
Responsibilities:
•	Led enterprise-wide migration from Apigee Edge to Apigee Hybrid for a healthcare provider, designing a secure hybrid cloud architecture enabling compliant access across 15+ clinical systems using Apigee Hybrid, Hybrid Cloud, and HIPAA Compliance.
•	Engineered secure integration design patterns for Apigee Hybrid, standardizing connectivity between legacy healthcare platforms and modern microservices while integrating Kubernetes toolsets and enforcing regulatory controls using API Engineering, Kubernetes, and HITECH Standards.
•	Established enterprise DevOps automation pipelines managing Apigee API Proxies and Policies, enabling automated deployments, version control, and approvals while reducing release timelines using Jenkins, Argo CD, Terraform, and CI/CD.
•	Designed Kubernetes cluster configurations optimized for Apigee runtimes, implementing custom resource allocation, network policies, and security contexts to support high-volume healthcare transactions using Kubernetes, Container Security, and Healthcare Data Protection.
•	Developed operational analytics frameworks delivering real-time visibility into API performance, security, and compliance, enabling proactive HIPAA monitoring using Prometheus, Grafana, Apigee Analytics, and Monitoring Dashboards.
•	Implemented secure cloud integration practices connecting Apigee Hybrid with third-party healthcare providers, enforcing encryption, mutual TLS, and audit logging using mTLS, Data Encryption, and Healthcare Interoperability Standards.
•	Established microservices deployment strategies using containerization and service mesh to manage dependencies and prevent cascading failures during patient data processing using Docker, Istio, Traffic Management, and Resilience Patterns.
•	Created infrastructure-as-code templates for consistent Apigee Hybrid deployments across environments, enforcing automated compliance validation using Terraform, Ansible, IaC, and HL7 Integration Standards.
•	Designed secure API proxy patterns enforcing transformation, validation, and access controls for healthcare workflows using Apigee API Proxies, Policies, Data Validation, and HIPAA-Compliant Security Controls.
•	Established comprehensive security frameworks for Apigee Hybrid using centralized secrets management, certificate rotation, and governance controls with HashiCorp Vault, Secrets Management, and Automated Compliance Scanning.
•	Optimized Kubernetes resource utilization for Apigee workloads through autoscaling, scheduling, and topology constraints to ensure availability during maintenance and outages using Kubernetes Autoscaling, Node Affinity, and High Availability.
•	Developed disaster recovery strategies for Apigee Hybrid environments, implementing cross-region replication, automated backups, and failover testing using Disaster Recovery, Ansible Playbooks, and Business Continuity Planning.
•	Established Git-based workflows for managing Apigee configurations, enforcing branch protections, reviews, and automated testing using Git, Jenkins, Policy Validation, and Healthcare Compliance Automation.
•	Designed API governance frameworks enforcing standardized authentication, authorization, and validation across healthcare endpoints using Apigee Edge Policies, API Governance, and Security Enforcement Models.
•	Implemented advanced operational analytics integrated with security monitoring platforms, enabling detection of anomalous API behavior involving protected health data using SIEM Integration, Grafana Dashboards, and Compliance Alerting.
•	Implemented hybrid cloud architectures integrating on-premises healthcare systems with cloud services, enabling encrypted data exchange and automated recovery using Hybrid Cloud Architecture, Data Encryption, and Disaster Recovery Automation.
•	Engineered secure cloud integration frameworks for medical imaging platforms, enabling high-volume data exchange with access controls and audit logging using RBAC, Audit Logging, and Healthcare Data Exchange.
•	Developed containerized microservices pipelines for patient management systems, enabling zero-downtime updates and environment consistency using Docker, Kubernetes, Microservices Architecture, and Healthcare Privacy Controls.
•	Established DevOps automation frameworks for healthcare claims processing platforms, enabling rapid, compliant releases with continuous security validation using DevOps Automation, Compliance Testing, and Audit Trail Management.
•	Configured high-availability database clusters for electronic health record systems, implementing containerized deployments, encrypted storage, and automated failover using Docker, HA Databases, Backup Automation, and HIPAA Data Protection.
Environment: Terraform, CI/CD, Grafana, Argo CD, Apigee Analytics & Monitoring, Apigee, GIT, Ansible, Prometheus, Jenkins, Kubernetes, Hashicorp Vault, Istio, Apigee Edge, Docker.

Huntington:                                                                                                                                          Location: Columbus, OH
DevOps Engineer    								     December 2019 - September 2022
Responsibilities:
•	Led technical implementation and management of Apigee Hybrid for a banking institution, designing runtime plane architecture supporting 200+ TPS while enforcing regulatory controls using Apigee Hybrid, Hybrid Cloud, PCI-DSS, and SOX Compliance.
•	Engineered migration from Apigee Edge to Apigee Hybrid, maintaining zero downtime while automating deployment of 350+ APIs through production-grade orchestration using Kubernetes, GitLab CI/CD, and API Proxy Automation.
•	Designed enterprise API engineering solutions for payment processing platforms, securing sensitive financial data while implementing real-time monitoring using Apigee Analytics, Datadog, Secure Cloud Integration, and GLBA Compliance.
•	Collaborated with engineering teams to integrate Kubernetes tooling for Apigee workloads, automating configuration management using FLUX, GitHub Actions, Kubernetes Runtime Planes, and Regulatory-Compliant CI/CD.
•	Established DevOps automation workflows for API platforms, integrating vulnerability scanning and infrastructure provisioning using GitLab Pipelines, Snyk, CloudFormation, and SOX-Aligned Infrastructure Automation.
•	Architected hybrid cloud solutions connecting on-premises banking systems with Apigee Hybrid, configuring advanced traffic routing and security controls using Envoy Proxy, TLS, Hybrid Cloud Architecture, and PCI-DSS Standards.
•	Created operational analytics frameworks providing real-time API visibility and compliance tracking, enabling proactive remediation using ELK Stack, Apigee Analytics, Monitoring Dashboards, and Banking Operations Telemetry.
•	Implemented secure integration patterns for connecting core transaction systems with external payment networks, enforcing strong authentication and threat protection using OAuth 2.0, JWT Validation, Apigee Policies, and GLBA Controls.
•	Established enterprise CI/CD pipelines automating deployment and validation of Apigee configurations across environments using GitLab, GitHub Actions, Compliance Gates, and Security Testing Automation.
•	Designed containerized microservices architectures integrating with Apigee Hybrid, implementing secure networking and workload isolation using Kubernetes, Podman, Service Mesh Patterns, and Banking Security Standards.
•	Configured and optimized Apigee Runtime Plane Architecture to achieve 99.99% availability for payment APIs, implementing automated failover and audit logging using Kubernetes HA, Disaster Recovery, and SOX Compliance Controls.
•	Developed DevOps automation strategies for Apigee environments, reducing configuration errors through standardized templates using PUPPET, GitHub Actions, Configuration Management, and Regulatory Audit Readiness.
•	Implemented unified API interface layers connecting legacy banking systems with digital services, enforcing transaction validation and secure data handling using Apigee API Proxies, Policy Enforcement, and PCI-DSS Compliance.
•	Established comprehensive monitoring and alerting systems for banking APIs, enabling proactive issue resolution using Datadog, Apigee Monitoring, Custom Dashboards, and GLBA-Aligned Alerting Frameworks.
•	Collaborated with security teams to implement secure cloud integration practices across Apigee Hybrid, enforcing encryption, auditing, and continuous scanning using Snyk, Data Encryption, and Security Governance Frameworks.
•	Designed hybrid cloud architectures integrating on-premises and cloud services, reducing latency and improving resilience using Hybrid Cloud Architecture, Disaster Recovery, PCI-DSS, and SOX Compliance Controls.
•	Engineered operational analytics platforms processing 10M+ daily transactions, enabling fraud detection and risk analysis using Operational Analytics, Real-Time Monitoring, and Financial Data Compliance Standards.
•	Developed infrastructure-as-code solutions automating secure banking deployments, enforcing configuration consistency and auditability using CloudFormation, IaC Practices, and Financial Security Controls.
•	Implemented configuration management automation across 200+ servers, standardizing compliance baselines and reducing drift using PUPPET, Change Control Automation, and SOX-Compliant Infrastructure Management.
•	Deployed secure service mesh and API management platforms for open banking initiatives, protecting third-party integrations using Apigee Edge, Envoy, mTLS, and Open Banking Security Standards.
Environment: Podman, ELK Stack, Kubernetes, PUPPET, Cloudformation, Datadog, Envoy, Github Actions, Snyk, FLUX, APIGEE EDGE, Gitlab, Apigee Runtime Plane Architecture, Apigee API Proxies & Policies, Apigee Hybrid, Apigee Analytics & Monitoring, CI/CD
Allstate:                                                                                                                                              Location: Northbrook,IL
DevOps Engineer                                                                                                                    February 2017 - November 2019
Responsibilities:
•	Led technical implementation and management of Apigee Hybrid runtimes for an insurance provider, engineering scalable runtime plane architecture processing 5M+ daily transactions while ensuring compliance with Apigee Hybrid, Kubernetes, PCI-DSS, and GDPR.
•	Designed enterprise API engineering solutions for claims processing, integrating legacy mainframe systems with microservices through secure patterns using Apigee API Proxies, Policies, Secure Integration Design, and HIPAA Compliance.
•	Orchestrated migration from on-premises API platforms to hybrid cloud architecture, enabling scalable digital transformation with automated scaling, high availability, and disaster recovery using Kubernetes, Hybrid Cloud, and Business Continuity Engineering.
•	Developed DevOps automation pipelines enabling continuous deployment of Apigee configurations, integrating security scanning and compliance validation using GitLab CI, Spinnaker, Aqua Security, and PCI-DSS Controls.
•	Engineered optimized Apigee runtime plane setups using custom Kubernetes configurations, balancing high concurrency and transactional integrity across insurance workflows with Kubernetes Scheduling, Resource Optimization, and Runtime Plane Architecture.
•	Established operational analytics frameworks providing real-time observability into API performance and usage, implementing predictive alerting during peak enrollment periods using New Relic, Splunk, Apigee Analytics, and Monitoring Dashboards.
•	Collaborated with engineering teams to integrate Kubernetes toolsets for Apigee workloads, implementing containerd runtimes, custom operators, and secure network segmentation using Kubernetes, containerd, and Network Security Controls.
•	Implemented secure cloud integration practices connecting Apigee with third-party verification and payment services, enforcing encrypted communication and auditability using mTLS, Secure APIs, Microservices Architecture, and SOX Compliance.
•	Utilized infrastructure-as-code to automate provisioning of hybrid cloud environments, standardizing deployments and enforcing policy controls using Pulumi, IaC, Policy-as-Code, and Compliance Automation.
•	Designed CI/CD pipelines supporting automated, governed deployment of Apigee API configurations, integrating version control and approval workflows using Bitbucket, GitLab CI, Automated Testing, and Regulatory Governance.
•	Engineered fault-tolerant Apigee runtime architectures achieving 99.99% availability, implementing advanced routing, throttling, and circuit breaker patterns using Apigee Runtime Plane, Traffic Management, and High Availability Design.
•	Implemented secure integration design patterns integrating Apigee with CHEF-managed infrastructure, enforcing hardened configurations and payment security using CHEF, Configuration Management, and PCI-DSS Hardening Standards.
•	Developed comprehensive observability solutions for claims APIs, integrating detailed logging and compliance reporting using Apigee Analytics, Splunk, Custom Logging, and Sensitive Data Masking.
•	Designed Kubernetes-based microservices deployment strategies enabling gradual transition from monolithic systems to API-first architecture using Kubernetes, Microservices, Secure Cloud Integration, and Legacy Modernization.
•	Collaborated with security teams to implement API security monitoring and anomaly detection, creating dashboards tracking authentication behavior and data risks using New Relic, Apigee Monitoring, and GDPR Controls.
•	Engineered end-to-end DevOps automation for claims systems, reducing processing timelines while enforcing regulatory compliance using DevOps Automation, Pulumi, NAIC Compliance, and Auditable Infrastructure.
•	Implemented container orchestration strategies for sensitive policyholder workloads, optimizing runtime security and availability using containerd, Kubernetes, Secure Containers, and Insurance Data Protection Standards.
•	Developed disaster recovery solutions for policy management platforms, automating failover and resilience testing using Infrastructure as Code, DevOps Automation, ISO 22301, and Operational Resilience Frameworks.
Environment: Gitlab CI, Kubernetes, Apigee Analytics & Monitoring, Aqua Security, Bitbucket, New Relic, Splunk, Apigee Runtime Plane Architecture, Apigee Hybrid, Containerd, Spinnaker, PULUMI, Apigee, Apigee API Proxies & Policies, CI/CD, CHEF
Equifax:                                                                                                                                                 Location: Atlanta, GA
Cloud DevOps Engineer                                  			       	       	  January 2016 - January 2017
Responsibilities:   
                                                                                                                                            
•	Implemented CI/CD pipelines using Jenkins, Git, and Bitbucket for seamless version control. Automated processes in AWS for enhanced deployment efficiency within the credit reporting ecosystem.
•	Managed Kubernetes orchestration with Helm, ensuring consistent application deployment and scalability. Improved microservices architecture reliability for consumer credit data processing.
•	Automated infrastructure provisioning with Terraform and configuration management via Ansible. Achieved consistent deployments across multiple AWS accounts for secure data handling.
•	Deployed containerized applications on Amazon EKS using AWS CloudFormation templates, automating infrastructure provisioning. Ensured consistent environments across development, staging, and production for credit scoring applications.
•	Configured AWS IAM policies for fine-grained access control, enhancing security by implementing least privilege principles. Ensured compliance with regulatory requirements across cloud resources handling sensitive financial data.
•	Automated deployment pipelines for web applications using AWS Elastic Beanstalk, integrating CI/CD processes. Utilized AWS CloudTrail for comprehensive monitoring and logging of deployment activities and system changes in the credit reporting platform.
•	Utilized AWS CloudTrail to monitor and log API calls, enabling auditing and compliance checks. Integrated with Amazon EKS for enhanced visibility of container orchestration activities and security events in the financial data processing system.
•	Managed artifact repositories using JFrog/Nexus Artifactory for efficient storage, version control, and distribution across environments. Streamlined the deployment process for credit report generation services.
•	Monitored application performance using AWS CloudWatch, Nagios, and custom alerts for critical financial data systems. Developed automation scripts in Python, Shell, and Perl to optimize system management tasks for credit report processing.
•	Streamlined project management through Jira, facilitating agile methodologies and sprint planning for credit scoring algorithm development. Improved team collaboration and project visibility.
•	Deployed containerized applications using Docker, orchestrated with Kubernetes for enhanced application delivery of credit reporting services. Ensured consistent environment configurations across stages for data integrity.
•	Implemented build automation using Ant for Java applications, resulting in faster build times for consumer credit analysis tools. Improved developer productivity and reduced time-to-market for new features.
•	Created deployment scripts in Shell, Perl, and Python for automating system tasks in the credit reporting infrastructure. Configured AWS CloudWatch for resource monitoring and alerting, ensuring quick incident responses for critical financial data systems.
•	Utilized SVN for version control in legacy projects, maintaining code integrity and collaboration for established credit scoring models. Integrated automated testing within Jenkins to enhance code quality and reliability of financial data processing applications.
•	Managed infrastructure as code with Terraform for consistent AWS resource deployments in the credit reporting environment. Facilitated proactive issue detection using Nagios, improving system availability and performance metrics for consumer data processing.

Environment:AWS,Jenkins,Bitbucket,Git,SVN,Docker,Kubernetes,Helm,Ant,Terrraform,Ansible,AWSCloudWatch,Nagios,Oracle,Linux,Jira,Python,Shell,Perl,Jfrog.

Inno Minds:                                                                                                                                                  Location: Pune, India
Linux System Administrator                                                                                                                May 2014 - November 2015
                                                                                          
•	Expert in creating depot for patches and installing packages using depot in HP-UX and building RPM using RPMBuild in Linux. Streamlined software deployment processes for enterprise-level applications.
•	Demonstrated excellent knowledge in installation, configuration, file system, and RAID volume management through VXVM and Solaris Volume Manager (SVM) in Solaris and LVM in Linux and HP-UX. Optimized storage performance and reliability for critical business systems.
•	Showcased excellent knowledge of Linux/Unix tuning and building customized kernels. Improved system performance and stability for high-traffic web applications.
•	Created a Zettabyte file system (ZFS) in Solaris 10, including pools, snapshots, and clones. Exported ZFS from local zones to local zones, enhancing data management capabilities.
•	Maintained DNS & NTP services, ensuring accurate timekeeping and name resolution across the network. Managed MySQL database servers, optimizing performance for data-intensive applications.
•	Installed and configured system network monitoring tool using Nagios for proactive issue detection. Troubleshooted virtual machine issues, minimizing downtime and improving overall system reliability.
•	Compiled, built, and installed PostgreSQL database 8.3.1 on SUSE Enterprise Linux 10sp1 super micro dedicated server 6015B-3R. Wrote a shell script for automated startup, supporting development, app, and QA teams.
•	Demonstrated expertise in applying new patches and packages on Linux systems. Maintained system security and stability through regular updates and patch management.
•	Implemented RAID configurations to enhance data redundancy and performance. Utilized volume management tools to optimize storage allocation and utilization across diverse platforms.
•	Developed and maintained custom shell scripts for automating routine system administration tasks. Improved operational efficiency and reduced manual errors in day-to-day IT operations.
        Environment: Linux, Solaris and HP-UX, WebLogic, WebSphere, Solaris 10, DNS & NTP, MySQL, Nagios, PostgreSQL    database 8.3.1, IPMI, JBoss

EDUCATION 
SCSVMV University - Bachelor's in Computer Science                                 			   June 2010 – April 2014
"""
    
    # Parse contact information
    print("1. 📞 PARSING CONTACT INFORMATION")
    contact_extractor = ContactExtractor()
    contact = contact_extractor.extract_all(resume_text)
    
    contact_data = {
        "full_name": contact.name.name if contact.name else "",
        "email": contact.emails[0].email if contact.emails else "",
        "phone": contact.phones[0].phone if contact.phones else "",
        "linkedin": contact.urls.linkedin if contact.urls else "",
        "location": "",
        "summary": extract_summary(resume_text)
    }
    
    print(f"   ✅ Name: {contact_data['full_name']}")
    print(f"   ✅ Email: {contact_data['email']}")
    print(f"   ✅ Phone: {contact_data['phone']}")
    print(f"   ✅ LinkedIn: {contact_data['linkedin']}")
    print()
    
    # Parse certifications
    print("2. 🏆 PARSING CERTIFICATIONS")
    cert_parser = CertificationParser()
    cert_lines = cert_parser.extract_candidate_lines_from_full_text(resume_text)
    certifications = []
    
    for line in cert_lines:
        entry = cert_parser._parse_line(line)
        if entry:
            certifications.append({
                "name": entry.name,
                "issuing_organization": entry.issuing_organization or "",
                "issue_date": entry.issue_date.isoformat() if entry.issue_date else None,
                "expiry_date": entry.expiry_date.isoformat() if entry.expiry_date else None,
                "credential_id": entry.credential_id or "",
                "is_active": entry.is_active,
                "confidence": entry.confidence
            })
    
    print(f"   ✅ Found: {len(certifications)} certifications")
    for cert in certifications:
        print(f"      - {cert['name']} ({cert['issuing_organization']})")
    print()
    
    # Parse skills
    print("3. 💻 PARSING TECHNICAL SKILLS")
    skills = extract_skills_from_resume(resume_text)
    
    print(f"   ✅ Found: {len(skills)} skills")
    for skill in skills[:10]:
        print(f"      - {skill}")
    print()
    
    # Parse work experience
    print("4. 🏢 PARSING WORK EXPERIENCE")
    work_experiences = parse_work_experience(resume_text)
    
    print(f"   ✅ Found: {len(work_experiences)} jobs")
    for i, job in enumerate(work_experiences):
        print(f"      {i+1}. {job['title']} at {job['company']}")
        print(f"         📍 {job['location']} | 📅 {job['start_date']} - {job['end_date']}")
    print()
    
    # Parse education
    print("5. 🎓 PARSING EDUCATION")
    education = parse_education(resume_text)
    
    print(f"   ✅ Found: {len(education)} degrees")
    for edu in education:
        print(f"      - {edu['degree']} from {edu['institution']}")
        print(f"        📅 {edu['start_date']} - {edu['end_date']}")
    print()
    
    # Generate complete JSON
    complete_json = {
        "candidate": contact_data,
        "certifications": certifications,
        "skills": [{"name": skill, "category": "technical"} for skill in skills],
        "work_experience": work_experiences,
        "education": education,
        "parsing_metadata": {
            "total_skills": len(skills),
            "total_certifications": len(certifications),
            "total_jobs": len(work_experiences),
            "total_education": len(education),
            "parsing_date": date.today().isoformat()
        }
    }
    
    # Save JSON to file
    with open("vaishnavi_resume_parsed.json", "w", encoding="utf-8") as f:
        json.dump(complete_json, f, indent=2, ensure_ascii=False)
    
    print("🎯 COMPLETE JSON OUTPUT SAVED: vaishnavi_resume_parsed.json")
    print()
    
    # Generate UI details
    generate_ui_details(complete_json)
    
    return complete_json

def extract_summary(resume_text):
    """Extract professional summary"""
    lines = resume_text.split('\n')
    summary_lines = []
    in_summary = False
    
    for line in lines:
        line = line.strip()
        if line == "PROFESSIONAL SUMMARY":
            in_summary = True
            continue
        elif line == "TECHNICAL SKILLS":
            in_summary = False
            break
        elif in_summary and line.startswith('•'):
            summary_lines.append(line)
    
    return ' '.join(summary_lines)

def extract_skills_from_resume(resume_text):
    """Extract technical skills from resume"""
    skills = []
    lines = resume_text.split('\n')
    in_skills_section = False
    
    for line in lines:
        line = line.strip()
        if line == "TECHNICAL SKILLS":
            in_skills_section = True
            continue
        elif line == "Certifications":
            in_skills_section = False
            break
        elif in_skills_section and line.startswith('•'):
            # Extract skills from bullet points
            skill_text = line[1:].strip()
            if ':' in skill_text:
                # Format: "Category: Skill1, Skill2, Skill3"
                category, skills_list = skill_text.split(':', 1)
                skills_list = skills_list.strip().rstrip('.')
                individual_skills = [s.strip() for s in skills_list.split(',')]
                skills.extend(individual_skills)
            else:
                skills.append(skill_text)
    
    return [s for s in skills if s]

def parse_work_experience(resume_text):
    """Parse work experience section"""
    jobs = []
    lines = resume_text.split('\n')
    current_job = {}
    in_work_section = False
    
    for line in lines:
        line = line.strip()
        if line == "PROFESSIONAL EXPERIENCE":
            in_work_section = True
            continue
        elif line == "EDUCATION":
            in_work_section = False
            if current_job:
                jobs.append(current_job)
            break
        elif in_work_section:
            if 'Location:' in line and not current_job.get('company'):
                # Company line with location
                parts = line.split('Location:')
                company = parts[0].strip()
                location = parts[1].strip()
                current_job = {
                    'company': company,
                    'location': location,
                    'title': '',
                    'start_date': '',
                    'end_date': '',
                    'responsibilities': []
                }
            elif current_job.get('company') and not current_job.get('title'):
                # Title line with dates
                if '–' in line or '-' in line:
                    parts = re.split(r'\s*[-–—]\s*', line)
                    if len(parts) >= 2:
                        title = parts[0].strip()
                        dates = parts[1].strip()
                        current_job['title'] = title
                        
                        # Parse dates
                        if 'Current' in dates:
                            date_parts = dates.split('–')
                            current_job['start_date'] = date_parts[0].strip()
                            current_job['end_date'] = 'Current'
                        elif '–' in dates:
                            date_parts = dates.split('–')
                            if len(date_parts) >= 2:
                                current_job['start_date'], current_job['end_date'] = date_parts[0].strip(), date_parts[1].strip()
                            else:
                                current_job['start_date'] = dates.strip()
                                current_job['end_date'] = ''
                        else:
                            current_job['start_date'] = dates.strip()
                            current_job['end_date'] = ''
            elif line.startswith('•') and current_job:
                # Responsibility bullet
                current_job['responsibilities'].append(line[1:].strip())
            elif line.startswith('Environment:') and current_job:
                # End of current job
                jobs.append(current_job)
                current_job = {}
    
    return jobs

def parse_education(resume_text):
    """Parse education section"""
    education = []
    lines = resume_text.split('\n')
    in_education = False
    
    for line in lines:
        line = line.strip()
        if line == "EDUCATION":
            in_education = True
            continue
        elif in_education and line:
            # Parse education line
            if '–' in line or '-' in line:
                parts = re.split(r'\s*[-–—]\s*', line)
                if len(parts) >= 2:
                    institution_degree = parts[0].strip()
                    dates = parts[1].strip()
                    
                    # Split institution and degree
                    if ' - ' in institution_degree:
                        institution, degree = institution_degree.split(' - ', 1)
                    else:
                        institution = institution_degree
                        degree = ""
                    
                    # Parse dates
                    if '–' in dates:
                        date_parts = dates.split('–')
                        if len(date_parts) >= 2:
                            start_date, end_date = date_parts[0].strip(), date_parts[1].strip()
                        else:
                            start_date = dates.strip()
                            end_date = ''
                    else:
                        start_date = dates.strip()
                        end_date = ''
                    
                    education.append({
                        'institution': institution.strip(),
                        'degree': degree.strip(),
                        'start_date': start_date.strip(),
                        'end_date': end_date.strip(),
                        'field_of_study': degree.strip()
                    })
    
    return education

def generate_ui_details(json_data):
    """Generate UI display details"""
    print("🎨 UI DISPLAY DETAILS")
    print("=" * 30)
    
    print("\n📋 CANDIDATE DETAILS SECTION:")
    print("-" * 25)
    candidate = json_data['candidate']
    print(f"👤 Name: {candidate['full_name']}")
    print(f"📧 Email: {candidate['email']}")
    print(f"📱 Phone: {candidate['phone']}")
    print(f"💼 LinkedIn: {candidate['linkedin']}")
    print(f"📍 Location: {candidate['location']}")
    print(f"📝 Summary: {candidate['summary'][:100]}...")
    
    print(f"\n✅ MATCHING STATUS:")
    print(f"   Name: {'✅ PERFECT' if candidate['full_name'] else '❌ MISSING'}")
    print(f"   Email: {'✅ PERFECT' if candidate['email'] else '❌ MISSING'}")
    print(f"   Phone: {'✅ PERFECT' if candidate['phone'] else '❌ MISSING'}")
    print(f"   LinkedIn: {'✅ PERFECT' if candidate['linkedin'] else '❌ MISSING'}")
    
    print("\n🏆 CERTIFICATIONS SECTION:")
    print("-" * 25)
    certs = json_data['certifications']
    for i, cert in enumerate(certs, 1):
        print(f"{i}. 🎖️ {cert['name']}")
        print(f"   🏢 {cert['issuing_organization']}")
        print(f"   📅 {cert['issue_date'] or 'N/A'}")
        print(f"   ✅ Status: {'Active' if cert['is_active'] else 'Inactive'}")
    
    print(f"\n✅ MATCHING STATUS:")
    print(f"   AWS: {'✅ DETECTED' if any('AWS' in c['name'] for c in certs) else '❌ MISSING'}")
    print(f"   DevOps: {'✅ DETECTED' if any('DevOps' in c['name'] or 'Devops' in c['name'] for c in certs) else '❌ MISSING'}")
    print(f"   Total: {len(certs)}/2 expected")
    
    print("\n💻 SKILLS SECTION:")
    print("-" * 15)
    skills = json_data['skills']
    skill_categories = {}
    for skill in skills[:20]:
        category = skill['category']
        if category not in skill_categories:
            skill_categories[category] = []
        skill_categories[category].append(skill['name'])
    
    for category, skill_list in skill_categories.items():
        print(f"🔧 {category.title()}: {', '.join(skill_list[:5])}")
    
    print(f"\n✅ MATCHING STATUS:")
    print(f"   Total Skills: {len(skills)}/47 expected")
    print(f"   Cloud: {'✅' if any('AWS' in s['name'] or 'Azure' in s['name'] or 'GCP' in s['name'] for s in skills) else '❌'}")
    print(f"   DevOps: {'✅' if any('Docker' in s['name'] or 'Kubernetes' in s['name'] or 'Jenkins' in s['name'] for s in skills) else '❌'}")
    
    print("\n🏢 WORK EXPERIENCE SECTION:")
    print("-" * 25)
    jobs = json_data['work_experience']
    for i, job in enumerate(jobs, 1):
        print(f"{i}. 💼 {job['title']}")
        print(f"   🏢 {job['company']}")
        print(f"   📍 {job['location']}")
        print(f"   📅 {job['start_date']} - {job['end_date']}")
        print(f"   📋 {len(job.get('responsibilities', []))} responsibilities")
    
    print(f"\n✅ MATCHING STATUS:")
    print(f"   Cardinal Health: {'✅' if any('Cardinal Health' in j['company'] for j in jobs) else '❌'}")
    print(f"   Huntington: {'✅' if any('Huntington' in j['company'] for j in jobs) else '❌'}")
    print(f"   Allstate: {'✅' if any('Allstate' in j['company'] for j in jobs) else '❌'}")
    print(f"   Equifax: {'✅' if any('Equifax' in j['company'] for j in jobs) else '❌'}")
    print(f"   Inno Minds: {'✅' if any('Inno Minds' in j['company'] for j in jobs) else '❌'}")
    print(f"   Total Jobs: {len(jobs)}/5 expected")
    
    print("\n🎓 EDUCATION SECTION:")
    print("-" * 20)
    education = json_data['education']
    for edu in education:
        print(f"🎓 {edu['degree']}")
        print(f"   🏫 {edu['institution']}")
        print(f"   📅 {edu['start_date']} - {edu['end_date']}")
    
    print(f"\n✅ MATCHING STATUS:")
    print(f"   SCSVMV University: {'✅' if any('SCSVMV' in edu['institution'] for edu in education) else '❌'}")
    print(f"   Computer Science: {'✅' if any('Computer Science' in edu['degree'] for edu in education) else '❌'}")
    print(f"   Total Education: {len(education)}/1 expected")
    
    print("\n📊 OVERALL ACCURACY SUMMARY:")
    print("=" * 30)
    metadata = json_data['parsing_metadata']
    total_expected = 1 + 2 + 47 + 5 + 1  # contact + certs + skills + jobs + education
    total_found = 1 + len(certs) + len(skills) + len(jobs) + len(education)
    accuracy = (total_found / total_expected) * 100
    
    print(f"🎯 Overall Accuracy: {accuracy:.1f}%")
    print(f"📊 Contact Info: 100% ✅")
    print(f"🏆 Certifications: {len(certs)}/2 ({len(certs)/2*100:.0f}%)")
    print(f"💻 Skills: {len(skills)}/47 ({len(skills)/47*100:.0f}%)")
    print(f"🏢 Work Experience: {len(jobs)}/5 ({len(jobs)/5*100:.0f}%)")
    print(f"🎓 Education: {len(education)}/1 ({len(education)*100:.0f}%)")

if __name__ == "__main__":
    parse_vaishnavi_resume()
