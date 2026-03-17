import sys
import os
# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'backend'))

from app.services.parser.work_experience_parser import WorkExperienceParser
import json

def test_client_format():
    """Test parsing of Client/Role/Location format"""
    
    # Client format resume text
    text = """
PROFESSIONAL EXPERIENCE:
Client: Nike                                                                                                                                                    Location: Beaverton, OR
Role: Senior Full Stack Developer                                                                                                                 January 2023 – Current
Responsibilities:
•	Designed and developed middle-tier business logic using Java and Spring Boot, implementing RESTful APIs to support a SaaS-based retail platform serving customer-facing and merchant operations, ensuring high transaction throughput and low latency across distributed microservices architecture hosted on AWS EKS and AWS EC2 instances.
•	Built native iOS mobile applications for retail merchants using Swift, UIKit, and SwiftUI, integrating RESTful APIs developed in Java to enable real-time inventory management, order tracking, and payment processing while ensuring seamless API integration, responsiveness, and offline data synchronization.
•	Implemented service layer frameworks using Spring Boot and Spring Cloud to orchestrate complex workflows across order management, payment gateway, and fulfillment services, applying Design Patterns including Factory, Singleton, Strategy, and Observer to maintain SOLID principles and code reusability.
•	Developed API contracts and Swagger-based documentation for cross-functional teams, ensuring alignment between iOS mobile clients built with Swift and backend Java services, while participating in architecture and design reviews to validate scalability, security, and PCI-DSS compliance for all payment processing workflows.
•	Integrated AWS Lambda functions for event-driven processing of order confirmations and inventory updates, connected via AWS SQS and AWS SNS for asynchronous messaging, and consumed Kafka streams for real-time analytics and reporting pipelines, ensuring fault tolerance and transaction consistency.
•	Collaborated with Product Owners and business stakeholders to review and translate functional specifications into technical designs and user stories within the Agile and SAFe framework, participating in sprint planning, backlog refinement, and increment planning events to deliver customer-facing features.
•	Worked closely with QA teams to design comprehensive test cases and integration tests using JUnit, Mockito, and XCTest for backend Java services and iOS applications, ensuring code coverage, functional accuracy, and regression prevention while coordinating with CM team for CI/CD pipelines.
•	Optimized application performance by implementing multithreading, connection pooling, and caching strategies using Redis and Spring Cache within Java services handling heavy transaction volumes, while debugging and resolving memory leaks, race conditions, and API latency issues in both Java backend and Swift-based iOS applications.
•	Provisioned and managed AWS infrastructure using Terraform and AWS CDK, deploying AWS RDS MySQL, AWS S3 for asset storage, AWS WAF for web application firewall protection, and AWS Lambda for serverless functions, ensuring PCI-DSS compliance, data encryption, and audit logging via Splunk.
•	Mentored junior and mid-level developers on Java design principles, Object-Oriented Programming, Design Patterns, and iOS development best practices using Swift, UIKit, and SwiftUI, conducting code reviews, pair programming sessions, and technical workshops to advocate for code quality and maintainability.
•	Designed scalable microservices architectures using Java Spring Cloud, implemented asynchronous messaging with Kafka and RabbitMQ, applied circuit breaker patterns with Resilience4j for fault-tolerant high-transaction systems.
•	Integrated third-party services including payment gateways, shipping APIs, and fraud detection systems into both Java backend services and iOS mobile applications built with Swift, ensuring secure token handling, PCI-DSS compliance, OAuth 2.0 authentication, and end-to-end encryption to protect sensitive customer information.
•	Configured monitoring and observability solutions using Prometheus, Grafana, Splunk, and AWS CloudWatch to track API response times, error rates, throughput metrics, and system health for Java microservices and iOS app backend interactions, enabling proactive incident detection and root cause analysis.
•	Implemented centralized logging using Logback and Splunk for structured log aggregation across all Java services, AWS Lambda functions, and Kafka event streams, enabling audit trails, transaction traceability, and debugging support in production environments while ensuring GDPR and PCI-DSS compliance.
•	Designed and developed RESTful APIs using Java, Spring Boot, and Spring Cloud Gateway to expose secure, scalable endpoints consumed by iOS applications built with Swift, UIKit, and SwiftUI, implementing rate limiting, request validation, JWT-based authentication, and versioning strategies.
•	Participated in offshore team coordination by leading daily standups, conducting technical knowledge transfer sessions, and reviewing code submissions from distributed team members across time zones, ensuring consistent code quality, adherence to coding standards, and alignment with Agile sprint goals using Jira and Confluence.
•	Developed modular and reusable UI components in iOS using SwiftUI and UIKit, applying MVVM architecture and Swift reactive programming patterns with Combine framework to bind REST API responses from Java backend services to the mobile interface, ensuring testability, maintainability, and responsive user experience.
•	Supported production deployments and post-release monitoring by coordinating with CM team and DevOps engineers to execute blue-green deployments, canary releases, and rollback procedures using Jenkins, Docker, and AWS EKS, ensuring zero-downtime deployments and minimal customer impact during critical retail events.
•	Enhanced data consistency and transactional integrity by implementing distributed transaction management patterns using Saga and two-phase commit strategies across Java microservices, Kafka event streams, and AWS RDS MySQL databases, ensuring ACID compliance and data accuracy for retail order processing and payment settlement workflows.
Environment: Kafka, Git, AWS WAF, AWS EC2, AWS Lambda, docker, Gradle, Java, SQL, Xcode, JUnit, AWS EKS, AWS S3, Splunk, angular, logback, jira, grafana, Swift, swagger, AWS RDS, jenkins, Terraform, UIKit, AWS, AWS SQS, prometheus, Maven, SwiftUI, AWS CDK, MySQL, AWS SNS, SpringCloud, Spring Boot
Client: BNY Mellon                                                                                                                                      Location: New York, NY
Role: Senior Full Stack Developer                                                                                                    March 2020 – December 2022
Responsibilities:
•	Designed and developed middle-tier APIs using Java, Spring Boot, and Helidon frameworks for a SaaS financial trading platform, implementing RESTful services that exposed business logic while ensuring PCI-DSS compliance for secure payment transaction processing across all endpoints.
•	Built native iOS mobile applications using Swift, UIKit, and SwiftUI frameworks, integrating REST APIs developed in Java to enable real-time account management and fund transfers while implementing OAuth 2.0 authentication protocols within Xcode environment.
•	Managed Agile workflows using Jira and Azure Boards, implemented unit testing with JUnit, Mockito, and XCTest, established CI/CD pipelines using Jenkins and GitLab CI with Git version control.
•	Implemented object-oriented design patterns including Singleton, Factory, Observer, and Strategy in Java middleware to handle high transaction volumes exceeding 50,000 requests per hour, utilizing multithreading and JVM tuning for optimized performance and SOX compliance.
•	Deployed containerized Java microservices to Azure AKS using Terraform infrastructure-as-code and Azure Bicep templates, configuring CI/CD pipelines with Git and Maven while implementing Azure Service Bus for asynchronous messaging and Kafka for event streaming.
•	Integrated third-party payment gateway APIs into iOS applications using Swift and UIKit, consuming RESTful endpoints built with Java and Spring Boot to enable secure credit card processing while implementing encryption controls satisfying PCI-DSS requirements.
•	Developed service layer frameworks in Java to encapsulate business logic for loan origination and credit card authorization workflows, implementing SOX-compliant audit trails and design patterns including DAO and Repository for enterprise-grade maintainability.
•	Troubleshot and optimized application performance for iOS Swift applications and Java backend services, utilizing Splunk for centralized logging to identify bottlenecks, implementing connection pooling with MySQL databases and caching mechanisms to reduce response times.
•	Designed and implemented Azure Functions serverless components in Java to handle batch processing of financial transactions, integrating with Azure Service Bus queues and utilizing Spring Boot for dependency injection while ensuring GLBA privacy requirements.
•	Mentored team members on Java development best practices, object-oriented design principles, and design patterns application, conducting code reviews to enforce standards for RESTful API design while advocating automated testing with JUnit within Agile methodologies.
•	Ensured performance and responsiveness of iOS applications built with Swift, UIKit, and SwiftUI by implementing comprehensive unit testing using XCTest framework, collaborating with QA teams for defect resolution to maintain PCI-DSS and GLBA compliant experiences.
•	Integrated Kafka event streaming platform with Java Spring Boot microservices to support real-time fraud detection, implementing event-driven architecture patterns to process payment events and trigger alerts while ensuring message persistence met SOX audit requirements.
•	Worked with configuration management teams to establish CI/CD pipelines using Git, Maven, Gradle, and Azure DevOps, implementing automated code quality gates and security scanning to ensure Java and Swift releases met PCI-DSS compliance standards.
•	Developed financial advisor-facing features in iOS mobile applications using Swift and Java, implementing secure document upload and electronic signature workflows that consumed REST APIs built with Spring Boot and Helidon frameworks while maintaining GLBA confidentiality.
•	Implemented database connectivity layers in Java using MySQL for transactional data storage, designing normalized schema structures for customer accounts while working with database developers to optimize query performance ensuring SOX audit trail requirements.
•	Provided APIs using Java service layer frameworks including Spring Boot and Helidon that exposed business logic for interest calculation and loan amortization, implementing error handling and RESTful conventions while enforcing PCI-DSS security controls.
•	Monitored application health using Splunk dashboards for Azure AKS-hosted Java microservices and iOS mobile analytics, configuring alerts for transaction failures and security anomalies while coordinating with operations teams to implement automated remediation through Azure Functions.
Environment: SwiftUI, Terraform, Azure AKS, Maven, Kafka, Gradle, Helidon, Swift, REST, JUnit, MySQL, Spring Boot, Azure, Git, UIKit, Java, Azure Functions, Splunk, Azure Bicep, SQL, Azure Service Bus, Xcode

Client: Cigna Health                                                                                                                                      Location: Charlotte, NC
Role: Java developer                                                                                                                                May 2017 – February 2020
Responsibilities:
•	Developed middle-tier business logic using Java and Spring Boot for a SaaS-based physician application, exposing RESTful APIs consumed by iOS applications built with Swift, UIKit, and SwiftUI, while implementing Microservices architecture patterns.
•	Built iOS mobile applications using Swift, UIKit, and SwiftUI within Xcode, integrating with backend Java RESTful APIs through JSON serialization, implementing HIPAA-compliant TLS encryption and PHI data masking across both layers.
•	Collaborated with Product Owners to translate functional specifications into technical designs for physician workflows, ensuring compliance with HIPAA standards throughout Agile sprint cycles using SAFe methodology and Jira tracking.
•	Implemented OO design patterns including Singleton, Factory, and MVVM across Java Microservices and Swift iOS clients, enabling reusable components for high-transaction healthcare workflows processing over 50,000 concurrent sessions using Spring Boot frameworks.
•	Integrated FHIR and HL7 messaging into Java backend services using Kafka for asynchronous processing, orchestrating data exchange between EHR systems and iOS mobile clients while implementing AWS Lambda for event-driven workflows.
•	Optimized middle-tier architecture using Spring Boot and Quarkus, implementing multithreading and JVM tuning to maintain sub-200ms API response times under peak load, ensuring ACID compliance for transactions stored in MySQL and AWS RDS.
•	Designed normalized schemas in MySQL and AWS RDS, optimizing SQL queries for physician dashboards, implementing indexing strategies and ORM mappings using Hibernate within Java services, ensuring PHI encryption compliance with HIPAA requirements.
•	Participated in architecture and code reviews with cross-functional teams, advocating for code quality standards and HIPAA-compliant practices, mentoring developers on Java Microservices design, RESTful API best practices, and Swift iOS integration.
•	Ensured iOS application performance by implementing asynchronous networking using URLSession in Swift, optimizing UI rendering in UIKit and SwiftUI, conducting memory profiling to maintain smooth physician experiences on iPhone and iPad devices.
•	Configured CI/CD pipelines using Jenkins, automating Maven builds for Java Microservices, orchestrating Docker containerization, deploying to AWS EKS clusters, and integrating XCTest automation for iOS regression testing and releases.
•	Deployed cloud infrastructure on AWS using Terraform, provisioning AWS EC2 instances, AWS Lambda serverless functions, AWS S3 for HIPAA-compliant audit logs, AWS RDS databases, and AWS SQS for message queuing workflows.
•	Implemented API security controls including OAuth 2.0 authentication, JWT validation in Java middleware, RBAC for users, and SSL/TLS certificate pinning in Swift iOS clients, ensuring end-to-end HIPAA compliance and PHI protection.
•	Collaborated with QA teams to define test case design, writing JUnit tests for Java services achieving 85% coverage, supporting UAT sessions with clinical stakeholders, and resolving defects through Jira workflows and JUnit validation.
•	Integrated Kafka event streaming into Java backend for real-time physician notifications, designing producer and consumer components within Spring Boot Microservices, implementing idempotency strategies, and ensuring HIPAA-compliant logging for PHI data through Kafka topics.
•	Troubleshot and optimized performance across Swift iOS clients and Java backend services using Splunk for log aggregation, resolving API bottlenecks, fixing memory leaks in Swift controllers, and tuning JVM garbage collection with JUnit performance testing.
Environment: AWS EKS, Xcode, Git, AWS, AWS EC2, SwiftUI, AWS RDS, Quarkus, Java, AWS SQS, CI/CD, Maven, Kafka, AWS Lambda, MySQL, Gradle, Swift, Terraform, JUnit, UIKit, AWS WAF, SQL, Spring Boot, AWS S3, Splunk, AWS CDK
Client: ADP                                                                                                                                                    Location: Roseland, NJ
Role: Backend Developer                                                                                                                   December 2015 – April 2017
Responsibilities:
•	Participated in all phases of the SDLC for payroll and workforce management systems, supporting requirement gathering through development using Agile practices while documenting HR workflows using UML to ensure alignment across employee processes.
•	Managed front-end, business, and persistence tiers using JSP, JavaScript, and Hibernate to enhance payroll applications, performing extensive performance tuning with JProfiler that reduced pay period calculation times by 30%.
•	Developed microservices and APIs using Spring Cloud, Spring Security, and Spring Boot to support secure payroll data transfer, building user-friendly interfaces that improved employee self-service capabilities and reduced submission errors.
•	Provisioned and optimized Aurora PostgreSQL clusters for high-volume payroll databases, implementing resilient backup and failover strategies while configuring Spring Boot service connections for improved tax calculation system integration.
•	Contributed to open-source Maven plugins focused on payroll rule validation and set up RabbitMQ clusters to support real-time payroll event streaming, designing queueing mechanisms that prioritized critical pay events during high-volume periods.
•	Used Eclipse as primary Java IDE to create XML formats for payroll data interchange while utilizing CVS for version control, Jira for tracking enhancements, and implementing Jenkins pipelines for deployment of payroll module updates.
•	Implemented exactly-once processing semantics using RabbitMQ's transactional messaging to maintain accuracy in payroll disbursements, building idempotent logic for batch processing that improved data integrity across earnings and deductions workflows.
•	Designed scalable microservices architectures using Java Spring Cloud, implemented asynchronous messaging with Kafka and RabbitMQ, applied circuit breaker patterns with Resilience4j for fault-tolerant high-transaction systems.
•	Integrated RabbitMQ to manage serialization of payroll data structures in streaming applications, configuring fault-tolerant environments with replication features that ensured uninterrupted pay cycle operations even under network instability.
•	Configured and optimized OpenShift clusters to support production deployments of HR and payroll applications, implementing resource quotas and utilizing service mesh capabilities to improve communication between microservices.
Environment: Java 8, Spring Boot, Microservices, Restful API, PostgreSQL, pgAdmin, PL/SQL, Agile, JavaScript, Git, Spring Cloud, Maven, Spring Security, Jenkins, Jira, RabbitMQ, Docker, Kubernetes, Junit, Terraform, Hibernate, Postman, Mockito, GKE, Google compute engine, GCP Cloud, GCP Cloud SQL, Apigee API Management, Maven, Jenkins, Git, OpenShift, Jprofiler
Client: Amazon India                                                                                                                             Location: Bangalore, India
Role: Backend Developer                                                                                                                      June 2014 – October 2015
Responsibilities:
•	Implemented Scrum practices for e-commerce platform development teams, boosting sprint velocity by 30% while establishing daily stand-ups and bi-weekly retrospectives that significantly reduced time-to-market for seller onboarding workflows.
•	Applied design patterns including Singleton, Factory, and J2EE patterns such as Business Delegate and DAO for order processing systems, enhancing code maintainability across fulfillment center integration points.
•	Employed Spring Framework's IoC Dependency Injection to inject inventory service objects into product listing action classes using Service Locator Design Pattern, improving modularity of the seller portal codebase.
•	Developed responsive user interfaces for seller dashboards using HTML, JavaScript, and JSP, integrating third-party payment gateways and logistics APIs seamlessly into the marketplace application.
•	Executed high-traffic e-commerce applications under J2EE architecture, utilizing Spring, Struts, Hibernate, Servlets, WebLogic, and JSP for seller portal infrastructure that achieved high uptime during major sales events.
•	Developed microservices with Spring Boot for inventory management and implemented Coherence cache for product metadata, enhancing application scalability during flash sales and reducing database load by 60%.
•	Utilized Hibernate for Object-Relational Mapping (ORM) of marketplace entities, enabling efficient database querying through HQL while implementing custom caching strategies that maintained data consistency across distributed seller systems.
•	Generated code for Java Bean classes, form handlers, and JSP pages for seller registration workflows using RAD on IBM WebSphere, accelerating development time for new marketplace features by 40%.
•	Implemented Spring AOP modules for cross-cutting concerns like logging and security in seller authentication system, while using Azure Blob Storage for efficient storage of product images and seller documents.
•	Designed scalable microservices architectures using Java Spring Cloud, implemented asynchronous messaging with Kafka and RabbitMQ, applied circuit breaker patterns with Resilience4j for fault-tolerant high-transaction systems.
•	Developed comprehensive test cases using JUnit for order processing components and Protractor for automation testing of seller portal interfaces, achieving 85% test coverage and reducing post-deployment issues by 50%.
Environment: Java 8, JSP, Spring MVC, Servlets, JavaScript, Hibernate, Microsoft SQL Server,Scrum, WSDL, SOAP, JAX-B, Log4j, XML, JNDI, JMS, JSTL, RMI, Struts, Generics, Multithreading, JML, Azure Repos, Azure Functions, Amazon SNS, Spring, WebLogic, AOP, SQL, JUnit, SVN, Log4J, IBM WebSphere
"""
    
    print("=" * 60)
    print("TESTING CLIENT/ROLE/LOCATION FORMAT PARSING")
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
    test_client_format()
