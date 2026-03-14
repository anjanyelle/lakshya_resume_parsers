from backend.app.services.parser.work_experience_parser import WorkExperienceParser
import logging

# Configure logging to see what's happening
logging.basicConfig(level=logging.DEBUG)

def debug_mixed_format():
    text = "\n".join(
        [
            "Work history",
            "+1 (404)-445-8754 ╖ Linkedin",
            "— → —",
            "Processed and transformed large-scale data using Snowflake, SnowSQL, and Snowpipe",
            "Computer Science ╖ Bachelor of Technology (BTech)",
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
    print("\n--- Debugging Mixed Format Case ---")
    jobs = parser.parse_experience_section(text)
    print(f"Jobs found: {len(jobs)}")
    for i, job in enumerate(jobs):
        print(f"Job {i}: Company: {job.company}, Title: {job.title}, Confidence: {job.confidence}")

def debug_table_format():
    text = "\n".join(
        [
            "Acme Corp | Software Engineer | Jan 2020 - Dec 2022 | NYC",
            "Beta Ltd  | Senior Dev       | 2018 - 2020         | LA",
        ]
    )
    parser = WorkExperienceParser()
    print("\n--- Debugging Table Format Case ---")
    jobs = parser.parse_experience_section(text)
    print(f"Jobs found: {len(jobs)}")
    for i, job in enumerate(jobs):
        print(f"Job {i}: Company: {job.company}, Title: {job.title}, Confidence: {job.confidence}")

if __name__ == "__main__":
    debug_mixed_format()
    debug_table_format()
