"""
Debug script to understand why company names are being replaced with descriptions.
"""

from parsers.experience_extractor import ExperienceExtractor

# Sample problematic job block (based on the output you showed)
sample_block = """Role:Senior Python Engineer
Built enterprise web applications using Flask and AngularJS
Developed ETL pipelines using Python  Pandas
Integrated RabbitMQ for asynchronous messaging
Wrote SQL optimization scripts reducing query time by 30%"""

print("=" * 80)
print("DEBUGGING COMPANY NAME EXTRACTION")
print("=" * 80)

extractor = ExperienceExtractor()

# Test the extraction
result = extractor._parse_job_experience(sample_block)

print("\nInput Block:")
print("-" * 80)
print(sample_block)
print("-" * 80)

print("\nExtracted Data:")
print("-" * 80)
print(f"Job Title: {result.get('job_title')}")
print(f"Company Name: {result.get('company_name')}")
print(f"Description: {result.get('description')[:100]}..." if result.get('description') else "Description: None")
print("-" * 80)

print("\nISSUE: Company name should be extracted from the resume, not the description!")
print("\nExpected company_name: 'TechCorp' or similar (from actual resume)")
print(f"Actual company_name: '{result.get('company_name')}'")

# Test with a properly formatted block
proper_block = """Senior Python Engineer
Google Inc.
March 2020 - Present | Hyderabad, India
Built enterprise web applications using Flask and AngularJS
Developed ETL pipelines using Python and Pandas"""

print("\n" + "=" * 80)
print("TESTING WITH PROPERLY FORMATTED BLOCK")
print("=" * 80)

result2 = extractor._parse_job_experience(proper_block)

print("\nInput Block:")
print("-" * 80)
print(proper_block)
print("-" * 80)

print("\nExtracted Data:")
print("-" * 80)
print(f"Job Title: {result2.get('job_title')}")
print(f"Company Name: {result2.get('company_name')}")
print(f"Start Date: {result2.get('start_date')}")
print(f"End Date: {result2.get('end_date')}")
print(f"Location: {result2.get('location')}")
print(f"Description: {result2.get('description')[:100]}..." if result2.get('description') else "Description: None")
print("-" * 80)
