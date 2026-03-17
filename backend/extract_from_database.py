#!/usr/bin/env python3

"""
Extract Your Resume Data from Database
Create dataset from your existing parsed resumes
"""

import json
from datetime import datetime
from app.core.database import SessionLocal
from app.models import ParsingJob

def extract_from_database():
    """Extract your resume data from database"""
    
    print("🎯 Extracting Resume Data from Database")
    print("=" * 50)
    
    # Connect to database
    db = SessionLocal()
    
    try:
        # Get all parsing jobs
        jobs = db.query(ParsingJob).all()
        
        print(f"📊 Found {len(jobs)} jobs in database")
        
        dataset = []
        
        for i, job in enumerate(jobs, 1):
            print(f"\n📋 Processing Job {i}: {job.id}")
            
            # Get parsed data
            parsed_data = job.parsed_data or {}
            
            # Check if complete_resume_json exists
            complete_json = parsed_data.get('complete_resume_json', {})
            
            if not complete_json:
                print(f"  ❌ No complete_resume_json found")
                continue
            
            # Get resume text
            resume_text = job.raw_text or ""
            
            if not resume_text:
                print(f"  ❌ No resume text found")
                continue
            
            # Create training sample
            sample = {
                "id": i,
                "resume_text": resume_text,
                "expected_output": complete_json,
                "metadata": {
                    "created_at": datetime.now().isoformat(),
                    "source": "database_extraction",
                    "quality_score": 1.0,
                    "verified": True,
                    "format_type": "database_resume",
                    "industry": "extracted",
                    "job_id": job.id,
                    "created_at_job": job.created_at.isoformat() if job.created_at else None
                }
            }
            
            dataset.append(sample)
            print(f"  ✅ Sample created successfully")
            print(f"  📊 Work entries: {len(complete_json.get('work', []))}")
            print(f"  🎓 Education entries: {len(complete_json.get('education', []))}")
        
        # Save dataset
        if dataset:
            with open('database_resume_dataset.json', 'w', encoding='utf-8') as f:
                json.dump(dataset, f, indent=2, ensure_ascii=False)
            
            print(f"\n✅ Dataset saved to 'database_resume_dataset.json'")
            print(f"📊 Total samples: {len(dataset)}")
        
        return dataset
        
    except Exception as e:
        print(f"❌ Error extracting from database: {e}")
        return []
    
    finally:
        db.close()

def extract_specific_job(job_id: str):
    """Extract specific job from database"""
    
    print(f"🎯 Extracting Job {job_id} from Database")
    print("=" * 50)
    
    db = SessionLocal()
    
    try:
        # Get specific job
        job = db.query(ParsingJob).filter(ParsingJob.id == job_id).first()
        
        if not job:
            print(f"❌ Job {job_id} not found")
            return None
        
        # Get parsed data
        parsed_data = job.parsed_data or {}
        complete_json = parsed_data.get('complete_resume_json', {})
        
        if not complete_json:
            print(f"❌ No complete_resume_json found for job {job_id}")
            return None
        
        # Get resume text
        resume_text = job.raw_text or ""
        
        if not resume_text:
            print(f"❌ No resume text found for job {job_id}")
            return None
        
        # Create sample
        sample = {
            "id": 1,
            "resume_text": resume_text,
            "expected_output": complete_json,
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "source": "database_specific",
                "quality_score": 1.0,
                "verified": True,
                "format_type": "specific_job",
                "industry": "extracted",
                "job_id": job_id
            }
        }
        
        # Save sample
        with open(f'job_{job_id}_dataset.json', 'w', encoding='utf-8') as f:
            json.dump([sample], f, indent=2, ensure_ascii=False)
        
        print(f"✅ Job {job_id} dataset saved to 'job_{job_id}_dataset.json'")
        
        # Show structure
        print(f"\n📋 Job {job_id} Structure:")
        print(f"  📊 Work entries: {len(complete_json.get('work', []))}")
        print(f"  🎓 Education entries: {len(complete_json.get('education', []))}")
        print(f"  🔧 Skills entries: {len(complete_json.get('skills', []))}")
        print(f"  🏆 Certifications: {len(complete_json.get('certifications', []))}")
        
        return sample
        
    except Exception as e:
        print(f"❌ Error extracting job {job_id}: {e}")
        return None
    
    finally:
        db.close()

def show_database_summary():
    """Show summary of database content"""
    
    print("🎯 Database Summary")
    print("=" * 30)
    
    db = SessionLocal()
    
    try:
        jobs = db.query(ParsingJob).all()
        
        print(f"📊 Total jobs: {len(jobs)}")
        
        # Count jobs with complete_resume_json
        complete_json_count = 0
        for job in jobs:
            parsed_data = job.parsed_data or {}
            if parsed_data.get('complete_resume_json'):
                complete_json_count += 1
        
        print(f"📊 Jobs with complete_resume_json: {complete_json_count}")
        print(f"📊 Jobs without complete_resume_json: {len(jobs) - complete_json_count}")
        
        # Show recent jobs
        print(f"\n📋 Recent Jobs:")
        for job in jobs[-5:]:  # Last 5 jobs
            parsed_data = job.parsed_data or {}
            has_complete = "✅" if parsed_data.get('complete_resume_json') else "❌"
            print(f"  {has_complete} {job.id} - {job.created_at.strftime('%Y-%m-%d') if job.created_at else 'No date'}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    finally:
        db.close()

def main():
    """Main function"""
    print("🎯 Extract Resume Data from Database")
    print("=" * 60)
    
    # Show database summary
    show_database_summary()
    
    # Extract all jobs
    dataset = extract_from_database()
    
    print("\n✅ Database Extraction Complete!")
    print("📊 Files created:")
    print("  • database_resume_dataset.json - All extracted resumes")
    print("  • Ready for training your resume parser")

if __name__ == "__main__":
    main()
