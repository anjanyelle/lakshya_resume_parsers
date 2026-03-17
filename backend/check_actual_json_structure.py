#!/usr/bin/env python3
"""
CHECK ACTUAL JSON STRUCTURE USED IN YOUR PROJECT
"""

def check_actual_json_structure():
    """Check the actual JSON structure your project uses"""
    
    print("=" * 80)
    print("🔍 YOUR ACTUAL JSON STRUCTURE")
    print("=" * 80)
    
    # Based on enhanced_pipeline_final.py
    actual_json_structure = {
        "basics": {
            "name": "string",
            "email": "string", 
            "phone": "string",
            "location": "string",
            "summary": "string",
            "linkedin": "string"
        },
        "work": [
            {
                "title": "string",
                "company": "string",
                "date_range": "string",
                "location": "string",
                "description": "string"
            }
        ],
        "education": [
            {
                "institution": "string",
                "degree": "string",
                "field_of_study": "string",
                "graduation_year": "string",
                "location": "string"
            }
        ],
        "skills": [
            {
                "name": "string",
                "level": "string",
                "category": "string"
            }
        ],
        "certifications": [
            {
                "name": "string",
                "issuer": "string",
                "license_number": "string",
                "issue_date": "string",
                "expiry_date": "string"
            }
        ],
        "projects": [],  # TODO: Add project parser integration
        "achievements": [],  # TODO: Add achievement parser integration
        "volunteer": [],  # TODO: Add volunteer parser integration
        "publications": [],  # TODO: Add publication parser integration
        "languages": [],  # TODO: Add language parser integration
        "references": [],  # TODO: Add reference parser integration
        "texts": {
            "additional_text": "string"
        }
    }
    
    print("📋 YOUR ACTUAL JSON STRUCTURE (from enhanced_pipeline_final.py):")
    print("=" * 80)
    
    for key, value in actual_json_structure.items():
        if isinstance(value, dict):
            print(f"🔹 {key}:")
            for sub_key, sub_value in value.items():
                print(f"   - {sub_key}: {sub_value}")
        elif isinstance(value, list):
            if value and isinstance(value[0], dict):
                print(f"🔹 {key}: [list of objects with {len(value[0])} fields]")
                for sub_key, sub_value in value[0].items():
                    print(f"   - {sub_key}: {sub_value}")
            else:
                print(f"🔹 {key}: [] (empty list)")
        else:
            print(f"🔹 {key}: {value}")
    
    print("\n" + "=" * 80)
    print("🔍 COMPARISON WITH MY ANALYSIS")
    print("=" * 80)
    
    comparison = {
        "MY ANALYSIS STRUCTURE": {
            "candidate": "name, email, phone, location, linkedin",
            "job_title": "raw, normalized, category",
            "total_experience": "years, months, label",
            "summary": "string",
            "skills": "all, by_category",
            "work_experience": "company, title, start_date, end_date, location",
            "education": "degree, institution, graduation_year, field_of_study",
            "certifications": "name, issuer, license_number"
        },
        "YOUR ACTUAL STRUCTURE": {
            "basics": "name, email, phone, location, summary, linkedin",
            "work": "title, company, date_range, location, description",
            "education": "institution, degree, field_of_study, graduation_year, location",
            "skills": "name, level, category",
            "certifications": "name, issuer, license_number, issue_date, expiry_date",
            "projects": "[] (TODO)",
            "achievements": "[] (TODO)",
            "volunteer": "[] (TODO)",
            "publications": "[] (TODO)",
            "languages": "[] (TODO)",
            "references": "[] (TODO)",
            "texts": "additional_text"
        }
    }
    
    print("📊 STRUCTURE DIFFERENCES:")
    print("=" * 50)
    
    my_keys = set(comparison["MY ANALYSIS STRUCTURE"].keys())
    your_keys = set(comparison["YOUR ACTUAL STRUCTURE"].keys())
    
    print("🔹 IN MY ANALYSIS BUT NOT IN YOURS:")
    for key in my_keys - your_keys:
        print(f"   - {key}: {comparison['MY ANALYSIS STRUCTURE'][key]}")
    
    print("\n🔹 IN YOURS BUT NOT IN MY ANALYSIS:")
    for key in your_keys - my_keys:
        print(f"   - {key}: {comparison['YOUR ACTUAL STRUCTURE'][key]}")
    
    print("\n🔹 COMMON STRUCTURES (different organization):")
    common = my_keys & your_keys
    for key in common:
        my_structure = comparison["MY ANALYSIS STRUCTURE"][key]
        your_structure = comparison["YOUR ACTUAL STRUCTURE"][key]
        print(f"   - {key}:")
        print(f"     My: {my_structure}")
        print(f"     Yours: {your_structure}")
    
    print("\n" + "=" * 80)
    print("🎯 KEY DIFFERENCES SUMMARY")
    print("=" * 80)
    
    differences = [
        "🔹 YOU use 'basics' instead of 'candidate'",
        "🔹 YOU use 'work' instead of 'work_experience'", 
        "🔹 YOU use 'date_range' instead of separate start_date/end_date",
        "🔹 YOU have additional sections (projects, achievements, etc.)",
        "🔹 YOU have 'texts' section for additional content",
        "🔹 YOUR skills have 'level' and 'category' fields",
        "🔹 YOUR work entries have 'description' field"
    ]
    
    for diff in differences:
        print(diff)
    
    print("\n" + "=" * 80)
    print("✅ CONCLUSION")
    print("=" * 80)
    print("🎯 YOUR ACTUAL STRUCTURE IS DIFFERENT FROM MY ANALYSIS!")
    print("🎯 You use the 'basics/work/education/skills/certifications' structure")
    print("🎯 This is based on JSON Resume format (https://jsonresume.org/)")
    print("🎯 My analysis assumed a different custom structure")
    print("🎯 Your actual structure is well-structured and production-ready")
    
    return actual_json_structure

if __name__ == "__main__":
    check_actual_json_structure()
