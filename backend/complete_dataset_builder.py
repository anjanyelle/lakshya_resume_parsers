#!/usr/bin/env python3

"""
Complete Dataset Builder
All-in-one tool to create your resume dataset
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Any

class CompleteDatasetBuilder:
    """Complete dataset builder for your resumes"""
    
    def __init__(self):
        self.dataset = []
        self.output_file = "my_complete_resume_dataset.json"
    
    def add_resume_from_text(self, resume_text: str, metadata: Dict[str, Any] = None) -> bool:
        """Add resume from text"""
        
        if not resume_text or not resume_text.strip():
            print("❌ Empty resume text")
            return False
        
        try:
            from app.services.enhanced_pipeline_final import EnhancedResumePipelineFinal
            
            enhanced_pipeline = EnhancedResumePipelineFinal()
            parsed_result = enhanced_pipeline.parse_resume_complete(resume_text)
            
            sample = {
                "id": len(self.dataset) + 1,
                "resume_text": resume_text.strip(),
                "expected_output": parsed_result,
                "metadata": {
                    "created_at": datetime.now().isoformat(),
                    "source": "text_input",
                    "quality_score": 1.0,
                    "verified": True,
                    "format_type": "text_resume",
                    "industry": "general",
                    **(metadata or {})
                }
            }
            
            self.dataset.append(sample)
            print(f"✅ Resume added successfully (ID: {sample['id']})")
            return True
            
        except Exception as e:
            print(f"❌ Error parsing resume: {e}")
            return False
    
    def add_resume_from_file(self, file_path: str, metadata: Dict[str, Any] = None) -> bool:
        """Add resume from file"""
        
        if not os.path.exists(file_path):
            print(f"❌ File not found: {file_path}")
            return False
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                resume_text = f.read()
            
            file_metadata = {
                "file_path": file_path,
                "file_size": len(resume_text),
                "source": "file_input",
                **(metadata or {})
            }
            
            return self.add_resume_from_text(resume_text, file_metadata)
            
        except Exception as e:
            print(f"❌ Error reading file: {e}")
            return False
    
    def add_resumes_from_directory(self, directory: str, file_pattern: str = "*.txt") -> int:
        """Add all resumes from directory"""
        
        if not os.path.exists(directory):
            print(f"❌ Directory not found: {directory}")
            return 0
        
        import glob
        
        file_paths = glob.glob(os.path.join(directory, file_pattern))
        added_count = 0
        
        print(f"📁 Found {len(file_paths)} files in {directory}")
        
        for file_path in file_paths:
            print(f"\n📄 Processing: {os.path.basename(file_path)}")
            
            metadata = {
                "directory": directory,
                "file_pattern": file_pattern
            }
            
            if self.add_resume_from_file(file_path, metadata):
                added_count += 1
        
        print(f"\n✅ Added {added_count} resumes from directory")
        return added_count
    
    def add_from_database(self, limit: int = None) -> int:
        """Add resumes from database"""
        
        try:
            from app.core.database import SessionLocal
            from app.models import ParsingJob
            
            db = SessionLocal()
            
            # Query jobs
            query = db.query(ParsingJob)
            if limit:
                query = query.limit(limit)
            
            jobs = query.all()
            added_count = 0
            
            print(f"📊 Found {len(jobs)} jobs in database")
            
            for job in jobs:
                parsed_data = job.parsed_data or {}
                complete_json = parsed_data.get('complete_resume_json', {})
                resume_text = job.raw_text or ""
                
                if not complete_json or not resume_text:
                    continue
                
                sample = {
                    "id": len(self.dataset) + 1,
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
                
                self.dataset.append(sample)
                added_count += 1
                
                if added_count % 10 == 0:
                    print(f"📊 Processed {added_count} jobs...")
            
            db.close()
            
            print(f"✅ Added {added_count} resumes from database")
            return added_count
            
        except Exception as e:
            print(f"❌ Error accessing database: {e}")
            return 0
    
    def validate_dataset(self) -> bool:
        """Validate dataset structure"""
        
        if not self.dataset:
            print("❌ Empty dataset")
            return False
        
        required_keys = ['basics', 'work', 'education', 'skills', 'certifications', 'projects', 'languages', 'volunteer', 'references', 'achievements', 'publications']
        
        errors = []
        
        for i, sample in enumerate(self.dataset, 1):
            expected_output = sample.get('expected_output', {})
            
            # Check required keys
            missing_keys = [key for key in required_keys if key not in expected_output]
            if missing_keys:
                errors.append(f"Sample {i}: Missing keys {missing_keys}")
            
            # Check basics
            basics = expected_output.get('basics', {})
            if not basics.get('name'):
                errors.append(f"Sample {i}: Missing name")
            
            # Check data quality
            work = expected_output.get('work', [])
            education = expected_output.get('education', [])
            skills = expected_output.get('skills', [])
            
            if not work and not education and not skills:
                errors.append(f"Sample {i}: No meaningful data")
        
        if errors:
            print("❌ Validation errors:")
            for error in errors[:10]:  # Show first 10 errors
                print(f"  {error}")
            if len(errors) > 10:
                print(f"  ... and {len(errors) - 10} more errors")
            return False
        
        print("✅ Dataset validation passed!")
        return True
    
    def save_dataset(self, filename: str = None) -> bool:
        """Save dataset to file"""
        
        if not self.dataset:
            print("❌ Empty dataset")
            return False
        
        output_file = filename or self.output_file
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(self.dataset, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Dataset saved to '{output_file}'")
            print(f"📊 Total samples: {len(self.dataset)}")
            return True
            
        except Exception as e:
            print(f"❌ Error saving dataset: {e}")
            return False
    
    def show_summary(self):
        """Show dataset summary"""
        
        if not self.dataset:
            print("❌ Empty dataset")
            return
        
        print(f"📊 Dataset Summary:")
        print(f"  Total samples: {len(self.dataset)}")
        
        # Count by source
        sources = {}
        for sample in self.dataset:
            source = sample.get('metadata', {}).get('source', 'unknown')
            sources[source] = sources.get(source, 0) + 1
        
        print(f"  Sources: {sources}")
        
        # Count by format type
        formats = {}
        for sample in self.dataset:
            format_type = sample.get('metadata', {}).get('format_type', 'unknown')
            formats[format_type] = formats.get(format_type, 0) + 1
        
        print(f"  Format types: {formats}")
        
        # Show sample structure
        if self.dataset:
            sample = self.dataset[0]
            expected_output = sample.get('expected_output', {})
            
            print(f"  Sample structure:")
            print(f"    Keys: {list(expected_output.keys())}")
            print(f"    Work entries: {len(expected_output.get('work', []))}")
            print(f"    Education entries: {len(expected_output.get('education', []))}")
            print(f"    Skills entries: {len(expected_output.get('skills', []))}")

def main():
    """Main function"""
    print("🎯 Complete Dataset Builder")
    print("=" * 60)
    
    builder = CompleteDatasetBuilder()
    
    while True:
        print("\nChoose option:")
        print("1. Add resume from text")
        print("2. Add resume from file")
        print("3. Add resumes from directory")
        print("4. Add from database")
        print("5. Show summary")
        print("6. Validate dataset")
        print("7. Save dataset")
        print("8. Exit")
        
        choice = input("Enter choice (1-8): ").strip()
        
        if choice == "1":
            print("\n📝 Enter your resume text (press Enter twice to finish):")
            resume_lines = []
            while True:
                line = input()
                if line == "" and len(resume_lines) > 0 and resume_lines[-1] == "":
                    break
                resume_lines.append(line)
            
            resume_text = "\n".join(resume_lines).strip()
            builder.add_resume_from_text(resume_text)
            
        elif choice == "2":
            file_path = input("\nEnter file path: ").strip()
            builder.add_resume_from_file(file_path)
            
        elif choice == "3":
            directory = input("\nEnter directory path: ").strip()
            pattern = input("Enter file pattern (default: *.txt): ").strip() or "*.txt"
            builder.add_resumes_from_directory(directory, pattern)
            
        elif choice == "4":
            limit = input("Enter limit (leave empty for all): ").strip()
            limit = int(limit) if limit else None
            builder.add_from_database(limit)
            
        elif choice == "5":
            builder.show_summary()
            
        elif choice == "6":
            builder.validate_dataset()
            
        elif choice == "7":
            filename = input("Enter filename (default: my_complete_resume_dataset.json): ").strip()
            filename = filename if filename else None
            builder.save_dataset(filename)
            
        elif choice == "8":
            print("👋 Goodbye!")
            break
            
        else:
            print("❌ Invalid choice")

if __name__ == "__main__":
    main()
