#!/usr/bin/env python3
"""
Quick test script for Priya's resume
"""

from resume_parser_pipeline import parse_resume

resume_text = """Priya Nair Venkataraman
LinkedIn | +1 (512)-338-9017 | priya.nair.data@gmail.com
PROFESSIONAL SUMMARY
Designed and optimized enterprise-scale data warehouses using Azure Synapse Analytics, Azure SQL Database, and Databricks, implementing complex ETL workflows through Azure Data Factory, dbt, and SSIS to deliver clean, reliable data pipelines supporting business intelligence across healthcare and financial services domains.
TECHNICAL SKILLS
ETL ELT Azure Data Factory dbt SSIS Informatica PowerCenter Talend AWS Glue Apache NiFi
Databases Azure SQL Database MS SQL Server Oracle PostgreSQL MySQL
Cloud Azure AWS GCP
PROFESSIONAL EXPERIENCE
Client UnitedHealth Group
Role SR Data Engineer
Duration March 2023 to Current
Designed and implemented end-to-end ELT pipelines using Python PySpark and Apache Spark ingesting large scale claims and member data from Azure Data Lake Gen2 into Azure Synapse Analytics.
Client American Airlines
Role SR Data Engineer
Duration August 2020 to February 2023
Designed scalable ETL pipelines using AWS Glue PySpark and Apache Spark ingesting flight operations data into AWS Redshift and Databricks.
Client FedEx Ground
Role Data Engineer
Duration November 2017 to July 2020
Designed and maintained ETL pipelines using Informatica PowerCenter and SSIS.
Client Cigna Healthcare
Role Data Engineer Migration Specialist
Duration February 2016 to October 2017
Developed claims data integration platform on AWS.
Client Wipro Technologies
Role ETL Developer
Duration June 2014 to January 2016
Developed ETL pipelines using Informatica PowerCenter and SSIS.
EDUCATION
Master of Science Data Science and Analytics University of Texas at Austin August 2012 to May 2014
Bachelor of Engineering Information Technology PSG College of Technology June 2008 to May 2012
"""

print("="*80)
print("🧪 TESTING PRIYA'S RESUME")
print("="*80)
print(f"\n📄 Resume Length: {len(resume_text)} characters\n")

result = parse_resume(resume_text)

print("="*80)
print("🏢 WORK EXPERIENCE EXTRACTED:")
print("="*80)

for i, exp in enumerate(result['experience'], 1):
    print(f"\n📌 Experience #{i}:")
    print(f"   Company:      {exp['company']}")
    print(f"   Role:         {exp['role']}")
    print(f"   Location:     {exp['location']}")
    print(f"   Start Date:   {exp['start_date']}")
    print(f"   End Date:     {exp['end_date']}")

print("\n" + "="*80)
print("🎓 EDUCATION EXTRACTED:")
print("="*80)

for i, edu in enumerate(result['education'], 1):
    print(f"\n📌 Education #{i}:")
    print(f"   Degree:       {edu['degree']}")
    print(f"   Institution:  {edu['institution']}")
    print(f"   Start Date:   {edu['start_date']}")
    print(f"   End Date:     {edu['end_date']}")

print("\n" + "="*80)
print("📊 SUMMARY:")
print("="*80)
print(f"✅ Work Experience: {len(result['experience'])} entries")
print(f"✅ Education: {len(result['education'])} entries")
print("="*80)
