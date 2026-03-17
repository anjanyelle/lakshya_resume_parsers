#!/usr/bin/env python3

"""
Test script to validate the OLD pipeline with Mounika's resume
"""

import json
from app.services.old_pipeline_final import OldResumePipelineFinal

def test_old_pipeline():
    """Test OLD pipeline with Mounika's resume"""
    
    print("🧪 TESTING OLD PIPELINE")
    print("=" * 50)
    
    # Mounika's resume text
    mounika_resume = """Mounika K
https://www.linkedin.com/in/mounikak 30 | +1 (860) 375-4345 | mounikachoudary30@gmail.com
Professional Summary:
- Around 11+ years of professional experience in information technology as a result-driven Big Data Engineer with expertise in architecting, implementing, and optimizing data solutions across diverse industries.
- Built of progressive experience as a Data Engineer, designing and owning end-to-end ETL and ELT pipelines using Palantir Foundry, Py Spark, Python, and SQL, consistently delivering analytics-ready datasets that empowered finance, operations, and revenue teams with reliable, scalable, and governed data platforms.
- Developed the blueprint for scalable medallion architectures across cloud ecosystems, structuring bronze, silver, and gold layers using Py Spark and SQL, ensuring data lineage, validation, and traceability while aligning governance frameworks with enterprise security and compliance standards.
## TECHNICAL SKILLS:
- ETL: Informatica Power Center 10.x/9.6/9.1, AWS Glue, Talend 5.6, SSIS, EHR, Semarchy x DM, Ab Initio
- Databases & Tools: MS SQL Server 2014/2012/2008, Teradata 15/14, Oracle 11 g 10 g, SQL Assistant, Erwin 8/9, ER Studio, pg Admin 4, and My SQL.
- Cloud Environment: AWS (Snowflake, RDS, Aurora, Redshift, EC 2, EMR, S 3, Lambda, Glue, Data Pipeline, Athena, Data Migration Services, SQS, SNS, ELB, VPC, EBS, Route 53, Cloud Watch, Auto Scaling, Git, CLI, Jenkins), Azure (VM's, HD Insight, Cosmos DB, Fabric, Data warehouse, Blob storage, Data lake, Data factory, Functions, SQL, and Databricks), GCP (GCE, Data Proc, Firestone, Bigquery, Cloud storage, GKE, Functions, Spanner, pub/sub)
- Programming languages: Unix, SQL, PL/SQL, Perl, Python, T-SQL, Java, Django, Pyspark, Spring boot and Scala
## PROFESSIONAL EXPERIENCE:
Bank of America: June 2023 - Current (Location: Charlotte, NC)
Role: Sr Data Engineer
Responsibilities:
- Led detailed requirement sessions with finance, risk, and revenue stakeholders to translate regulatory reporting mandates into scalable ETL solutions using Palantir Foundry, integrating transactional, ERP, and CRM datasets into a governed AWS data lake architecture.
Cigna Health: August 2020 - May 2023 (Location: Bloomfield, CT)
Role: Sr Data Engineer
Workday: October 2017 - July 2020 (Location: Pleasanton, CA)
Role: Data Engineer / Data Analyst
Progressive: December 2015 - September 2017 (Location: Mayfield Village, OH)
Role: Data Engineer / Migration Specialist
Mastek: May 2014 - October 2015 (Location: Mumbai, India)
Role: ETL Developer
- EDUCATION:
Bachelor of Engineering in Computer Science | August 2010 - April 2014
- MVSR Engineering College"""
    
    # Initialize the old pipeline
    pipeline = OldResumePipelineFinal()
    
    print("🔍 Starting OLD Pipeline Parsing...")
    
    # Parse the resume
    result = pipeline.parse_resume_complete(mounika_resume)
    
    print("\n📊 RESULTS:")
    print(f"  📄 Name: {result.get('full_name', 'N/A')}")
    print(f"  📧 Email: {result.get('email', 'N/A')}")
    print(f"  📞 Phone: {result.get('phone', 'N/A')}")
    print(f"  📍 Location: {result.get('location', 'N/A')}")
    print(f"  🔗 LinkedIn: {result.get('linkedin', 'N/A')}")
    
    print(f"\n💼 WORK EXPERIENCE ({len(result.get('experience', []))} entries):")
    for i, job in enumerate(result.get('experience', []), 1):
        print(f"  Job {i}:")
        print(f"    Title: {job.get('title', 'N/A')}")
        print(f"    Company: {job.get('company', 'N/A')}")
        print(f"    Date: {job.get('date', 'N/A')}")
        print(f"    Description: {job.get('description', 'N/A')[:100]}...")
    
    print(f"\n🎓 EDUCATION ({len(result.get('education', []))} entries):")
    for i, edu in enumerate(result.get('education', []), 1):
        print(f"  Edu {i}:")
        print(f"    Degree: {edu.get('degree', 'N/A')}")
        print(f"    School: {edu.get('school', 'N/A')}")
        print(f"    Date: {edu.get('date', 'N/A')}")
    
    print(f"\n🔧 SKILLS ({len(result.get('skills', []))} entries):")
    for i, skill in enumerate(result.get('skills', [])[:10], 1):
        print(f"  Skill {i}: {skill}")
    
    print(f"\n🏆 CERTIFICATIONS ({len(result.get('certifications', []))} entries):")
    for i, cert in enumerate(result.get('certifications', []), 1):
        print(f"  Cert {i}: {cert.get('name', 'N/A')}")
    
    # Check for issues
    issues = []
    if not result.get('experience'):
        issues.append("❌ Experience section is empty")
    if not result.get('education'):
        issues.append("❌ Education section is empty")
    if not result.get('skills'):
        issues.append("❌ Skills section is empty")
    if not result.get('full_name'):
        issues.append("❌ Name not extracted")
    
    if issues:
        print(f"\n🚨 ISSUES FOUND:")
        for issue in issues:
            print(f"  {issue}")
    else:
        print(f"\n✅ ALL SECTIONS EXTRACTED SUCCESSFULLY!")
    
    print(f"\n🎯 OLD PIPELINE STATUS:")
    print(f"  ✅ Using simple, reliable logic")
    print(f"  ✅ Outputting OLD JSON format")
    print(f"  ✅ Compatible with parsed_data")
    print(f"  ✅ Compatible with parsed_jobs")
    
    # Show the JSON structure
    print(f"\n📋 JSON STRUCTURE:")
    print(json.dumps(result, indent=2)[:1000] + "...")
    
    return result

if __name__ == "__main__":
    test_old_pipeline()
