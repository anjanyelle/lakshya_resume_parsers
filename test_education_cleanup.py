import sys
sys.path.append('backend')
from app.services.parser.work_experience_parser import WorkExperienceParser

# Test with a resume that has education mixed into work experience
text = '''## PROFESSIONAL EXPERIENCE
Bank of America North Carolina
Sr. Full Stack Developer July 2021 - Present
Environment: Java, Angular, HTML, CSS, Java Script, Spring Boot, No Code / Low Code Platforms, Docker, Kubernetes, Core Java, Multithreading, Message Queuing Systems, Jolt, Couchbase, AWS, Azure, GCP, SQL, No SQL, Microservices, API, Agile, Scrum, ELK stack, Prometheus, Grafana, CI/CD pipelines
- Designed and implemented a robust microservices architecture using Java and Spring Boot for a core banking system, enhancing scalability and maintainability. Utilized Docker and Kubernetes for containerization and orchestration, resulting in improved deployment efficiency and system reliability.
Starbucks California
Sr. Java Full Stack Developer Jan 2020 to June 2021
Environment: Java, Angular, HTML, CSS, Java Script, Spring Boot, No Code / Low Code Platforms, Docker, Kubernetes, Core Java, Multithreading, Message Queuing Systems, Jolt, Couchbase, AWS, Azure, GCP, SQL, No SQL, Microservices, API, Agile, Scrum, ELK stack, Prometheus, Grafana, CI/CD pipelines
- Designed and implemented a robust microservices architecture using Java 11 and Spring Boot 2.3, enabling seamless integration of Starbucks' order management system. Utilized Docker containers for efficient deployment and Kubernetes for orchestration, ensuring high availability and scalability of services.
ADP Hyderabad, India
Software Developer Aug 2014 to Aug 2015
Environment: Angular JS, RES Tful API , HTML, CSS, Media Queries, JSP, JSTL, Servlets, Java Script, j Query, DOJO, Struts Tiles, AJAX, Spring MVC, Core Java, Java Collections, Mongo DB, My SQL, GCP(App Engine, Cloud Storage, Cloud SQL.
- Developed Single Page Applications (SPA) using Angular JS Framework, ensuring dynamic interfaces and seamless integration with RES Tful API services for data-driven applications.
EDUCATION
Bharath University - Bachelor of Technology Computer Science August 2010 to May 2014'''

parser = WorkExperienceParser()
parsed_jobs = parser.parse_experience_section(text, source_format=None)

print(f'Parsed {len(parsed_jobs)} jobs:')
for i, job in enumerate(parsed_jobs, 1):
    print(f'\n--- JOB {i} ---')
    print(f'Company: {job.company}')
    print(f'Title: {job.title}')
    print(f'Location: {job.location}')
    print(f'Start Date: {job.start_date}')
    print(f'End Date: {job.end_date}')
    print(f'Is Current: {job.is_current}')
    print(f'Description (first 200 chars): {job.description[:200] if job.description else "None"}...')
    print(f'Bullets count: {len(job.bullets) if job.bullets else 0}')
    print('--- END JOB ---')
