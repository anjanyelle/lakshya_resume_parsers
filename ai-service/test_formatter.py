"""
Test script for Resume Text Formatter

This script demonstrates how to use the resume formatter to clean
and structure raw resume text before NER processing.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from parsers.resume_formatter import ResumeTextFormatter


def test_rule_based_formatting():
    """Test rule-based formatting without LLM."""
    
    # Sample raw resume text (messy OCR output)
    raw_text = """
John Doe
john.doe@email.com | (555) 123-4567 | New York, NY
EXPERIENCE
Software Engineer at Tech Corp Jan 2020 - Present
• Developed microservices using Python and FastAPI
• Led team of 5 engineers
Senior Developer at StartupXYZ Jun 2018 - Dec 2019
• Built REST APIs
• Implemented CI/CD pipelines
EDUCATION
Master of Science in Computer Science
Stanford University 2016-2018
Bachelor of Technology in Computer Engineering
MIT 2012-2016
SKILLS
Python, Java, JavaScript, React, Node.js, Docker, Kubernetes, AWS
"""
    
    formatter = ResumeTextFormatter(llm_client=None)
    formatted_text = formatter.format_resume_text(raw_text)
    
    print("=" * 80)
    print("RULE-BASED FORMATTING TEST")
    print("=" * 80)
    print("\n--- RAW TEXT ---")
    print(raw_text)
    print("\n--- FORMATTED TEXT ---")
    print(formatted_text)
    print("\n" + "=" * 80)


def test_with_messy_text():
    """Test with very messy text."""
    
    messy_text = """
JANE SMITH
Email: jane.smith@example.com Phone: +1-555-987-6543 Location: San Francisco, CA LinkedIn: linkedin.com/in/janesmith GitHub: github.com/janesmith

PROFESSIONAL SUMMARY Senior Data Engineer with 6+ years experience building scalable data pipelines big data solutions cloud platforms strong experience in spark kafka aws gcp leading teams delivering high performance systems

PROFESSIONAL EXPERIENCE Senior Data Engineer BigData Inc. March 2021 - Present • Designed and implemented large-scale data pipelines processing over 10TB daily using Spark and Kafka • Improved data processing performance by 40% through optimization techniques • Worked closely with cross-functional teams to define data strategies • Mentored junior engineers and conducted code reviews • Built real-time streaming systems using Kafka and Spark Streaming • Developed data lake solutions using AWS S3 and EMR Data Engineer DataCorp May 2019 - Feb 2021 • Built ETL pipelines using Airflow and Python • Integrated data from multiple sources including APIs and databases • Worked with PostgreSQL MongoDB Redshift • Improved ETL performance by 25% • Collaborated with data scientists for model deployment Junior Data Analyst Insight Analytics Jan 2017 - Apr 2019 • Developed SQL queries for reporting • Created dashboards using Tableau and Power BI • Performed data cleaning and preprocessing • Supported analytics team in generating business insights

EDUCATION Master of Science in Data Science University of California Berkeley 2017-2019 GPA: 3.9/4.0 Bachelor of Science in Computer Science UCLA 2013-2017 GPA: 3.7/4.0

TECHNICAL SKILLS Programming: Python Scala SQL Java Big Data: Spark Hadoop Kafka Airflow Cloud Platforms: AWS S3 EMR Redshift Lambda GCP BigQuery Compute Engine Databases: PostgreSQL MongoDB Cassandra MySQL Tools: Git Docker Kubernetes Jenkins Tableau Power BI

PROJECTS Real-Time Fraud Detection System • Built streaming pipeline using Kafka Spark Streaming • Processed millions of transactions per day • Reduced fraud detection latency by 50% Data Warehouse Migration • Migrated on-premise warehouse to AWS Redshift • Optimized queries and reduced cost by 30%

CERTIFICATIONS AWS Certified Solutions Architect Google Cloud Professional Data Engineer

ADDITIONAL EXPERIENCE Freelance Data Consultant 2020-2021 • Worked with startups on data engineering solutions • Designed scalable architectures • Built analytics dashboards

PUBLICATIONS "Scalable Data Pipelines in Cloud Environments" Published in Data Engineering Journal 2020

------------------------------------------------------------

PAGE 2

WORK EXPERIENCE CONTINUED Lead Data Engineer CloudTech Solutions Jan 2022 - Present Led team of 8 engineers built microservices data pipelines optimized big data workflows implemented CI/CD pipelines using Jenkins docker kubernetes improved system reliability designed architecture for high availability systems worked with stakeholders defined requirements

Senior Data Engineer BigData Inc continued • Automated deployment pipelines • Designed monitoring systems using Prometheus and Grafana • Ensured data quality and validation frameworks • Integrated machine learning pipelines

EDUCATION CONTINUED Certifications Coursera Deep Learning Specialization Udacity Data Engineering Nanodegree

SKILLS CONTINUED Machine Learning basics NLP TensorFlow PyTorch Data Visualization advanced Tableau dashboards

------------------------------------------------------------

PAGE 3

OTHER EXPERIENCE Volunteer Data Engineer NGO Analytics Project Built dashboards for NGO reporting system improved transparency worked with non technical teams

INTERNSHIP Data Intern TechStart 2016 Built small ETL pipelines worked on SQL queries supported senior engineers

ACHIEVEMENTS Employee of the Year BigData Inc 2022 Best Innovation Award DataCorp 2020

LANGUAGES English Fluent Spanish Intermediate

INTERESTS Hiking Traveling Blogging Technology Writing

------------------------------------------------------------

PAGE 4

RANDOM OCR MIXED TEXT (SIMULATING BAD EXTRACTION)
Data Engineer BigData Inc March 2021 Present Designed pipelines Spark Kafka AWS S3 EMR Lambda GCP BigQuery improved perf 40 percent mentored team built streaming system DataCorp May 2019 Feb 2021 ETL Airflow Python PostgreSQL MongoDB Tableau PowerBI education ms data science berkeley bsc cs ucla skills python scala sql java aws gcp docker kubernetes random words mixed lines broken format continues here without proper structure experience education mixed together

END OF RESUME
"""
    
 

    formatter = ResumeTextFormatter(llm_client=None)
    formatted_text = formatter.format_resume_text(messy_text)
    
    print("=" * 80)
    print("MESSY TEXT FORMATTING TEST")
    print("=" * 80)
    print("\n--- RAW MESSY TEXT ---")
    print(messy_text)
    print("\n--- FORMATTED TEXT ---")
    print(formatted_text)
    print("\n" + "=" * 80)


def main():
    """Run all tests."""
    print("\n🧪 Testing Resume Text Formatter\n")
    
    test_rule_based_formatting()
    print("\n")
    test_with_messy_text()
    
    print("\n✅ All tests completed!")
    print("\nNOTE: For LLM-based formatting, you need to provide an LLM client.")
    print("Example:")
    print("  formatter = ResumeTextFormatter(llm_client=your_llm_client)")
    print("  formatted = formatter.format_resume_text(raw_text)")


if __name__ == "__main__":
    main()
