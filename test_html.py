#!/usr/bin/env python3
"""
Test script to verify HTML content without authentication
"""
import requests

# Test the HTML endpoint without authentication
job_id = "f1a64055-89b5-45c2-b544-987e8327bf07"
url = f"http://localhost:8000/api/v1/files/{job_id}/html-test"

try:
    response = requests.get(url, timeout=10)
    print(f"Status: {response.status_code}")
    print(f"Content length: {len(response.text)}")
    print(f"Content preview: {response.text[:200]}...")
    
    if response.status_code == 200:
        print("✅ HTML endpoint is working!")
    else:
        print(f"❌ HTML endpoint failed: {response.status_code}")
        
except Exception as e:
    print(f"❌ Error: {e}")
