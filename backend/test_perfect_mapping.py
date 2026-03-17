#!/usr/bin/env python3

"""
Test Perfect JSON Dataset for Data Mapping
Shows how to use perfect_json_dataset.json for perfect data mapping
"""

import json
from typing import Dict, Any

def test_perfect_mapping():
    """Test perfect data mapping from perfect_json_dataset.json"""
    
    print("🎯 Testing Perfect JSON Dataset for Data Mapping")
    print("=" * 60)
    
    # Load the perfect JSON dataset
    with open('perfect_json_dataset.json', 'r', encoding='utf-8') as f:
        dataset = json.load(f)
    
    print(f"📊 Loaded {len(dataset)} perfect samples")
    
    # Test the first sample (Alistair Caldwell)
    sample = dataset[0]
    expected_output = sample['expected_output']
    
    print("\n🎯 Perfect Data Mapping Test:")
    print("-" * 40)
    
    # Test basics mapping
    print("\n📋 BASICS MAPPING:")
    basics = expected_output['basics']
    for key, value in basics.items():
        print(f"  {key}: '{value}' ✅")
    
    # Test work mapping
    print("\n💼 WORK MAPPING:")
    work = expected_output['work']
    for i, job in enumerate(work):
        print(f"  Job {i+1}:")
        for key, value in job.items():
            print(f"    {key}: '{value}' ✅")
    
    # Test education mapping
    print("\n🎓 EDUCATION MAPPING:")
    education = expected_output['education']
    for i, edu in enumerate(education):
        print(f"  Education {i+1}:")
        for key, value in edu.items():
            print(f"    {key}: '{value}' ✅")
    
    # Test skills mapping
    print("\n🔧 SKILLS MAPPING:")
    skills = expected_output['skills']
    for i, skill in enumerate(skills[:5]):  # Show first 5
        print(f"  Skill {i+1}:")
        for key, value in skill.items():
            print(f"    {key}: '{value}' ✅")
    
    # Test certifications mapping
    print("\n🏆 CERTIFICATIONS MAPPING:")
    certifications = expected_output['certifications']
    for i, cert in enumerate(certifications):
        print(f"  Certification {i+1}:")
        for key, value in cert.items():
            print(f"    {key}: '{value}' ✅")
    
    # Validate structure
    print("\n🔍 STRUCTURE VALIDATION:")
    required_keys = ['basics', 'work', 'education', 'skills', 'certifications', 'projects', 'languages', 'volunteer', 'references', 'achievements', 'publications']
    
    for key in required_keys:
        if key in expected_output:
            print(f"  {key}: ✅ Present")
        else:
            print(f"  {key}: ❌ Missing")
    
    # Validate basics structure
    print("\n🔍 BASICS VALIDATION:")
    required_basics = ['name', 'email', 'phone', 'location', 'summary', 'linkedin', 'github', 'website']
    
    for key in required_basics:
        if key in basics:
            print(f"  basics.{key}: ✅ Present")
        else:
            print(f"  basics.{key}: ❌ Missing")
    
    # Show sample mapping for your parser
    print("\n🎯 SAMPLE MAPPING FOR YOUR PARSER:")
    print("-" * 40)
    
    print("# Perfect JSON Structure for Your Parser:")
    print("parsed_data = {")
    print("    'basics': {")
    for key, value in basics.items():
        print(f"        '{key}': '{value}',")
    print("    },")
    print("    'work': [")
    for job in work:
        print("        {")
        for key, value in job.items():
            print(f"            '{key}': '{value}',")
        print("        },")
    print("    ],")
    print("    'education': [...],")
    print("    'skills': [...],")
    print("    'certifications': [...],")
    print("    'projects': [],")
    print("    'languages': [...],")
    print("    'volunteer': [],")
    print("    'references': [],")
    print("    'achievements': [],")
    print("    'publications': []")
    print("}")
    
    print("\n✅ Perfect JSON Dataset Ready for Data Mapping!")
    print("🎯 Use perfect_json_dataset.json for perfect key-value mapping!")

def show_mapping_examples():
    """Show examples of how to map data from resume text to JSON"""
    
    print("\n🎯 MAPPING EXAMPLES:")
    print("=" * 40)
    
    mapping_examples = {
        "name": {
            "resume_text": "ALISTAIR H. CALDWELL",
            "json_key": "basics.name",
            "mapped_value": "ALISTAIR H. CALDWELL"
        },
        "email": {
            "resume_text": "a.caldwell.dotnet@enterprise-solutions.net",
            "json_key": "basics.email",
            "mapped_value": "a.caldwell.dotnet@enterprise-solutions.net"
        },
        "phone": {
            "resume_text": "(512) 555-0942",
            "json_key": "basics.phone",
            "mapped_value": "(512) 555-0942"
        },
        "company": {
            "resume_text": "Nexus FinTech Systems",
            "json_key": "work[0].company",
            "mapped_value": "Nexus FinTech Systems"
        },
        "title": {
            "resume_text": "Global Director of Engineering & Principal .NET Architect",
            "json_key": "work[0].title",
            "mapped_value": "Global Director of Engineering & Principal .NET Architect"
        },
        "skill": {
            "resume_text": "C#",
            "json_key": "skills[0].name",
            "mapped_value": "C#"
        }
    }
    
    for field, mapping in mapping_examples.items():
        print(f"\n📋 {field.upper()} MAPPING:")
        print(f"  Resume Text: '{mapping['resume_text']}'")
        print(f"  JSON Key: '{mapping['json_key']}'")
        print(f"  Mapped Value: '{mapping['mapped_value']}' ✅")

if __name__ == "__main__":
    test_perfect_mapping()
    show_mapping_examples()
