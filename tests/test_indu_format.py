"""
Test script for Indu's resume format - Client: Company, City, State
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.services.parser.work_experience_parser import WorkExperienceParser

def test_indu_format():
    """Test Indu's resume format parsing"""
    
    # Sample text from Indu's resume
    indu_resume_text = """
Client: TransUnion, Chicago, IL
Role: DevOps Engineer
Responsibilities:
• Designed and managed cloud solutions across AWS and Azure platforms for credit reporting and financial services. Successfully deployed secure and scalable applications using critical services including AWS EC2, S3, RDS, Azure Virtual Machines, Blob Storage, and Azure SQL Database.
• Enhanced Software Development Life Cycle (SDLC) by implementing integration with Jenkins, GitHub Actions, and Azure DevOps for CI/CD pipelines. Automated build and deployment processes for financial data processing applications, reducing release cycles by 25%.

Client: Change Healthcare, Hyderabad, India
Role: Linux Administration / System Engineer
Responsibilities:
• Administered and automated Linux/Unix environments, specifically Red Hat Enterprise Linux (RHEL), using Bash and Python scripts to enhance operational efficiency of healthcare data processing systems by 25%.
• Managed complex system configurations, including Logical Volume Management (LVM) setups, to optimize storage and backup processes for large-scale healthcare datasets.

EDUCATION
Bachelor of Technology in Computer Science
QIS College of Engineering, Andhra Pradesh, India.
"""
    
    parser = WorkExperienceParser()
    
    print("🧪 Testing Indu's Resume Format")
    print("=" * 50)
    
    # Test format detection
    detected_format = parser.detect_format(indu_resume_text)
    print(f"📋 Detected Format: {detected_format}")
    
    # Test job extraction
    jobs = parser.extract_individual_jobs(indu_resume_text)
    print(f"📊 Jobs Found: {len(jobs)}")
    
    for i, job in enumerate(jobs, 1):
        print(f"\n🏢 Job {i}:")
        print(f"   Text: {job[:100]}...")
        
        # Parse the job
        job_entry = parser.parse_experience_section(job)
        if job_entry:
            print(f"   ✅ Company: {job_entry[0].company if job_entry else 'N/A'}")
            print(f"   ✅ Title: {job_entry[0].title if job_entry else 'N/A'}")
            print(f"   ✅ Location: {job_entry[0].location if job_entry else 'N/A'}")
            print(f"   ✅ Start: {job_entry[0].start_date if job_entry else 'N/A'}")
            print(f"   ✅ End: {job_entry[0].end_date if job_entry else 'N/A'}")
            print(f"   ✅ Current: {job_entry[0].is_current if job_entry else 'N/A'}")
        else:
            print(f"   ❌ Failed to parse job")
    
    print(f"\n🎯 Test Complete!")
    return jobs

if __name__ == "__main__":
    test_indu_format()
