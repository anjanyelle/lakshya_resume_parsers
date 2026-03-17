import sys
sys.path.append('backend')
from app.services.parser.work_experience_parser import WorkExperienceParser

# Test the parser with Pavan Kumar's resume format
text = '''## PROFESSIONAL EXPERIENCE
Bank of America North Carolina
Sr. Full Stack Developer July 2021 - Present
Environment: Java, Angular, HTML, CSS, Java Script, Spring Boot, No Code / Low Code Platforms, Docker, Kubernetes, Core Java, Multithreading, Message Queuing Systems, Jolt, Couchbase, AWS, Azure, GCP, SQL, No SQL, Microservices, API, Agile, Scrum, ELK stack, Prometheus, Grafana, CI/CD pipelines
- Designed and implemented a robust microservices architecture using Java and Spring Boot for a core banking system, enhancing scalability and maintainability. Utilized Docker and Kubernetes for containerization and orchestration, resulting in improved deployment efficiency and system reliability.
- Developed responsive and interactive user interfaces using Angular and HTML/CSS/Java Script, integrating real-time data visualization for banking dashboards. Implemented Angular material design components to ensure a consistent and user-friendly experience across various banking applications.
Starbucks California
Sr. Java Full Stack Developer Jan 2020 to June 2021
Environment: Java, Angular, HTML, CSS, Java Script, Spring Boot, No Code / Low Code Platforms, Docker, Kubernetes, Core Java, Multithreading, Message Queuing Systems, Jolt, Couchbase, AWS, Azure, GCP, SQL, No SQL, Microservices, API, Agile, Scrum, ELK stack, Prometheus, Grafana, CI/CD pipelines
- Designed and implemented a robust microservices architecture using Java 11 and Spring Boot 2.3, enabling seamless integration of Starbucks' order management system. Utilized Docker containers for efficient deployment and Kubernetes for orchestration, ensuring high availability and scalability of services.
- Developed responsive and interactive user interfaces for Starbucks' mobile app using Angular 9 and Type Script, implementing Core Java concepts for business logic. Integrated RES Tful AP Is to facilitate real-time communication between front-end and back-end services, enhancing overall user experience.
Credit Karma San Francisco
Full Stack Java Developer Feb 2018 to Dec 2019
Environment: Java, Angular, HTML, CSS, Java Script, Spring Boot, No Code / Low Code Platforms, Docker, Kubernetes, Core Java, Multithreading, Message Queuing Systems, Jolt, Couchbase, AWS, Azure, GCP, SQL, No SQL, Microservices, API, Agile, Scrum, ELK stack, Prometheus, Grafana, CI/CD pipelines
- Developed Angular components for financial dashboard interfaces, enhancing Angular performance through lazy loading and efficient change detection strategies.
- Created responsive React applications with Redux state management, implementing optimized React rendering techniques to handle real-time financial data display.
Amazon Hyderabad, India
SDE-II (Java Full Stack Developer) oct 2015 to Dec 2017
Environment: Java 8, Microservices, Spring MVC, Spring Boot, Maven, AWS RDS (My SQL), Postgre SQL, Hibernate, Node.js, Dynamo DB, AWS Lambda, O Auth 2.0, AWS API Gateway, React.js, React Query, Lazy Loading, Redis Caching, Red Hat Open Shift, Docker, Kubernetes, J Unit, Mockito, Jest, Enzyme, Sonar Qube, CI/CD, Cloud-Native Development,Rabbit MQ.
- Utilized Java 8 for microservices development and maintained Maven build artifacts, ensuring efficient dependency management and automation across large-scale projects.
- Designed scalable microservices with Spring MVC and Java, ensuring resilience, fault tolerance, and seamless integration for handling high-traffic applications effectively.
ADP Hyderabad, India
Software Developer Aug 2014 to Aug 2015
Environment: Angular JS, RES Tful API , HTML, CSS, Media Queries, JSP, JSTL, Servlets, Java Script, j Query, DOJO, Struts Tiles, AJAX, Spring MVC, Core Java, Java Collections, Mongo DB, My SQL, GCP(App Engine, Cloud Storage, Cloud SQL.
- Developed Single Page Applications (SPA) using Angular JS Framework, ensuring dynamic interfaces and seamless integration with RES Tful API services for data-driven applications.
- Designed Angular JS modules to dynamically update web pages based on real-time data fetched from REST API services, improving user interactivity and responsiveness.'''

parser = WorkExperienceParser()
print(f"Total text length: {len(text)} characters")
print(f"First 100 chars: {repr(text[:100])}")
print(f"Last 100 chars: {repr(text[-100:])}")
job_chunks = parser.extract_individual_jobs(text)

print(f'Extracted {len(job_chunks)} job chunks:')
for i, chunk in enumerate(job_chunks, 1):
    print(f'\n--- JOB {i} ---')
    print(f'Length: {len(chunk)} characters')
    print(chunk[:200] + ('...' if len(chunk) > 200 else ''))
    print('--- END JOB ---')
