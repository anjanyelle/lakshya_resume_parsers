import re

# Test the fixed pattern
resume_text = """Humana: August 2023 - Current (Location: Louisville, KY)
Role: Sr. Big Data Engineer
Responsibilities:
- Designed and deployed agentic retrieval workflows using Python, Lang Chain, and Lang Graph to build context-aware agents ingesting PR metadata, commit metadata, and Git Hub history, enabling automated CES scoring and quality metric computation for healthcare pipelines while ensuring HIPAA-compliant audit trails and HL 7 interoperability across AWS S 3, AWS Lambda, and AWS Glue.

Morgan Stanley: October 2020 - July 2023 (Location: New York, NY)
Role: Sr Data Engineer
- Designed and deployed production-grade data pipelines using Python and Dagster on AWS, ingesting PR metadata, commit metadata, and code quality telemetry from Git Hub and Jenkins, integrating AWS Lambda, AWS S 3, AWS Glue, and AWS ECS to ensure PCI-DSS-compliant financial workflows, automated retries, backfills, and observability with metrics, traces, and logs.

Delta Airlines: December 2017 - September 2020 (Location: Atlanta, GA)
Role: Data Engineer / Data Analyst
- Designed and deployed production-grade data pipelines using Python and Apache Airflow to ingest commit metadata and PR metadata from Git Hub, integrating AWS Lambda and AWS Event Bridge for real-time processing, exposing quality metrics via REST AP Is, ensuring SOC 2 audit trails and FAA/IATA compliance across aviation engineering workflows.

Cisco: February 2016 - November 2017 (Location: San Jose, CA)
Role: Data Engineer / Migration Specialist
- Built a Network Data Integration platform using Azure Cloud, improving enterprise data integration efficiency while enabling seamless data flow across global networking systems by consolidating monitoring telemetry from thousands of devices deployed in international data centers.

Flipkart: August 2014 - December 2015 (Location: Bangalore, India)
Role: ETL Developer
- Built a scalable ETL pipeline using AWS Services, Informatica, and Talend, integrating data from e commerce platforms, inventory systems, and customer databases to create a unified data flow supporting high volume daily transaction processing across multiple online retail channels."""

print("=== TESTING FIXED PATTERN ===")

# Test the new pattern
company_date_pattern = re.compile(r'^[^:]+:\s*[A-Z][a-z]+\s+\d{4}\s*-\s*[^-\n]+', re.MULTILINE)
matches = company_date_pattern.findall(resume_text)
print(f"Company date pattern matches: {matches}")

# Test the splitting logic
parts = re.split(r'\n(?=[A-Z][a-zA-Z\s&]+:\s*[A-Z][a-z]+\s*\d{4})', resume_text)
print(f"Split parts count: {len(parts)}")
for i, part in enumerate(parts):
    if part.strip():
        lines = part.strip().split('\n')
        first_line = lines[0]
        company = first_line.split(':')[0]
        print(f"Part {i}: {company}")
        print(f"  First line: {first_line}")
        print()

# Test extract_individual_jobs logic
def test_extract_individual_jobs(text):
    # PATTERN 1: Client: format (highest priority)
    client_pattern = re.compile(r'\n\s*Client\s*[:\-\-–]', re.IGNORECASE)
    client_matches = client_pattern.findall(text)
    
    if len(client_matches) >= 2:
        print(f"Found {len(client_matches)} client markers, splitting by client")
        parts = client_pattern.split(text)
        client_blocks = []
        for p in parts:
            p_strip = p.strip()
            if p_strip:
                client_blocks.append(p_strip)
        if len(client_blocks) >= 1:
            return client_blocks
    
    # PATTERN 2: Company: Date Range (Location: City, State) format
    company_date_pattern = re.compile(r'^[^:]+:\s*[A-Z][a-z]+\s+\d{4}\s*-\s*[^-\n]+', re.MULTILINE)
    if company_date_pattern.search(text):
        print("Found Company: Date Range format, splitting")
        parts = re.split(r'\n(?=[A-Z][a-zA-Z\s&]+:\s*[A-Z][a-z]+\s*\d{4})', text)
        company_blocks = []
        for p in parts:
            p_strip = p.strip()
            if p_strip:
                company_blocks.append(p_strip)
        if len(company_blocks) >= 1:
            return company_blocks
    
    # PATTERN 3: Standard job boundaries
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines:
        return []
    
    return [text]

result = test_extract_individual_jobs(resume_text)
print(f"Extracted {len(result)} job blocks:")
for i, job in enumerate(result):
    print(f"Job {i+1}: {job[:50]}...")
