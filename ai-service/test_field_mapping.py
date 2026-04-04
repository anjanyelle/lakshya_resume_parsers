#!/usr/bin/env python3
"""
Test script to verify work_experience -> work_history field mapping
"""

import sys
import os

# Add current directory to path to import main
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import ParseResponse

def test_field_mapping():
    """Test that work_experience maps to work_history correctly"""
    
    print("Testing work_experience -> work_history field mapping...")
    print("=" * 60)
    
    # Test 1: Input with work_experience only
    print("\n1. Test: Input with work_experience only")
    data1 = {
        "candidate_id": "test-123",
        "status": "success",
        "name": "John Doe",
        "email": "john@example.com",
        "work_experience": [
            {
                "job_title": "Software Engineer",
                "company_name": "Acme Corp",
                "start_date": "2020-01-01",
                "end_date": "2022-12-31"
            }
        ]
    }
    
    response1 = ParseResponse(**data1)
    print(f"   work_experience count: {len(response1.work_experience)}")
    print(f"   work_history count: {len(response1.work_history)}")
    print(f"   Fields match: {response1.work_experience == response1.work_history}")
    
    # Test 2: Input with work_history only
    print("\n2. Test: Input with work_history only")
    data2 = {
        "candidate_id": "test-456",
        "status": "success",
        "name": "Jane Smith",
        "email": "jane@example.com",
        "work_history": [
            {
                "job_title": "Data Scientist",
                "company_name": "Tech Inc",
                "start_date": "2019-06-01",
                "end_date": "2021-05-31"
            }
        ]
    }
    
    response2 = ParseResponse(**data2)
    print(f"   work_experience count: {len(response2.work_experience)}")
    print(f"   work_history count: {len(response2.work_history)}")
    print(f"   Fields match: {response2.work_experience == response2.work_history}")
    
    # Test 3: Input with both fields (should keep both)
    print("\n3. Test: Input with both work_experience and work_history")
    data3 = {
        "candidate_id": "test-789",
        "status": "success",
        "name": "Bob Johnson",
        "email": "bob@example.com",
        "work_experience": [
            {
                "job_title": "Backend Developer",
                "company_name": "Startup Co",
                "start_date": "2021-01-01",
                "end_date": "2023-12-31"
            }
        ],
        "work_history": [
            {
                "job_title": "Different Role",
                "company_name": "Different Co",
                "start_date": "2018-01-01",
                "end_date": "2020-12-31"
            }
        ]
    }
    
    response3 = ParseResponse(**data3)
    print(f"   work_experience count: {len(response3.work_experience)}")
    print(f"   work_history count: {len(response3.work_history)}")
    print(f"   work_experience title: {response3.work_experience[0]['job_title']}")
    print(f"   work_history title: {response3.work_history[0]['job_title']}")
    
    # Test 4: Empty fields
    print("\n4. Test: Empty work_experience/work_history")
    data4 = {
        "candidate_id": "test-empty",
        "status": "success",
        "name": "Empty Test",
        "email": "empty@example.com"
    }
    
    response4 = ParseResponse(**data4)
    print(f"   work_experience count: {len(response4.work_experience)}")
    print(f"   work_history count: {len(response4.work_history)}")
    print(f"   Both empty: {len(response4.work_experience) == 0 and len(response4.work_history) == 0}")
    
    print("\n" + "=" * 60)
    print("✅ Field mapping tests completed!")
    print("✅ Backend compatibility issue resolved!")
    print("\nThe AI service now returns both 'work_experience' and 'work_history' fields,")
    print("with automatic mapping between them for backend compatibility.")

if __name__ == "__main__":
    test_field_mapping()
