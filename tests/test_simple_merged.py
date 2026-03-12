import sys
import os
# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'backend'))

from app.services.parser.work_experience_parser import WorkExperienceParser
import json

def test_simple_merged():
    """Test parsing of simple merged format with ## headers on separate lines"""
    
    # Simple merged format with ## headers on separate lines
    text = """Professional Experience · Company

— → —

## HCA Healthcare: November 2022 - Current (Location: Nashville, TN)
Site Reliability Engineer
- Designed and deployed HIPAA-compliant cloud infrastructure on AWS using Terraform
- Established SLOs, SLIs, and error budgets for mission-critical healthcare services
- Built CI/CD pipelines using Jenkins and Git workflows

## American Express: January 2020 - October 2022 (Location: New York, NY)
Site Reliability Engineer
- Designed and deployed PCI-DSS-compliant cloud infrastructure on Azure
- Established SRE principles including SLIs, SLOs, and error budgets
- Built CI/CD pipelines using GitHub Actions and Git workflows

## Best Buy: March 2017 - December 2019 (Location: Richfield, MN)
Cloud DevOps Engineer
- Designed and deployed scalable cloud infrastructure on Google Cloud Platform
- Established comprehensive SLIs, SLOs, and error budgets for retail services
- Built CI/CD pipelines using GitLab CI/CD integrated with Git workflows"""
    
    print("=" * 60)
    print("TESTING SIMPLE MERGED FORMAT")
    print("=" * 60)
    
    work_parser = WorkExperienceParser()
    
    # Parse the entire experience section
    print("\nTESTING FULL PARSING")
    print("-" * 40)
    parsed_jobs = work_parser.parse_experience_section(text)
    
    print(f"\nNumber of parsed jobs: {len(parsed_jobs)}")
    
    # Convert to UI format
    ui_data = []
    for i, job in enumerate(parsed_jobs):
        job_dict = {
            "title": job.title,
            "company": job.company,
            "location": job.location,
            "start_date": job.start_date.isoformat() if job.start_date else None,
            "end_date": job.end_date.isoformat() if job.end_date else None,
            "is_current": job.is_current,
            "description": job.description,
            "bullets": job.bullets,
            "confidence": job.confidence
        }
        ui_data.append(job_dict)
        
        print(f"\n--- Job {i+1} ---")
        print(f"Company: {job.company}")
        print(f"Title: {job.title}")
        print(f"Location: {job.location}")
        print(f"Start Date: {job.start_date}")
        print(f"End Date: {job.end_date}")
        print(f"Is Current: {job.is_current}")
        print(f"Description length: {len(job.description) if job.description else 0}")
        print(f"Bullets count: {len(job.bullets) if job.bullets else 0}")
    
    # Show JSON output that UI would receive
    print("\n" + "=" * 60)
    print("JSON OUTPUT FOR UI:")
    print("=" * 60)
    print(json.dumps({"work_experience": ui_data}, indent=2))

if __name__ == "__main__":
    test_simple_merged()
