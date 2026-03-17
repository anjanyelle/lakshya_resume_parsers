#!/usr/bin/env python3
"""
Test JSON Conversion Directly
"""

import json
from app.workers.pipeline import _convert_to_kick_resume_format

# Test data (simulating parsed resume)
test_parsed_data = {
    "contact": {
        "name": {"name": "John Doe"},
        "emails": [{"email": "john.doe@example.com"}],
        "phones": [{"phone": "+1-555-123-4567"}],
        "location": {"city": "New York", "country": "USA"}
    },
    "work_experience": [
        {
            "title": "Software Engineer",
            "company": "Tech Corp",
            "description": "June 2023 - Current (Location: New York, NY)\nRole: Software Engineer\nResponsibilities:\n- Developed software"
        }
    ],
    "education": [
        {
            "institution": "University of Technology",
            "degree": "Bachelor of Science in Computer Science",
            "graduationYear": "2020"
        }
    ],
    "skills": [
        {"name": "Python", "category": "Programming", "confidence": 0.85},
        {"name": "JavaScript", "category": "Programming", "confidence": 0.85}
    ],
    "certifications": [
        {"name": "AWS Certified", "issuer": "Amazon"}
    ]
}

def test_json_conversion():
    """Test the JSON conversion function"""
    print("🧪 TESTING JSON CONVERSION")
    print("=" * 50)
    
    # Convert to Kick Resume format
    kick_format = _convert_to_kick_resume_format(test_parsed_data)
    
    # Display result
    print("✅ CONVERTED JSON:")
    print(json.dumps(kick_format, indent=2))
    
    # Save to file
    with open("test_converted_json.json", "w") as f:
        json.dump(kick_format, f, indent=2)
    
    print("\n💾 Saved to: test_converted_json.json")
    print("🎯 This shows how your JSON will look when processing works!")

if __name__ == "__main__":
    test_json_conversion()
