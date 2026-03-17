#!/usr/bin/env python3
"""
Check Latest Fixed JSON from Database
Run this script to see your properly formatted JSON
"""

import sqlite3
import json
from pathlib import Path

def check_latest_json():
    """Check and display the latest fixed JSON"""
    db_path = Path("resume_parser.db")
    
    if not db_path.exists():
        print("❌ Database not found!")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # First, check the table structure
        cursor.execute("PRAGMA table_info(parsing_jobs)")
        columns = cursor.fetchall()
        print("📋 Database columns:")
        for col in columns:
            print(f"   {col[1]}")
        print()
        
        # Get all jobs to see if there's a new one
        cursor.execute("""
            SELECT id, status, parsed_data, started_at, filename, raw_text, last_stage 
            FROM parsing_jobs 
            ORDER BY id DESC 
            LIMIT 10
        """)
        
        results = cursor.fetchall()
        if not results:
            print("❌ No parsing jobs found!")
            return
        
        print("📊 All recent jobs:")
        for job_id, status, parsed_data, started_at, filename, raw_text, last_stage in results:
            raw_status = "✅" if raw_text and len(raw_text) > 100 else "❌"
            print(f"   {job_id}: {status} ({filename}) (started: {started_at}) [raw: {raw_status}] [stage: {last_stage}]")
        print()
        
        # Check for any job with parsed data (even if not completed)
        any_parsed = None
        for job_id, status, parsed_data, started_at, filename, raw_text, last_stage in results:
            if parsed_data and len(parsed_data) > 100:  # Has actual JSON data
                any_parsed = (job_id, status, parsed_data, filename)
                break
        
        if not any_parsed:
            print("❌ No jobs with parsed data found!")
            print("💡 The resume might still be processing. Check the UI for status.")
            print("💡 Or there might be an error in processing.")
            
            # Show the latest pending job details
            latest_pending = results[0] if results else None
            if latest_pending:
                job_id, status, parsed_data, started_at, filename, raw_text, last_stage = latest_pending
                print(f"\n🔍 Latest pending job details:")
                print(f"   Job ID: {job_id}")
                print(f"   Filename: {filename}")
                print(f"   Status: {status}")
                print(f"   Last Stage: {last_stage}")
                print(f"   Raw Text Length: {len(raw_text) if raw_text else 0}")
                if raw_text:
                    print(f"   Raw Text Preview: {raw_text[:200]}...")
            return
        
        job_id, status, parsed_data, filename = any_parsed
        
        print(f"🎯 LATEST PARSING JOB:")
        print(f"   ID: {job_id}")
        print(f"   Status: {status}")
        print()
        
        if parsed_data:
            try:
                json_data = json.loads(parsed_data)
                
                print("✅ FIXED JSON STRUCTURE:")
                print("=" * 50)
                
                # Check basics
                basics = json_data.get('basics', {})
                if basics:
                    print("📝 CONTACT INFO:")
                    print(f"   Name: {basics.get('firstName', '')} {basics.get('lastName', '')}")
                    print(f"   Email: {basics.get('email', [])}")
                    print(f"   Phone: {basics.get('phone', [])}")
                    print(f"   Location: {basics.get('city', '')}, {basics.get('country', '')}")
                    print()
                
                # Check work experience
                work = json_data.get('work', [])
                print(f"💼 WORK EXPERIENCE: {len(work)} jobs")
                for i, job in enumerate(work[:3]):  # Show first 3
                    print(f"   {i+1}. {job.get('jobTitle', '')} at {job.get('company', '')}")
                    print(f"      {job.get('startDate', '')} - {job.get('endDate', '')}")
                    print(f"      {job.get('city', '')}, {job.get('country', '')}")
                print()
                
                # Check education
                education = json_data.get('education', [])
                print(f"🎓 EDUCATION: {len(education)} entries")
                for i, edu in enumerate(education[:2]):  # Show first 2
                    print(f"   {i+1}. {edu.get('degree', '')} at {edu.get('institution', '')}")
                    print(f"      Graduated: {edu.get('graduationYear', '')}")
                print()
                
                # Check skills
                skills = json_data.get('skills', [])
                print(f"🔧 SKILLS: {len(skills)} skills")
                if skills:
                    # Show first 5 skills
                    sample_skills = [skill.get('name', '') for skill in skills[:5]]
                    print(f"   Sample: {', '.join(sample_skills)}...")
                print()
                
                # Check certifications
                certifications = json_data.get('certifications', [])
                print(f"🏆 CERTIFICATIONS: {len(certifications)} certifications")
                for i, cert in enumerate(certifications[:3]):  # Show first 3
                    print(f"   {i+1}. {cert.get('name', '')}")
                    if cert.get('issuer'):
                        print(f"      Issuer: {cert.get('issuer', '')}")
                print()
                
                # Save full JSON to file
                output_file = Path("fixed_parsed_resume.json")
                with open(output_file, 'w') as f:
                    json.dump(json_data, f, indent=2)
                print(f"💾 Full JSON saved to: {output_file}")
                
                # Check if structure is correct
                print("🔍 STRUCTURE VALIDATION:")
                print("=" * 50)
                
                required_fields = ['basics', 'work', 'education', 'skills', 'certifications']
                for field in required_fields:
                    if field in json_data:
                        print(f"   ✅ {field}: Present")
                    else:
                        print(f"   ❌ {field}: Missing")
                
                # Check basics structure
                if basics:
                    basics_required = ['firstName', 'lastName', 'email', 'phone']
                    for field in basics_required:
                        if field in basics and basics[field]:
                            print(f"   ✅ basics.{field}: Present")
                        else:
                            print(f"   ❌ basics.{field}: Missing")
                
            except json.JSONDecodeError as e:
                print(f"❌ JSON parsing error: {e}")
        else:
            print("❌ No parsed data found!")
            
        conn.close()
        
    except Exception as e:
        print(f"❌ Database error: {e}")

if __name__ == "__main__":
    print("🔍 CHECKING LATEST FIXED JSON")
    print("=" * 60)
    check_latest_json()
