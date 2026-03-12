import sys
sys.path.append('backend')
from app.services.parser.work_experience_parser import WorkExperienceParser

# Test the parser with the resume text
text = '''## OBSIDIAN SHIELD DEFENSE | Seattle, WA
Director of Global Security Operations February 2021 - Present
Lead the global security strategy for a premier Managed Security Service Provider (MSSP) protecting over 50 enterprise clients in the aerospace and defense sectors.

## AETHER BIOTECH SOLUTIONS | San Francisco, CA
Head of Information Security (CISO Delegate) August 2017 - January 2021
Directed the security posture for a publicly traded biotechnology firm specializing in genomic research.

## PACIFIC NORTH POWER | Portland, OR
Senior Security Engineer (ICS/SCADA) May 2015 - July 2017
Served as the lead security engineer for a regional energy utility.

## VERTEX FINANCIAL SYSTEMS | Chicago, IL
Security Analyst / SOC Lead June 2013 - April 2015
Started as a Level 1 analyst and rapidly progressed to Shift Lead.'''

parser = WorkExperienceParser()
jobs = parser.parse_experience_section(text)
print(f'Found {len(jobs)} jobs:')
for i, job in enumerate(jobs):
    print(f'Job {i+1}: {job.company} - {job.title} ({job.start_date} to {job.end_date})')
