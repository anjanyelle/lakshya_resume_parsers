from app.services.parser.work_experience_parser import WorkExperienceParser
import sys

print("DEBUG START")
text = "\n".join(
    [
        "Work history",
        "+1 (404)-445-8754 · Linkedin",
        "— → —",
        "Processed and transformed large-scale data using Snowflake, SnowSQL, and Snowpipe",
        "Computer Science · Bachelor of Technology (BTech)",
        "2010-08-01 → 2014-03-01",
        "Salesforce Certified Sales Cloud Consultant",
        "Marketo Certified Solutions Architect (MCSA)",
        "Acme Corp - Data Engineer",
        "Jan 2020 - Dec 2021",
        "- Built ETL pipelines",
        "- Improved data quality",
    ]
)

parser = WorkExperienceParser()
print("Parser initialized")
jobs = parser.parse_experience_section(text)
print(f"Found {len(jobs)} jobs")

for job in jobs:
    print(f"Company: {job.company}")
    print(f"Title: {job.title}")
    print(f"Dates: {job.start_date} - {job.end_date}")
    print("-" * 20)
print("DEBUG END")
