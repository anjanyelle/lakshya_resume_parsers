"""
Script to check the uploaded resume data.
You can either:
1. Run this with authentication tokens, OR
2. Check the browser's Network tab for the API response
"""

import json

# If you can get the API response from browser network tab, paste it here:
sample_response = {
    "candidate": {
        "id": "your-candidate-id",
        "full_name": "Pavan Kumar",
        "email": "03248@gmail.com",
        "work_history": [
            {
                "company_name": "Bank of America",
                "job_title": "Senior Full Stack Developer", 
                "location": "North Carolina",
                "start_date": "2021-07-01",
                "end_date": None,
                "is_current": True,
                "description": "Should now contain bullets here...",
                "id": "job-id-1"
            }
        ],
        "work": [
            {
                "company": "Bank of America",
                "title": "Senior Full Stack Developer",
                "location": "North Carolina", 
                "bullets": ["Bullet 1", "Bullet 2"],
                "start_date": "2021-07-01",
                "end_date": None
            }
        ]
    }
}

def analyze_response(response_data):
    """Analyze the API response to verify work experience data"""
    candidate = response_data.get("candidate", {})
    
    print("=== RESUME UPLOAD ANALYSIS ===")
    print(f"Candidate: {candidate.get('full_name')}")
    print(f"Email: {candidate.get('email')}")
    
    print("\n=== WORK HISTORY (Database) ===")
    work_history = candidate.get("work_history", [])
    print(f"Jobs in work_history: {len(work_history)}")
    
    for i, job in enumerate(work_history, 1):
        print(f"\nJob {i}:")
        print(f"  Company: {job.get('company_name')}")
        print(f"  Title: {job.get('job_title')}")
        print(f"  Location: {job.get('location')}")
        print(f"  Dates: {job.get('start_date')} to {job.get('end_date')}")
        description = job.get('description')
        if description:
            print(f"  Description length: {len(description)} chars")
            print(f"  Description preview: {description[:100]}...")
            # Check if bullets are included
            bullet_count = description.count('- ')
            print(f"  Bullet points detected: {bullet_count}")
        else:
            print(f"  Description: NULL or EMPTY ❌")
    
    print("\n=== WORK FIELD (Parsed Data) ===")
    work = candidate.get("work", [])
    print(f"Jobs in work field: {len(work)}")
    
    for i, job in enumerate(work[:2], 1):  # Show first 2 jobs
        print(f"\nJob {i}:")
        print(f"  Company: {job.get('company')}")
        print(f"  Title: {job.get('title')}")
        print(f"  Location: {job.get('location')}")
        bullets = job.get('bullets', [])
        print(f"  Bullets count: {len(bullets)}")
        if bullets:
            print(f"  First bullet: {bullets[0][:80]}...")
    
    print("\n=== ANALYSIS RESULTS ===")
    
    # Check if the fix worked
    has_descriptions = any(job.get('description') for job in work_history)
    has_bullets_in_desc = any(job.get('description', '').count('- ') > 0 for job in work_history)
    
    if has_descriptions and has_bullets_in_desc:
        print("✅ SUCCESS: Database now contains bullet points in descriptions!")
        print("🎉 UI should display complete work experience now!")
    elif has_descriptions:
        print("⚠️  PARTIAL: Database has descriptions but no bullets detected")
        print("🔍 Check if bullets are formatted differently")
    else:
        print("❌ ISSUE: Database descriptions are still empty")
        print("🔄 May need to re-parse the resume or check pipeline")
    
    if work:
        print("✅ Parsed data available in 'work' field")
    else:
        print("❌ No data in 'work' field")

if __name__ == "__main__":
    print("To check your uploaded resume:")
    print("1. Open browser Developer Tools (F12)")
    print("2. Go to Network tab")
    print("3. Upload/refresh the resume")
    print("4. Find the API call to /api/v1/candidates/{id}")
    print("5. Copy the response and paste it here")
    print("6. Re-run this script")
    print("\nOr run with authentication if you have tokens")
    
    # Run with sample data
    analyze_response(sample_response)
