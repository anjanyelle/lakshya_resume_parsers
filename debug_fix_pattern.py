import re

# Test the pattern step by step
text = '''Bank of America North Carolina
Sr. Full Stack Developer July 2021 - Present'''

print("Testing fixed pattern...")
print("Text:", repr(text))

# Fixed pattern - breaking down the complex parts
pattern = r'^([A-Za-z\s&\-]+(?:\s+[A-Za-z\s&\-]+)*)\n([A-Za-z\s&\-\.]+\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}\s*[-–—]\s*(?:Present|Current|[A-Za-z]+\s+\d{4}))'

try:
    job_pattern = re.compile(pattern, re.MULTILINE | re.IGNORECASE)
    matches = list(job_pattern.finditer(text))
    print(f"Found {len(matches)} matches")
    for i, match in enumerate(matches):
        print(f"{i+1}. Company: '{match.group(1)}'")
        print(f"   Title/Date: '{match.group(2)}'")
except Exception as e:
    print(f"Error: {e}")
    print(f"Pattern: {pattern}")

# Test with the actual resume text
print("\nTesting with actual resume text...")
resume_text = '''## PROFESSIONAL EXPERIENCE
Bank of America North Carolina
Sr. Full Stack Developer July 2021 - Present
Environment: Java, Angular, HTML, CSS, Java Script, Spring Boot, No Code / Low Code Platforms, Docker, Kubernetes, Core Java, Multithreading, Message Queuing Systems, Jolt, Couchbase, AWS, Azure, GCP, SQL, No SQL, Microservices, API, Agile, Scrum, ELK stack, Prometheus, Grafana, CI/CD pipelines
- Designed and implemented a robust microservices architecture using Java and Spring Boot for a core banking system, enhancing scalability and maintainability. Utilized Docker and Kubernetes for containerization and orchestration, resulting in improved deployment efficiency and system reliability.
Starbucks California
Sr. Java Full Stack Developer Jan 2020 to June 2021
Environment: Java, Angular, HTML, CSS, Java Script, Spring Boot, No Code / Low Code Platforms, Docker, Kubernetes, Core Java, Multithreading, Message Queuing Systems, Jolt, Couchbase, AWS, Azure, GCP, SQL, No SQL, Microservices, API, Agile, Scrum, ELK stack, Prometheus, Grafana, CI/CD pipelines'''

try:
    job_pattern = re.compile(pattern, re.MULTILINE | re.IGNORECASE)
    matches = list(job_pattern.finditer(resume_text))
    print(f"Found {len(matches)} matches in resume text")
    for i, match in enumerate(matches):
        print(f"{i+1}. Company: '{match.group(1)}'")
        print(f"   Title/Date: '{match.group(2)[:50]}...'")
        print(f"   Position: {match.start()}-{match.end()}")
except Exception as e:
    print(f"Error: {e}")
