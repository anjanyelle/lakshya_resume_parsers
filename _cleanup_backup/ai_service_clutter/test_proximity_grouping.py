#!/usr/bin/env python3
"""
Test script to demonstrate proximity-based entity grouping
"""

from inference_example import ResumeParser

# Initialize parser
parser = ResumeParser()

# Test resume with multiple job entries
test_resume = """
Rajesh Kumar is a Senior Software Engineer with extensive experience.

Work Experience:

1. Tech Lead at TCS in Hyderabad from Jan 2022 to Present
   - Led a team of 10 developers
   - Worked on cloud migration projects for Google as client

2. Full Stack Developer at Infosys in Bangalore from March 2018 to December 2021
   - Developed web applications for Microsoft client
   - Implemented microservices architecture

3. Software Engineer at Wipro in Pune from June 2015 to February 2018
   - Built REST APIs for Amazon client
   - Database optimization work

Education:
- M.Tech in Artificial Intelligence from IIT Bombay (2013-2015)
- B.Tech in Computer Science from IIT Delhi (2009-2013)
"""

print("="*80)
print("TESTING PROXIMITY-BASED ENTITY GROUPING")
print("="*80)

# Extract structured data
data = parser.extract_structured_data(test_resume, confidence_threshold=0.6)

# Print results
parser.print_structured_output(data)

# Show detailed grouping
print("\n" + "="*80)
print("DETAILED ANALYSIS")
print("="*80)

print(f"\n✅ Person Name: {data['person_name']}")
print(f"\n✅ Total Work Experiences Found: {len(data['work_experience'])}")

for i, exp in enumerate(data['work_experience'], 1):
    print(f"\n  Job #{i}:")
    print(f"    Role: {exp['role']}")
    print(f"    Company: {exp['company']}")
    print(f"    Location: {exp['location']}")
    print(f"    Client: {exp['client']}")
    print(f"    Dates: {exp['start_date']} to {exp['end_date']}")

print(f"\n✅ Total Education Entries Found: {len(data['education'])}")

for i, edu in enumerate(data['education'], 1):
    print(f"\n  Education #{i}:")
    print(f"    Degree: {edu['degree']}")
    print(f"    Institution: {edu['institution']}")

print("\n" + "="*80)
print("✅ Proximity-based grouping ensures entities that appear close together")
print("   in the text are grouped into the same job/education entry!")
print("="*80)
