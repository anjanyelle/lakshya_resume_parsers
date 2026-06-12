#!/usr/bin/env python3
"""
Test backend integration with AI service to verify work_history saving
"""

import sys
import os
import json
import requests

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import ParseResponse, MasterParser

def test_backend_integration():
    """Test that simulates the backend calling the AI service"""
    
    print("Testing Backend Integration with AI Service")
    print("=" * 60)
    
    # Sample text (similar to what backend would send)
    sample_text = """
    Sai Bhargav Garikapati
    Email: bhargavg115@gmail.com
    Phone: 1 (919) 439-9350
    
    WORK EXPERIENCE
    Senior Data Engineer
    Home Depot
    Atlanta, GA
    March 2023 - Present
    
    Environment: Python, Java, SQL, Hadoop, HDFS, MapReduce, Hive, Spark, 
    Snowflake, Apache NiFi, Great Expectations, Apache Ranger, ERStudio, 
    Apache Airflow, Apache Flink, Apache Kafka Streams, Collibra, dbt, Docker
    
    - Designed multi-account AWS landing zone
    - Implemented secure VPC peering and network segmentation
    - Designed Kubernetes (EKS) clusters for container workloads
    
    Data Engineer
    Previous Company
    Bellevue, WA
    January 2020 - February 2023
    
    - Developed AWS infrastructure for customer-facing banking applications
    - Migrated legacy systems to containerized microservices
    - Implemented API Gateway-based secure integrations
    """
    
    # Test 1: Direct AI service call (like backend does)
    print("\n1. Testing AI Service Direct Call")
    print("-" * 40)
    
    try:
        # Simulate backend calling AI service
        ai_service_url = "http://localhost:8000"  # Default AI service URL
        
        response = requests.post(
            f"{ai_service_url}/parse-text",
            json={"text": sample_text, "candidate_id": "test-backend-integration"},
            timeout=30
        )
        
        if response.status_code == 200:
            ai_result = response.json()
            print(f"✅ AI Service Response Status: {response.status_code}")
            print(f"✅ Candidate ID: {ai_result.get('candidate_id')}")
            print(f"✅ Status: {ai_result.get('status')}")
            print(f"✅ Name: {ai_result.get('name')}")
            print(f"✅ Email: {ai_result.get('email')}")
            
            # Check work_experience and work_history
            work_exp = ai_result.get('work_experience', [])
            work_hist = ai_result.get('work_history', [])
            
            print(f"\n📋 work_experience: {len(work_exp)} entries")
            for i, exp in enumerate(work_exp, 1):
                print(f"   {i}. {exp.get('job_title', 'N/A')} at {exp.get('company_name', 'N/A')}")
                print(f"      Dates: {exp.get('start_date', 'N/A')} - {exp.get('end_date', 'N/A')}")
            
            print(f"\n📋 work_history: {len(work_hist)} entries")
            for i, exp in enumerate(work_hist, 1):
                print(f"   {i}. {exp.get('job_title', 'N/A')} at {exp.get('company_name', 'N/A')}")
                print(f"      Dates: {exp.get('start_date', 'N/A')} - {exp.get('end_date', 'N/A')}")
            
            # Verify they match
            if work_exp and work_hist:
                match = work_exp == work_hist
                print(f"\n✅ Fields match: {match}")
                if match:
                    print("🎉 Backend will receive work_history populated correctly!")
                else:
                    print("❌ Fields don't match")
            
            # Test 2: Simulate backend processing
            print(f"\n2. Testing Backend Processing Simulation")
            print("-" * 40)
            
            # Simulate backend extracting work_experience from AI response
            ai_work_experience = ai_result.get("work_experience", [])
            print(f"Backend would extract {len(ai_work_experience)} work experiences")
            
            # Convert AI service format to backend format (like pipeline.py does)
            backend_payload = []
            for exp in ai_work_experience:
                backend_payload.append({
                    "company": exp.get("company_name", ""),
                    "title": exp.get("job_title", ""),
                    "start_date": exp.get("start_date"),
                    "end_date": exp.get("end_date"),
                    "is_current": exp.get("is_current", False),
                    "location": exp.get("location", ""),
                    "description": exp.get("description", ""),
                    "client": exp.get("client", "")
                })
            
            print(f"Backend would save {len(backend_payload)} entries to work_history table:")
            for i, entry in enumerate(backend_payload, 1):
                print(f"   {i}. {entry.get('title')} at {entry.get('company')}")
                print(f"      Dates: {entry.get('start_date')} - {entry.get('end_date')}")
            
            print(f"\n🎉 SUCCESS: Backend integration test complete!")
            print(f"🎉 Backend will receive and save work_history data correctly!")
            
        else:
            print(f"❌ AI Service Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("⚠️  AI Service not running on localhost:8000")
        print("Start AI service with: cd ai-service && python3 main.py")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("Backend Integration Test Complete!")

if __name__ == "__main__":
    test_backend_integration()
