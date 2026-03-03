#!/usr/bin/env python3
"""
Test the HTML endpoint directly
"""
import requests

def test_html_endpoint():
    job_id = '31715690-3dfd-4e75-9bc6-90e12ab8c3c4'
    url = f'http://localhost:8000/api/v1/files/{job_id}/html'
    
    try:
        response = requests.get(url, timeout=10)
        print(f'Status: {response.status_code}')
        print(f'Content-Type: {response.headers.get("content-type", "N/A")}')
        print(f'Content length: {len(response.text)}')
        
        if response.status_code == 200:
            print('✅ HTML endpoint is working!')
            print(f'HTML sample: {response.text[:200]}...')
        else:
            print(f'❌ HTML endpoint failed: {response.status_code}')
            print(f'Error: {response.text[:200]}...')
            
    except Exception as e:
        print(f'❌ Backend not accessible: {e}')

if __name__ == '__main__':
    test_html_endpoint()
