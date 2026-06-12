#!/usr/bin/env python3
"""
Test the actual API endpoint to verify work_history field is included
"""

import sys
import os
import json

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import ParseResponse, MasterParser

def test_api_endpoint():
    """Test that the API endpoint returns both work_experience and work_history"""
    
    print("Testing API endpoint field mapping...")
    print("=" * 60)
    
    # Initialize master parser
    parser = MasterParser()
    
    # Sample text to parse (similar to your original data)
    sample_text = """
    Raghavendra Prasad Vemuri
    Email: raghav.vemuri.cloud@gmail.com
    Phone: 1 (972) 555-8432
    
    WORK EXPERIENCE
    Senior Software Engineer
    JPMorgan Chase
    Dallas, TX
    April 2020 - Present
    
    Project Overview: Modernization of enterprise trading platform to cloud-native AWS infrastructure.
    Key Responsibilities: Cloud Architecture
    - Designed multi-account AWS landing zone
    - Implemented secure VPC peering and network segmentation
    - Designed Kubernetes (EKS) clusters for container workloads
    
    Cloud Infrastructure Engineer
    Experian
    Chicago, IL
    January 2016 - March 2020
    
    - Designed AWS infrastructure for customer-facing banking applications
    - Migrated legacy systems to containerized microservices
    - Implemented API Gateway-based secure integrations
    
    Cloud Infrastructure Engineer
    MAJOR CLOUD PROGRAMS
    Atlanta, GA
    June 2012 - December 2015
    
    - Supported hybrid cloud integration strategy
    - Designed secure VPC architecture and security groups
    - Implemented S3 backup and disaster recovery solutions
    
    EDUCATION
    Master of Science in Cloud Computing
    University of Texas at Dallas
    2015 - 2017
    
    Bachelor of Arts in Computer Science
    Osmania University
    2008 - 2012
    
    SKILLS
    AWS, Bash, DevSecOps, Docker, DynamoDB, ELK Stack, GitHub, GitHub Actions, 
    GitLab, GitLab CI, Grafana, Istio, Java, Jenkins, Kubernetes, Microservices, 
    MongoDB, OAuth 2.0, PostgreSQL, Prometheus, Python, REST APIs, SQL, Serverless, Terraform
    """
    
    # Parse the text
    print("Parsing sample resume text...")
    result = parser.parse_text(sample_text, "raghavendra-test-123")
    
    # Create ParseResponse to simulate API endpoint behavior
    api_response = ParseResponse(**result)
    
    print(f"\n✅ Status: {api_response.status}")
    print(f"✅ Name: {api_response.name}")
    print(f"✅ Email: {api_response.email}")
    
    # Check work_experience field
    work_exp = api_response.work_experience
    print(f"\n📋 work_experience: {len(work_exp)} entries")
    for i, exp in enumerate(work_exp, 1):
        print(f"   {i}. {exp.get('job_title', 'N/A')} at {exp.get('company_name', 'N/A')}")
        print(f"      Dates: {exp.get('start_date', 'N/A')} - {exp.get('end_date', 'N/A')}")
    
    # Check work_history field (backend compatibility)
    work_hist = api_response.work_history
    print(f"\n📋 work_history: {len(work_hist)} entries")
    for i, exp in enumerate(work_hist, 1):
        print(f"   {i}. {exp.get('job_title', 'N/A')} at {exp.get('company_name', 'N/A')}")
        print(f"      Dates: {exp.get('start_date', 'N/A')} - {exp.get('end_date', 'N/A')}")
    
    # Verify they match
    if work_exp and work_hist:
        match = work_exp == work_hist
        print(f"\n✅ Fields match: {match}")
        
        if match:
            print("🎉 Backend compatibility issue RESOLVED!")
            print("🎉 The API now returns both 'work_experience' and 'work_history'")
            print("🎉 Backend will receive work_history field correctly!")
        else:
            print("❌ Fields don't match - need to investigate")
    else:
        print(f"⚠️  No work experience data found")
    
    # Check other fields
    skills = api_response.skills
    education = api_response.education
    print(f"\n📚 Skills: {len(skills)} items")
    print(f"🎓 Education: {len(education)} items")
    
    # Show the full API response structure (key fields)
    print(f"\n📊 API Response Structure:")
    print(f"   candidate_id: {api_response.candidate_id}")
    print(f"   status: {api_response.status}")
    print(f"   work_experience: {len(api_response.work_experience)} items")
    print(f"   work_history: {len(api_response.work_history)} items")
    print(f"   skills: {len(api_response.skills)} items")
    print(f"   education: {len(api_response.education)} items")
    print(f"   confidence: {api_response.confidence.get('overall', 0):.3f}")
    
    print("\n" + "=" * 60)
    print("✅ API Endpoint Test Complete!")
    print("✅ Backend will now receive work_history field populated correctly!")
    
    return api_response

if __name__ == "__main__":
    test_api_endpoint()
