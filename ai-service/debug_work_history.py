#!/usr/bin/env python3
"""
Debug script to test work_history extraction
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from parsers.master_parser import MasterParser

def test_work_history_extraction():
    """Test work history extraction with candidate data"""
    
    # Use the actual data from your candidate
    text = """Sai Bhargav Garikapati
Email: bhargavg115@gmail.com
Phone: 1 (919) 439-9350

WORK EXPERIENCE
Senior Data Engineer
Home Depot
Atlanta, GA
March 2023 - Present

Environment: Python, Java, SQL, Hadoop, HDFS, MapReduce, Hive, Spark, Snowflake, Apache NiFi, Great Expectations, Apache Ranger, ERStudio, Apache Airflow, Apache Flink, Apache Kafka Streams, Collibra, dbt, Docker

- Designed multi-account AWS landing zone
- Implemented secure VPC peering and network segmentation
- Designed Kubernetes (EKS) clusters for container workloads

SKILLS
AWS, Agile, Amazon Redshift, Apache Flink, Apache HTTP Server, Apache Hive, Apache Kafka, Apache Spark, Azure, BigQuery, Cassandra, Confluence, Databricks, Django, Docker, DynamoDB, Flask, GCP, GitHub, HBase, HTML, Hadoop, JavaScript, Jenkins, Kubernetes, Matplotlib, MongoDB, NumPy, Pandas, PostgreSQL, Power BI, Python, SQL, Scala, Scikit-learn, Scrum, Seaborn, Spring Boot, Tableau

EDUCATION
Master of Science in Cloud Computing
University of Texas at Dallas
2015 - 2017"""

    parser = MasterParser()
    result = parser.parse_text(text, '8e835123-8e5e-4ceb-baab-bd825816f446')

    print('=== AI SERVICE RESULTS ===')
    print(f'Status: {result.get("status")}')
    print(f'Work Experience: {len(result.get("work_experience", []))} entries')
    print(f'Work History: {len(result.get("work_history", []))} entries')
    print(f'Education: {len(result.get("education", []))} entries')
    print(f'Skills: {len(result.get("skills", []))} entries')

    if result.get('work_experience'):
        print('\nWork Experience Details:')
        for i, exp in enumerate(result.get('work_experience', []), 1):
            print(f'  {i}. {exp.get("job_title", "N/A")} at {exp.get("company_name", "N/A")}')
            print(f'     Dates: {exp.get("start_date", "N/A")} - {exp.get("end_date", "N/A")}')

    if result.get('work_history'):
        print('\nWork History Details:')
        for i, exp in enumerate(result.get('work_history', []), 1):
            print(f'  {i}. {exp.get("job_title", "N/A")} at {exp.get("company_name", "N/A")}')
            print(f'     Dates: {exp.get("start_date", "N/A")} - {exp.get("end_date", "N/A")}')

    if result.get('education'):
        print('\nEducation Details:')
        for i, edu in enumerate(result.get('education', []), 1):
            print(f'  {i}. {edu.get("degree", "N/A")} at {edu.get("institution_name", "N/A")}')
            print(f'     Dates: {edu.get("start_date", "N/A")} - {edu.get("end_date", "N/A")}')

    print('\n=== FULL RESULT KEYS ===')
    for key in result.keys():
        print(f'{key}: {type(result[key])} - {len(str(result[key]))} chars')

    return result

if __name__ == "__main__":
    test_work_history_extraction()
