import requests
import json

# Test the API response for a candidate
# You'll need to replace this with the actual candidate ID and API endpoint
candidate_id = "66eb4721-e8bc-4a66-acf9-f850cd9f165a"  # From your JSON
api_url = f"http://localhost:8000/api/v1/candidates/{candidate_id}"

try:
    response = requests.get(api_url)
    if response.status_code == 200:
        data = response.json()
        candidate = data.get("candidate", {})
        
        print("=== API RESPONSE ANALYSIS ===")
        print(f"Candidate Name: {candidate.get('full_name')}")
        print(f"Email: {candidate.get('email')}")
        
        print("\n=== WORK HISTORY (from database) ===")
        work_history = candidate.get("work_history", [])
        print(f"Work History count: {len(work_history)}")
        for i, job in enumerate(work_history, 1):
            print(f"\nJob {i}:")
            print(f"  Company: {job.get('company_name')}")
            print(f"  Title: {job.get('job_title')}")
            print(f"  Location: {job.get('location')}")
            print(f"  Dates: {job.get('start_date')} to {job.get('end_date')}")
            print(f"  Description: {job.get('description')[:100] if job.get('description') else 'NULL'}...")
        
        print("\n=== WORK (from parsed_data) ===")
        work = data.get("work", [])
        print(f"Work count: {len(work)}")
        for i, job in enumerate(work, 1):
            print(f"\nJob {i}:")
            print(f"  Company: {job.get('company')}")
            print(f"  Title: {job.get('title')}")
            print(f"  Location: {job.get('location')}")
            print(f"  Dates: {job.get('start_date')} to {job.get('end_date')}")
            bullets = job.get('bullets', [])
            print(f"  Bullets count: {len(bullets)}")
            if bullets:
                print(f"  First bullet: {bullets[0][:100]}...")
        
        print("\n=== RECOMMENDATION ===")
        if len(work_history) > 0 and len(work) > 0:
            print("✅ Both work_history and work data available")
            print("👉 UI should read from 'work' field for complete data with bullets")
            print("👇 work_history only has basic info, work has full details")
        elif len(work_history) > 0:
            print("⚠️  Only work_history available (no bullets)")
        elif len(work) > 0:
            print("✅ Only work field available (complete data)")
        else:
            print("❌ No work experience data found")
            
    else:
        print(f"❌ API Error: {response.status_code}")
        print(response.text)
        
except requests.exceptions.ConnectionError:
    print("❌ Cannot connect to API. Make sure the backend is running on localhost:8000")
except Exception as e:
    print(f"❌ Error: {e}")
