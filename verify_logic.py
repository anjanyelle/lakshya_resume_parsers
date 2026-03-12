import re

# Test the boundary detection logic
text = '''Cardinal Health Location: Dublin, OH
DevOps Engineer October 2022 - Current
Responsibilities:
Led enterprise-wide migration from Apigee Edge to Apigee Hybrid for a healthcare provider, designing a secure hybrid cloud architecture enabling compliant access across 15+ clinical systems using Apigee Hybrid, Hybrid Cloud, and HIPAA Compliance. Environment: Terraform, CI/CD, Grafana, Argo CD, Apigee Analytics & Monitoring, Apigee, GIT, Ansible, Prometheus, Jenkins, Kubernetes, Hashicorp Vault, Istio, Apigee Edge, Docker. Huntington: Location: Columbus, OH'''

print("Testing boundary detection logic:")
print("=" * 50)

# Find all positions where "Location:" appears
job_boundaries = []
for match in re.finditer(r'Location:', text):
    start_pos = match.start()
    job_start = max(0, start_pos - 100)
    context = text[job_start:start_pos]
    
    print(f"Found 'Location:' at position {start_pos}")
    print(f"Context before: {repr(context[-50:])}")
    
    # Find the company name
    company_match = re.search(r'([A-Za-z\s&\-]+?)\s*$', context)
    if company_match:
        company_start = job_start + company_match.start()
        company_name = company_match.group(1).strip()
        job_boundaries.append((company_start, match.group(0)))
        print(f"Company: '{company_name}'")
    print()

print(f"Total boundaries found: {len(job_boundaries)}")
for i, (pos, marker) in enumerate(job_boundaries):
    print(f"{i+1}. Position {pos}: {marker}")

# Test job extraction
if len(job_boundaries) > 1:
    print("\nTesting job extraction:")
    jobs = []
    for i, (start_pos, location_marker) in enumerate(job_boundaries):
        if i + 1 < len(job_boundaries):
            end_pos = job_boundaries[i + 1][0]
        else:
            end_pos = len(text)
        
        job_section = text[start_pos:end_pos].strip()
        jobs.append(job_section)
        print(f"Job {i+1}: {len(job_section)} chars - {job_section[:50]}...")

print(f"\nExtracted {len(jobs)} jobs total")
