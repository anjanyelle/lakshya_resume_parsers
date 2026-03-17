#!/usr/bin/env python3

"""
Verify Resume Parsing Results
Check if uploaded resume was parsed and mapped correctly
"""

import json
import sqlite3
import sys
from datetime import datetime
from typing import Dict, Any

def get_latest_parsing_job():
    """Get the most recent parsing job from database"""
    try:
        conn = sqlite3.connect('resume_parser.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, resume_text, parsed_data, complete_resume_json, status, created_at
            FROM parsing_jobs 
            ORDER BY created_at DESC 
            LIMIT 1
        """)
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'id': result[0],
                'resume_text': result[1],
                'parsed_data': result[2],
                'complete_resume_json': result[3],
                'status': result[4],
                'created_at': result[5]
            }
        else:
            return None
            
    except Exception as e:
        print(f"❌ Database error: {e}")
        return None

def verify_json_structure(complete_json: str) -> Dict[str, Any]:
    """Verify the JSON structure matches expected format"""
    try:
        parsed = json.loads(complete_json)
        
        verification = {
            'valid_json': True,
            'has_basics': 'basics' in parsed,
            'has_work': 'work' in parsed,
            'has_education': 'education' in parsed,
            'has_skills': 'skills' in parsed,
            'has_certifications': 'certifications' in parsed,
            'basics_fields': [],
            'work_count': 0,
            'education_count': 0,
            'skills_count': 0,
            'certifications_count': 0,
            'issues': []
        }
        
        # Check basics section
        if 'basics' in parsed:
            basics = parsed['basics']
            required_fields = ['name', 'email', 'phone', 'location']
            for field in required_fields:
                if field in basics and basics[field]:
                    verification['basics_fields'].append(f"✅ {field}")
                else:
                    verification['basics_fields'].append(f"❌ {field}")
                    verification['issues'].append(f"Missing basic field: {field}")
        
        # Check work section
        if 'work' in parsed and isinstance(parsed['work'], list):
            verification['work_count'] = len(parsed['work'])
            for i, work in enumerate(parsed['work']):
                required_fields = ['company', 'title', 'startDate']
                for field in required_fields:
                    if field not in work or not work[field]:
                        verification['issues'].append(f"Work {i+1}: Missing {field}")
        
        # Check education section
        if 'education' in parsed and isinstance(parsed['education'], list):
            verification['education_count'] = len(parsed['education'])
            for i, edu in enumerate(parsed['education']):
                required_fields = ['institution', 'degree']
                for field in required_fields:
                    if field not in edu or not edu[field]:
                        verification['issues'].append(f"Education {i+1}: Missing {field}")
        
        # Check skills section
        if 'skills' in parsed and isinstance(parsed['skills'], list):
            verification['skills_count'] = len(parsed['skills'])
            for i, skill in enumerate(parsed['skills']):
                if 'name' not in skill or not skill['name']:
                    verification['issues'].append(f"Skill {i+1}: Missing name")
        
        # Check certifications section
        if 'certifications' in parsed and isinstance(parsed['certifications'], list):
            verification['certifications_count'] = len(parsed['certifications'])
            for i, cert in enumerate(parsed['certifications']):
                if 'name' not in cert or not cert['name']:
                    verification['issues'].append(f"Certification {i+1}: Missing name")
        
        return verification
        
    except json.JSONDecodeError as e:
        return {
            'valid_json': False,
            'error': str(e),
            'issues': [f"Invalid JSON: {e}"]
        }

def compare_with_training_dataset(parsed_output: Dict[str, Any]) -> Dict[str, Any]:
    """Compare parsed output with training dataset patterns"""
    try:
        with open('comprehensive_all_resumes_dataset_updated.json', 'r') as f:
            training_data = json.load(f)
        
        comparison = {
            'structure_matches': True,
            'field_completeness': 0,
            'quality_score': 0,
            'recommendations': []
        }
        
        # Calculate field completeness
        total_fields = 0
        filled_fields = 0
        
        sections = ['basics', 'work', 'education', 'skills', 'certifications']
        for section in sections:
            if section in parsed_output:
                if section == 'basics':
                    for field in parsed_output[section]:
                        total_fields += 1
                        if parsed_output[section][field]:
                            filled_fields += 1
                else:
                    for item in parsed_output[section]:
                        for field in item:
                            total_fields += 1
                            if item[field]:
                                filled_fields += 1
        
        if total_fields > 0:
            comparison['field_completeness'] = (filled_fields / total_fields) * 100
        
        # Quality score based on completeness
        comparison['quality_score'] = min(100, comparison['field_completeness'])
        
        # Recommendations
        if comparison['field_completeness'] < 80:
            comparison['recommendations'].append("Low field completeness - check parsing rules")
        
        if len(parsed_output.get('work', [])) == 0:
            comparison['recommendations'].append("No work experience found - check section detection")
        
        if len(parsed_output.get('skills', [])) == 0:
            comparison['recommendations'].append("No skills found - check skill extraction")
        
        return comparison
        
    except Exception as e:
        return {
            'structure_matches': False,
            'error': str(e),
            'recommendations': [f"Comparison error: {e}"]
        }

def main():
    """Main verification function"""
    print("🔍 Resume Parsing Verification Tool")
    print("=" * 60)
    print("Checking if your uploaded resume was parsed and mapped correctly...")
    print("=" * 60)
    
    # Get latest parsing job
    job = get_latest_parsing_job()
    
    if not job:
        print("❌ No parsing jobs found in database")
        print("💡 Make sure you've uploaded and processed a resume first")
        return
    
    print(f"📋 Found parsing job #{job['id']}")
    print(f"📅 Created: {job['created_at']}")
    print(f"📊 Status: {job['status']}")
    print()
    
    # Check if parsing completed
    if job['status'] != 'completed':
        print(f"⚠️  Parsing not completed (status: {job['status']})")
        print("💡 Wait for parsing to complete or check for errors")
        return
    
    # Verify JSON structure
    print("🔧 Verifying JSON Structure...")
    verification = verify_json_structure(job['complete_resume_json'])
    
    print("📊 Structure Verification:")
    print(f"  ✅ Valid JSON: {verification['valid_json']}")
    print(f"  📋 Has Basics: {verification['has_basics']}")
    print(f"  💼 Has Work: {verification['has_work']}")
    print(f"  🎓 Has Education: {verification['has_education']}")
    print(f"  🔧 Has Skills: {verification['has_skills']}")
    print(f"  🏆 Has Certifications: {verification['has_certifications']}")
    print()
    
    print("📋 Basic Fields:")
    for field_status in verification['basics_fields']:
        print(f"  {field_status}")
    print()
    
    print("📊 Content Summary:")
    print(f"  💼 Work Positions: {verification['work_count']}")
    print(f"  🎓 Education Entries: {verification['education_count']}")
    print(f"  🔧 Skills: {verification['skills_count']}")
    print(f"  🏆 Certifications: {verification['certifications_count']}")
    print()
    
    # Show issues if any
    if verification['issues']:
        print("⚠️  Issues Found:")
        for issue in verification['issues']:
            print(f"  ❌ {issue}")
        print()
    else:
        print("✅ No structural issues found!")
        print()
    
    # Compare with training dataset
    print("🎯 Comparing with Training Dataset...")
    try:
        parsed_output = json.loads(job['complete_resume_json'])
        comparison = compare_with_training_dataset(parsed_output)
        
        print("📊 Quality Metrics:")
        print(f"  📈 Field Completeness: {comparison['field_completeness']:.1f}%")
        print(f"  🎯 Quality Score: {comparison['quality_score']:.1f}%")
        print()
        
        if comparison['recommendations']:
            print("💡 Recommendations:")
            for rec in comparison['recommendations']:
                print(f"  💭 {rec}")
            print()
        else:
            print("✅ Parsing quality looks good!")
            print()
    
    except Exception as e:
        print(f"❌ Comparison error: {e}")
        print()
    
    # Show sample of parsed data
    print("📋 Sample Parsed Data:")
    try:
        parsed_output = json.loads(job['complete_resume_json'])
        
        if 'basics' in parsed_output:
            basics = parsed_output['basics']
            print("  👤 Basic Info:")
            print(f"    Name: {basics.get('name', 'N/A')}")
            print(f"    Email: {basics.get('email', 'N/A')}")
            print(f"    Phone: {basics.get('phone', 'N/A')}")
            print(f"    Location: {basics.get('location', 'N/A')}")
            print()
        
        if 'work' in parsed_output and parsed_output['work']:
            print("  💼 Work Experience:")
            for i, work in enumerate(parsed_output['work'][:2]):  # Show first 2
                print(f"    {i+1}. {work.get('title', 'N/A')} at {work.get('company', 'N/A')}")
                print(f"       {work.get('startDate', 'N/A')} - {work.get('endDate', 'Present')}")
            print()
        
        if 'skills' in parsed_output and parsed_output['skills']:
            skills = [skill.get('name', 'N/A') for skill in parsed_output['skills'][:5]]
            print(f"  🔧 Top Skills: {', '.join(skills)}")
            print()
    
    except Exception as e:
        print(f"❌ Error displaying sample data: {e}")
    
    print("=" * 60)
    print("🎉 Verification Complete!")
    print("💡 Use this tool to check any uploaded resume parsing results")

if __name__ == "__main__":
    main()
