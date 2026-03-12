import re

# Test the pattern on a simple case
text = "Cardinal Health Location: Dublin, OH"
pattern = r'([A-Za-z\s&\-]+?)\s*:\s*Location:\s*([A-Za-z\s,]+)'
matches = re.findall(pattern, text)
print(f"Test 1 - Simple case: {matches}")

# Test on the actual merged text
merged_text = '''Cardinal Health Location: Dublin, OH
DevOps Engineer October 2022 - Current
Responsibilities:
Led enterprise-wide migration from Apigee Edge to Apigee Hybrid for a healthcare provider, designing a secure hybrid cloud architecture enabling compliant access across 15+ clinical systems using Apigee Hybrid, Hybrid Cloud, and HIPAA Compliance. Environment: Terraform, CI/CD, Grafana, Argo CD, Apigee Analytics & Monitoring, Apigee, GIT, Ansible, Prometheus, Jenkins, Kubernetes, Hashicorp Vault, Istio, Apigee Edge, Docker. Huntington: Location: Columbus, OH
Dev Ops Engineer December 2019 - September 2022'''

matches2 = re.findall(pattern, merged_text)
print(f"Test 2 - Merged text: {matches2}")
print(f"Found {len(matches2)} job headers")
