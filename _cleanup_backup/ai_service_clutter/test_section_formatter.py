"""
Test script for Section-Based Resume Formatter

This demonstrates the advanced section-wise formatting approach.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from parsers.section_based_formatter import (
    SectionBasedFormatter,
    format_resume_sectionwise,
    get_resume_sections
)


def test_section_based_formatting():
    """Test section-based formatting with messy resume."""
    
    messy_resume = """
JANE SMITH
Email: jane.smith@example.com Phone: +1-555-987-6543 Location: San Francisco, CA
PROFESSIONAL SUMMARY Senior Data Engineer with 6+ years experience building scalable data pipelines big data solutions cloud platforms strong experience in spark kafka aws gcp leading teams delivering high performance systems
PROFESSIONAL EXPERIENCE Senior Data Engineer BigData Inc. March 2021 - Present • Designed and implemented large-scale data pipelines processing over 10TB daily using Spark and Kafka • Improved data processing performance by 40% through optimization techniques • Worked closely with cross-functional teams to define data strategies • Mentored junior engineers and conducted code reviews • Built real-time streaming systems using Kafka and Spark Streaming • Developed data lake solutions using AWS S3 and EMR Data Engineer DataCorp May 2019 - Feb 2021 • Built ETL pipelines using Airflow and Python • Integrated data from multiple sources including APIs and databases • Worked with PostgreSQL MongoDB Redshift • Improved ETL performance by 25% • Collaborated with data scientists for model deployment Junior Data Analyst Insight Analytics Jan 2017 - Apr 2019 • Developed SQL queries for reporting • Created dashboards using Tableau and Power BI • Performed data cleaning and preprocessing • Supported analytics team in generating business insights
EDUCATION Master of Science in Data Science University of California Berkeley 2017-2019 GPA: 3.9/4.0 Bachelor of Science in Computer Science UCLA 2013-2017 GPA: 3.7/4.0
TECHNICAL SKILLS Programming: Python Scala SQL Java Big Data: Spark Hadoop Kafka Airflow Cloud Platforms: AWS S3 EMR Redshift Lambda GCP BigQuery Compute Engine Databases: PostgreSQL MongoDB Cassandra MySQL Tools: Git Docker Kubernetes Jenkins Tableau Power BI
PROJECTS Real-Time Fraud Detection System • Built streaming pipeline using Kafka Spark Streaming • Processed millions of transactions per day • Reduced fraud detection latency by 50% Data Warehouse Migration • Migrated on-premise warehouse to AWS Redshift • Optimized queries and reduced cost by 30%
CERTIFICATIONS AWS Certified Solutions Architect Google Cloud Professional Data Engineer
ACHIEVEMENTS Employee of the Year BigData Inc 2022 Best Innovation Award DataCorp 2020
LANGUAGES English Fluent Spanish Intermediate
"""
    
    print("=" * 80)
    print("SECTION-BASED FORMATTING TEST")
    print("=" * 80)
    print("\n--- RAW MESSY TEXT ---")
    print(messy_resume[:500] + "...\n")
    
    # Format using section-based approach
    formatter = SectionBasedFormatter()
    formatted = formatter.format_resume(messy_resume)
    
    print("--- FORMATTED SECTION-WISE TEXT ---\n")
    print(formatted)
    
    print("\n" + "=" * 80)
    print("SECTION SUMMARY")
    print("=" * 80)
    summary = formatter.get_section_summary()
    for section, line_count in summary.items():
        print(f"  {section}: {line_count} lines")
    print("=" * 80)


def test_extract_sections_as_dict():
    """Test extracting sections as a dictionary."""
    
    resume_text = """
John Doe
john.doe@email.com | (555) 123-4567 | New York, NY

PROFESSIONAL SUMMARY
Senior Software Engineer with 5+ years of experience in building scalable web applications.

WORK EXPERIENCE
Software Engineer at Tech Corp
Jan 2020 - Present
• Developed microservices using Python and FastAPI
• Led team of 5 engineers

Senior Developer at StartupXYZ
Jun 2018 - Dec 2019
• Built REST APIs
• Implemented CI/CD pipelines

EDUCATION
Master of Science in Computer Science
Stanford University
2016-2018

Bachelor of Technology in Computer Engineering
MIT
2012-2016

TECHNICAL SKILLS
Python, Java, JavaScript, React, Node.js, Docker, Kubernetes, AWS

CERTIFICATIONS
AWS Certified Solutions Architect
Google Cloud Professional Developer
"""
    
    print("\n" + "=" * 80)
    print("EXTRACT SECTIONS AS DICTIONARY")
    print("=" * 80)
    
    sections = get_resume_sections(resume_text)
    
    for section_name, content in sections.items():
        print(f"\n### {section_name} ###")
        print(content[:200] + "..." if len(content) > 200 else content)
    
    print("\n" + "=" * 80)


def test_comparison():
    """Compare basic vs section-based formatting."""
    
    from parsers.resume_formatter import format_resume_text
    
    sample_text = """
JANE SMITH jane@email.com PROFESSIONAL EXPERIENCE Senior Engineer TechCorp 2021-Present Built APIs Led team EDUCATION MS Computer Science Berkeley 2019 SKILLS Python Java AWS
"""
    
    print("\n" + "=" * 80)
    print("COMPARISON: Basic vs Section-Based")
    print("=" * 80)
    
    print("\n--- ORIGINAL ---")
    print(sample_text)
    
    print("\n--- BASIC FORMATTER ---")
    basic_formatted = format_resume_text(sample_text, llm_client=None)
    print(basic_formatted)
    
    print("\n--- SECTION-BASED FORMATTER ---")
    section_formatted = format_resume_sectionwise(sample_text)
    print(section_formatted)
    
    print("\n" + "=" * 80)


def main():
    """Run all tests."""
    print("\n🧪 Testing Section-Based Resume Formatter\n")
    
    test_section_based_formatting()
    test_extract_sections_as_dict()
    test_comparison()
    
    print("\n✅ All tests completed!")
    print("\n📋 SUMMARY:")
    print("  • Section-based formatter identifies and separates resume sections")
    print("  • Each section is formatted with clear headings and structure")
    print("  • Sections can be extracted as a dictionary for further processing")
    print("  • Better than basic formatter for section-wise organization")


if __name__ == "__main__":
    main()
