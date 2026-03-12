#!/usr/bin/env python3
"""
Download and organize datasets for enhanced resume parser
"""

import os
import requests
import subprocess
from pathlib import Path

def create_directory_structure():
    """Create the required directory structure"""
    
    base_path = Path("data/external")
    
    directories = [
        "work_experience",
        "certifications", 
        "companies",
        "skills",
        "mappings"
    ]
    
    for directory in directories:
        dir_path = base_path / directory
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"Created directory: {dir_path}")

def download_direct_csv_files():
    """Download CSV files directly from GitHub"""
    
    downloads = {
        "data/external/certifications/coursera_courses.csv": 
            "https://raw.githubusercontent.com/Siddharth1698/Coursera-Course-Dataset/master/UCoursera_Courses.csv",
        
        "data/external/certifications/edx_courses.csv":
            "https://raw.githubusercontent.com/MainakRepositor/Datasets/master/EdX.csv"
    }
    
    for file_path, url in downloads.items():
        try:
            print(f"Downloading {file_path}...")
            response = requests.get(url)
            response.raise_for_status()
            
            # Create directory if it doesn't exist
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'wb') as f:
                f.write(response.content)
            
            print(f"✓ Downloaded: {file_path}")
            
        except Exception as e:
            print(f"✗ Failed to download {url}: {e}")

def clone_github_repositories():
    """Clone GitHub repositories"""
    
    repos = {
        "data/external/work_experience/resume_classification_dataset":
            "https://github.com/noran-mohamed/Resume-Classification-Dataset.git",
        
        "data/external/companies/fortune500_companies":
            "https://github.com/cmusam/fortune500.git",
        
        "data/external/certifications/awesome_certificates":
            "https://github.com/PanXProject/awesome-certificates.git",
        
        "data/external/certifications/free_certifications":
            "https://github.com/cloudcommunity/Free-Certifications.git",
        
        "data/external/skills/job_description_matching":
            "https://github.com/binoydutt/Resume-Job-Description-Matching.git"
    }
    
    for target_dir, repo_url in repos.items():
        try:
            print(f"Cloning {repo_url}...")
            
            # Create parent directory if it doesn't exist
            Path(target_dir).parent.mkdir(parents=True, exist_ok=True)
            
            # Clone the repository
            result = subprocess.run(
                ["git", "clone", repo_url, target_dir],
                capture_output=True,
                text=True,
                cwd="."
            )
            
            if result.returncode == 0:
                print(f"✓ Cloned: {target_dir}")
            else:
                print(f"✗ Failed to clone {repo_url}: {result.stderr}")
                
        except Exception as e:
            print(f"✗ Error cloning {repo_url}: {e}")

def extract_important_files():
    """Extract and rename important CSV files from cloned repositories"""
    
    file_mappings = {
        # From Resume Classification Dataset
        "data/external/work_experience/resume_classification_dataset.csv":
            "data/external/work_experience/resume_classification_dataset/Resume.csv",
        
        # From Fortune 500
        "data/external/companies/fortune500_2019.csv":
            "data/external/companies/fortune500_companies/csv/2019.csv",
        
        # From Job Description Matching
        "data/external/skills/job_matching_skills.csv":
            "data/external/skills/job_description_matching/data.csv"
    }
    
    for target_file, source_file in file_mappings.items():
        source_path = Path(source_file)
        target_path = Path(target_file)
        
        if source_path.exists():
            try:
                # Create target directory if needed
                target_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Copy file
                import shutil
                shutil.copy2(source_path, target_path)
                print(f"✓ Extracted: {target_file}")
                
            except Exception as e:
                print(f"✗ Failed to extract {source_file}: {e}")
        else:
            print(f"⚠ Source file not found: {source_file}")

def create_sample_certification_data():
    """Create a sample certification CSV if downloads fail"""
    
    sample_data = """certification_name,issuer,level,skills_covered,industry
AWS Certified Solutions Architect,Amazon Web Services,Professional,"Cloud Architecture,AWS,DevOps",Technology
Google Cloud Professional Architect,Google,Professional,"Cloud Computing,GCP,Infrastructure",Technology
Microsoft Azure Fundamentals,Microsoft,Fundamental,"Azure,Cloud Basics,Microsoft",Technology
CompTIA A+,CompTIA,Fundamental,"Hardware,Software,Troubleshooting",Technology
PMP,PMI,Professional,"Project Management,Leadership,Planning",Business
Certified ScrumMaster,Scrum Alliance,Professional,"Agile,Scrum,Team Management",Business
IBM Data Science Professional,IBM,Professional,"Data Science,Python,Machine Learning",Data Science
Google Data Analytics,Google,Fundamental,"Data Analysis,SQL,Spreadsheet",Data Science
"""
    
    file_path = "data/external/certifications/sample_certifications.csv"
    
    try:
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w') as f:
            f.write(sample_data)
        print(f"✓ Created sample certification data: {file_path}")
    except Exception as e:
        print(f"✗ Failed to create sample data: {e}")

def main():
    """Main function to download and organize all datasets"""
    
    print("🚀 Setting up datasets for Enhanced Resume Parser...")
    print("=" * 60)
    
    # Step 1: Create directory structure
    print("\n📁 Creating directory structure...")
    create_directory_structure()
    
    # Step 2: Download direct CSV files
    print("\n📥 Downloading direct CSV files...")
    download_direct_csv_files()
    
    # Step 3: Clone GitHub repositories
    print("\n🔄 Cloning GitHub repositories...")
    clone_github_repositories()
    
    # Step 4: Extract important files
    print("\n📋 Extracting important files...")
    extract_important_files()
    
    # Step 5: Create sample data if needed
    print("\n📝 Creating sample certification data...")
    create_sample_certification_data()
    
    print("\n" + "=" * 60)
    print("✅ Dataset setup completed!")
    print("\n📊 Final directory structure:")
    print("data/external/")
    print("├── work_experience/")
    print("│   ├── resume_classification_dataset.csv")
    print("│   └── resume_classification_dataset/ (cloned repo)")
    print("├── certifications/")
    print("│   ├── coursera_courses.csv")
    print("│   ├── edx_courses.csv")
    print("│   ├── sample_certifications.csv")
    print("│   ├── awesome_certificates/ (cloned repo)")
    print("│   └── free_certifications/ (cloned repo)")
    print("├── companies/")
    print("│   ├── fortune500_2019.csv")
    print("│   └── fortune500_companies/ (cloned repo)")
    print("├── skills/")
    print("│   ├── job_matching_skills.csv")
    print("│   └── job_description_matching/ (cloned repo)")
    print("└── mappings/ (empty - for generated mappings)")
    
    print("\n🎯 Ready to run the enhanced resume parser!")

if __name__ == "__main__":
    main()
