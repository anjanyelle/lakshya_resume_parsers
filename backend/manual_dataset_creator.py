#!/usr/bin/env python3

"""
Manual Dataset Creator
Create your own dataset by manually entering data
"""

import json
from datetime import datetime

def create_manual_dataset():
    """Create dataset manually"""
    
    print("🎯 Manual Dataset Creator")
    print("=" * 40)
    
    # Get resume text
    print("📝 Enter your resume text (press Enter twice to finish):")
    
    resume_lines = []
    while True:
        line = input()
        if line == "" and len(resume_lines) > 0 and resume_lines[-1] == "":
            break
        resume_lines.append(line)
    
    resume_text = "\n".join(resume_lines).strip()
    
    if not resume_text:
        print("❌ No resume text provided")
        return
    
    print(f"\n📊 Resume text length: {len(resume_text)} characters")
    
    # Parse with enhanced pipeline
    try:
        from app.services.enhanced_pipeline_final import EnhancedResumePipelineFinal
        
        enhanced_pipeline = EnhancedResumePipelineFinal()
        parsed_result = enhanced_pipeline.parse_resume_complete(resume_text)
        
        print("✅ Resume parsed successfully!")
        print(f"📊 Sections found: {list(parsed_result.keys())}")
        
    except Exception as e:
        print(f"❌ Error parsing resume: {e}")
        return
    
    # Create dataset
    sample = {
        "id": 1,
        "resume_text": resume_text,
        "expected_output": parsed_result,
        "metadata": {
            "created_at": datetime.now().isoformat(),
            "source": "manual_input",
            "quality_score": 1.0,
            "verified": True,
            "format_type": "manual_resume",
            "industry": "manual"
        }
    }
    
    # Save dataset
    with open('manual_resume_dataset.json', 'w', encoding='utf-8') as f:
        json.dump([sample], f, indent=2, ensure_ascii=False)
    
    print("✅ Dataset saved to 'manual_resume_dataset.json'")
    
    # Show structure
    print("\n📋 Your Parsed Structure:")
    print("-" * 30)
    print(json.dumps(parsed_result, indent=2)[:1000] + "...")
    
    return [sample]

def create_batch_manual_dataset():
    """Create multiple manual entries"""
    
    print("🎯 Batch Manual Dataset Creator")
    print("=" * 40)
    
    dataset = []
    sample_id = 1
    
    while True:
        print(f"\n📝 Sample {sample_id} (press 'q' to quit):")
        
        # Get resume text
        print("Enter resume text (press Enter twice to finish):")
        
        resume_lines = []
        while True:
            line = input()
            if line.lower() == 'q':
                break
            if line == "" and len(resume_lines) > 0 and resume_lines[-1] == "":
                break
            resume_lines.append(line)
        
        if line.lower() == 'q':
            break
        
        resume_text = "\n".join(resume_lines).strip()
        
        if not resume_text:
            print("❌ No resume text provided, skipping...")
            continue
        
        # Parse resume
        try:
            from app.services.enhanced_pipeline_final import EnhancedResumePipelineFinal
            
            enhanced_pipeline = EnhancedResumePipelineFinal()
            parsed_result = enhanced_pipeline.parse_resume_complete(resume_text)
            
            print("✅ Resume parsed successfully!")
            
            # Create sample
            sample = {
                "id": sample_id,
                "resume_text": resume_text,
                "expected_output": parsed_result,
                "metadata": {
                    "created_at": datetime.now().isoformat(),
                    "source": "manual_batch",
                    "quality_score": 1.0,
                    "verified": True,
                    "format_type": "manual_batch_resume",
                    "industry": "manual_batch"
                }
            }
            
            dataset.append(sample)
            sample_id += 1
            
            print(f"✅ Sample {sample_id-1} added to dataset")
            
        except Exception as e:
            print(f"❌ Error parsing resume: {e}")
            continue
    
    # Save dataset
    if dataset:
        with open('manual_batch_dataset.json', 'w', encoding='utf-8') as f:
            json.dump(dataset, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Batch dataset saved to 'manual_batch_dataset.json'")
        print(f"📊 Total samples: {len(dataset)}")
    
    return dataset

def create_from_file():
    """Create dataset from text file"""
    
    print("🎯 Create Dataset from File")
    print("=" * 40)
    
    # Get file path
    file_path = input("Enter path to your resume text file: ").strip()
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            resume_text = f.read()
        
        print(f"✅ File loaded: {len(resume_text)} characters")
        
        # Parse resume
        try:
            from app.services.enhanced_pipeline_final import EnhancedResumePipelineFinal
            
            enhanced_pipeline = EnhancedResumePipelineFinal()
            parsed_result = enhanced_pipeline.parse_resume_complete(resume_text)
            
            print("✅ Resume parsed successfully!")
            
            # Create dataset
            sample = {
                "id": 1,
                "resume_text": resume_text,
                "expected_output": parsed_result,
                "metadata": {
                    "created_at": datetime.now().isoformat(),
                    "source": "file_input",
                    "quality_score": 1.0,
                    "verified": True,
                    "format_type": "file_resume",
                    "industry": "file",
                    "file_path": file_path
                }
            }
            
            # Save dataset
            with open('file_resume_dataset.json', 'w', encoding='utf-8') as f:
                json.dump([sample], f, indent=2, ensure_ascii=False)
            
            print("✅ Dataset saved to 'file_resume_dataset.json'")
            
            return [sample]
            
        except Exception as e:
            print(f"❌ Error parsing resume: {e}")
            return []
            
    except FileNotFoundError:
        print(f"❌ File not found: {file_path}")
        return []
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return []

def main():
    """Main function"""
    print("🎯 Manual Dataset Creator")
    print("=" * 60)
    
    print("Choose option:")
    print("1. Create single manual dataset")
    print("2. Create batch manual dataset")
    print("3. Create from text file")
    print("4. Exit")
    
    choice = input("Enter choice (1-4): ").strip()
    
    if choice == "1":
        create_manual_dataset()
    elif choice == "2":
        create_batch_manual_dataset()
    elif choice == "3":
        create_from_file()
    elif choice == "4":
        print("👋 Goodbye!")
    else:
        print("❌ Invalid choice")

if __name__ == "__main__":
    main()
