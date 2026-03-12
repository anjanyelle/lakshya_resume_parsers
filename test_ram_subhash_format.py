import sys
sys.path.append('backend')
from app.services.parser.work_experience_parser import WorkExperienceParser

# Test with Ram Subhash's resume format
text = '''## PROFESSIONAL EXPERIENCE:
Client: State Farm                    Location: Bloomington, IL
Role: SR. BIG DATA ENGINEER          October 2022 – Current
Responsibilities:
•	Designed and implemented end-to-end ETL pipelines using Python, PySpark, and Apache Spark, ingesting large-scale data from AWS S3 into Snowflake.
•	Managed real-time data streaming workflows by integrating Apache Kafka and Apache Pulsar with Snowflake Streams and Snowpipe.
Environment: Python, PySpark, Apache Spark, AWS S3, Snowflake, Pandas, NumPy

Client: Delta Airlines                                                                                                                                      Location: Atlanta, GA
Role: SR DATA ENGINEER                                                                                                           December 2019 – September 2022
Responsibilities:
•	Designed and implemented scalable ETL pipelines using Snowflake, Snowpipe, SnowSQL, and Fivetran.
•	Developed modular transformation workflows with dbt, leveraging Snowflake Tasks and Streams.
Environment: Snowflake, Snowpipe, SnowSQL, Fivetran, dbt, Snowflake Tasks

Client: UPS                                                                                                                                                  Location: Atlanta, GA  
Role: DATA ENGINEER / DATA  ANALYST                                                                              February 2017 – November 2019
Responsibilities:
•	Designed and implemented scalable ETL pipelines using Snowflake, SnowSQL, Snowpipe, and Talend.
•	Developed modular data transformation workflows with dbt, leveraging Snowflake Tasks and Streams.
Environment: Snowflake, SnowSQL, Snowpipe, Talend, dbt, Snowflake Tasks

EDUCATION:
Bachelor of Technology (BTech) | Computer Science | Amrita Vishwa Vidyapeetham | Kerala,India | August 2010 - March 2014'''

parser = WorkExperienceParser()
jobs = parser.parse_experience_section(text, source_format=None)

print(f"=== RAM SUBHASH FORMAT TEST ===")
print(f"Total jobs parsed: {len(jobs)}")

for i, job in enumerate(jobs, 1):
    print(f"\n--- JOB {i} ---")
    print(f"Company: {job.company}")
    print(f"Title: {job.title}")
    print(f"Location: {job.location}")
    print(f"Start: {job.start_date}")
    print(f"End: {job.end_date}")
    print(f"Current: {job.is_current}")
    print(f"Bullets count: {len(job.bullets) if job.bullets else 0}")
    print(f"Description length: {len(job.description) if job.description else 0}")
    if job.bullets:
        print(f"First bullet: {job.bullets[0][:80]}...")

print(f"\n=== EXPECTED RESULTS ===")
print("✅ Should extract 3 jobs:")
print("  1. State Farm - SR. BIG DATA ENGINEER (Bloomington, IL) - Oct 2022 - Current")
print("  2. Delta Airlines - SR DATA ENGINEER (Atlanta, GA) - Dec 2019 - Sep 2022")  
print("  3. UPS - DATA ENGINEER / DATA ANALYST (Atlanta, GA) - Feb 2017 - Nov 2019")
print("✅ Education section should be excluded")
print("✅ All bullets should be captured")
