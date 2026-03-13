import re

# Check if patterns are matching resume format
resume_text = """Humana: August 2023 - Current (Location: Louisville, KY)  
Role: Sr. Big Data Engineer
Responsibilities:
• Designed and deployed agentic retrieval workflows..."""

# Test the patterns used in extract_individual_jobs
print("=== TESTING PATTERNS ===")

# PATTERN 1: Client: format
client_pattern = re.compile(r'\n\s*Client\s*[:\-\-–]', re.IGNORECASE)
client_matches = client_pattern.findall(resume_text)
print(f'Client pattern matches: {client_matches}')

# PATTERN 2: Company: Date Range format
company_date_pattern = re.compile(r'\n\s*Company\s*:\s*[^\n]+\n', re.IGNORECASE)
company_date_matches = company_date_pattern.findall(resume_text)
print(f'Company date pattern matches: {company_date_matches}')

# Test the actual pattern that should match this resume format
# This resume uses "Company: Date Range" format
company_colon_pattern = re.compile(r'^([^:]+):\s*([^-]+)\s*-\s*[^-\n]+', re.MULTILINE)
company_colon_matches = company_colon_pattern.findall(resume_text)
print(f'Company colon pattern matches: {company_colon_matches}')

# Test a simpler pattern for this format
simple_pattern = re.compile(r'^([^:]+):\s*([^-\n]+)\s*-\s*[^-\n]+', re.MULTILINE)
simple_matches = simple_pattern.findall(resume_text)
print(f'Simple pattern matches: {simple_matches}')

# Test line by line
lines = resume_text.split('\n')
for i, line in enumerate(lines):
    print(f'Line {i}: {repr(line)}')
    if ':' in line and '-' in line:
        print(f'  -> Potential job line!')
