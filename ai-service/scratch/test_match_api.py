import requests
import json

def test_single_match():
    url = "http://127.0.0.1:8000/match"
    
    candidate = {
        'skills': ['Python', 'JavaScript', 'React', 'AWS', 'Docker', 'PostgreSQL'],
        'years_of_experience': 5,
        'work_experience': [
            {'job_title': 'Software Engineer', 'duration_months': 36},
            {'job_title': 'Senior Developer', 'duration_months': 24}
        ],
        'education': [
            {'degree': 'Bachelor of Science in Computer Science'}
        ]
    }
    
    job = {
        'required_skills': ['Python', 'React', 'Amazon Web Services', 'PostgreSQL'],
        'preferred_skills': ['Docker', 'TypeScript', 'Kubernetes'],
        'min_experience_years': 3,
        'max_experience_years': 7,
        'education_requirement': 'Bachelor'
    }
    
    payload = {
        "candidate_data": candidate,
        "job_data": job
    }
    
    print("Sending match request to AI Service...")
    try:
        response = requests.post(url, json=payload, headers={"Content-Type": "application/json"})
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print("Response JSON:")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"Error Response: {response.text}")
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    test_single_match()
