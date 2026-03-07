#!/usr/bin/env python3
"""
Test script for the AI Service FastAPI application.
Tests all endpoints and demonstrates usage.
"""

import requests
import json
import time
import os
from pathlib import Path

# API base URL
BASE_URL = "http://localhost:8000"

def test_health_endpoint():
    """Test the health check endpoint."""
    print("🏥 Testing Health Endpoint")
    print("-" * 30)
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check successful!")
            print(f"   Status: {data['status']}")
            print(f"   Version: {data['version']}")
            print(f"   Extractor Available: {data['extractor_available']}")
            print(f"   Supported Formats: {data['supported_formats']}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to AI service. Make sure it's running on port 8000")
        return False
    except Exception as e:
        print(f"❌ Health check error: {str(e)}")
        return False

def test_root_endpoint():
    """Test the root endpoint."""
    print("\n🏠 Testing Root Endpoint")
    print("-" * 30)
    
    try:
        response = requests.get(f"{BASE_URL}/")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Root endpoint successful!")
            print(f"   Message: {data['message']}")
            print(f"   Service: {data['service']}")
            print(f"   Version: {data['version']}")
            print(f"   Endpoints: {list(data['endpoints'].keys())}")
            return True
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Root endpoint error: {str(e)}")
        return False

def test_parse_text_endpoint():
    """Test the parse-text endpoint with sample text."""
    print("\n📝 Testing Parse Text Endpoint")
    print("-" * 30)
    
    sample_text = """
    JOHN DOE
    123 Main Street, Anytown, USA 12345
    (555) 123-4567 | john.doe@example.com
    
    PROFESSIONAL SUMMARY
    Experienced software engineer with 5+ years in full-stack development.
    Proficient in Python, JavaScript, and cloud technologies.
    
    EDUCATION
    Bachelor of Science in Computer Science
    University of Technology, 2018-2022
    
    EXPERIENCE
    Senior Software Engineer | Tech Corp | 2022-Present
    - Developed scalable web applications
    - Led team of 3 junior developers
    - Improved system performance by 40%
    
    SKILLS
    Programming: Python, JavaScript, Java, TypeScript
    Frameworks: React, Node.js, Django, Flask
    Cloud: AWS, Docker, Kubernetes
    """
    
    try:
        payload = {
            "text": sample_text,
            "candidate_id": "test-candidate-123"
        }
        
        response = requests.post(
            f"{BASE_URL}/parse-text",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Parse text successful!")
            print(f"   Candidate ID: {data['candidate_id']}")
            print(f"   Status: {data['status']}")
            print(f"   Word Count: {data['word_count']}")
            print(f"   Quality Score: {data['quality_score']:.2f}")
            print(f"   Parsing Method: {data['parsing_method']}")
            print(f"   Text Preview: {data['extracted_text'][:100]}...")
            return True
        else:
            print(f"❌ Parse text failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Parse text error: {str(e)}")
        return False

def test_parse_file_endpoint():
    """Test the parse endpoint with a file (if available)."""
    print("\n📄 Testing Parse File Endpoint")
    print("-" * 30)
    
    # Check if we have a test file
    test_files = []
    test_dir = Path("test_files")
    
    if test_dir.exists():
        for ext in ['.pdf', '.docx', '.txt']:
            test_files.extend(test_dir.glob(f"*{ext}"))
    
    if not test_files:
        print("⚠️  No test files found. Skipping file parsing test.")
        print("   Add test files to test_files/ directory to test file parsing.")
        return True
    
    test_file = test_files[0]  # Use first available file
    
    try:
        payload = {
            "file_path": str(test_file),
            "candidate_id": "test-candidate-456",
            "file_type": test_file.suffix[1:]  # Remove the dot
        }
        
        print(f"   Testing with file: {test_file.name}")
        
        response = requests.post(
            f"{BASE_URL}/parse",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Parse file successful!")
            print(f"   Candidate ID: {data['candidate_id']}")
            print(f"   Status: {data['status']}")
            print(f"   Word Count: {data['word_count']}")
            print(f"   Quality Score: {data['quality_score']:.2f}")
            print(f"   Parsing Method: {data['parsing_method']}")
            print(f"   Text Preview: {data['extracted_text'][:100]}...")
            return True
        else:
            print(f"❌ Parse file failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Parse file error: {str(e)}")
        return False

def test_error_handling():
    """Test error handling with invalid requests."""
    print("\n⚠️  Testing Error Handling")
    print("-" * 30)
    
    # Test with non-existent file
    try:
        payload = {
            "file_path": "/non/existent/file.pdf",
            "candidate_id": "test-123",
            "file_type": "pdf"
        }
        
        response = requests.post(
            f"{BASE_URL}/parse",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 404:
            print(f"✅ File not found error handled correctly!")
            print(f"   Status: {response.status_code}")
            return True
        else:
            print(f"⚠️  Expected 404, got {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error handling test failed: {str(e)}")
        return False

def run_all_tests():
    """Run all API tests."""
    print("🚀 AI Service API Test Suite")
    print("=" * 50)
    print()
    
    results = []
    
    # Run all tests
    results.append(test_health_endpoint())
    results.append(test_root_endpoint())
    results.append(test_parse_text_endpoint())
    results.append(test_parse_file_endpoint())
    results.append(test_error_handling())
    
    # Summary
    print("\n📊 Test Results Summary")
    print("=" * 30)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed!")
    else:
        print(f"⚠️  {total - passed} test(s) failed")
    
    print()
    print("To start the AI service:")
    print("  cd ai-service")
    print("  python main.py")
    print()
    print("Then run tests:")
    print("  python test_api.py")
    
    return passed == total

if __name__ == "__main__":
    # Check if service is running
    print("Checking if AI service is running...")
    time.sleep(1)
    
    # Run all tests
    success = run_all_tests()
    
    # Exit with appropriate code
    exit(0 if success else 1)
