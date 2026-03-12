import sys
import os
# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'backend'))

from app.services.parser.work_experience_parser import WorkExperienceParser

def test_chandra_shyam_parsing():
    """Test parsing of Chandra Shyam's resume format"""
    
    # Sample text from Chandra Shyam's resume
    text = """
PROFESSIONAL EXPERIENCE:

Company: Microsoft
January 2020 – Present (Location: Redmond, WA)
Role: Senior Software Engineer
Responsibilities:
• Led development of cloud-native microservices using Azure Kubernetes Service
• Implemented CI/CD pipelines using Azure DevOps and GitHub Actions
• Mentored junior developers and conducted code reviews

Company: Amazon Web Services
June 2018 – December 2019 (Location: Seattle, WA)
Role: Software Development Engineer
Responsibilities:
• Developed scalable solutions for AWS EC2 instances
• Worked on infrastructure as code using Terraform
• Collaborated with cross-functional teams to deliver features
"""
    
    print("=" * 60)
    print("TESTING CHANDRA SHYAM RESUME PARSING")
    print("=" * 60)
    
    work_parser = WorkExperienceParser()
    
    # Parse the entire experience section
    print("\nTESTING FULL PARSING")
    print("-" * 40)
    parsed_jobs = work_parser.parse_experience_section(text)
    
    print(f"\nNumber of parsed jobs: {len(parsed_jobs)}")
    for i, job in enumerate(parsed_jobs):
        print(f"\n--- Parsed Job {i+1} ---")
        print(f"Company: {job.company}")
        print(f"Title: {job.title}")
        print(f"Location: {job.location}")
        print(f"Start Date: {job.start_date}")
        print(f"End Date: {job.end_date}")
        print(f"Is Current: {job.is_current}")
        print(f"Description length: {len(job.description) if job.description else 0}")
        print(f"Bullets count: {len(job.bullets) if job.bullets else 0}")
        if job.bullets:
            print(f"First bullet: {job.bullets[0][:100]}...")

if __name__ == "__main__":
    test_chandra_shyam_parsing()
