#!/usr/bin/env python3
"""
Download additional datasets for 100% work experience format coverage
"""

import os
import subprocess
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

def download_dataset(name: str, url: str, target_dir: str):
    """Download a dataset from GitHub"""
    print(f"📥 Downloading {name}...")
    target_path = Path("data/external") / target_dir
    
    try:
        if target_path.exists():
            print(f"  ✅ {name} already exists")
            return
            
        # Clone the repository
        result = subprocess.run(
            ["git", "clone", url, str(target_path)],
            capture_output=True,
            text=True,
            timeout=300  # 5 minutes timeout
        )
        
        if result.returncode == 0:
            print(f"  ✅ Successfully downloaded {name}")
        else:
            print(f"  ❌ Failed to download {name}: {result.stderr}")
            
    except Exception as e:
        print(f"  ❌ Error downloading {name}: {e}")

def main():
    """Download all additional datasets"""
    print("🚀 Downloading Additional Datasets for 100% Coverage")
    print("=" * 60)
    
    datasets = [
        {
            "name": "LinkedIn Resume Dataset",
            "url": "https://github.com/samwit/gitlinked-resumes-dataset.git",
            "target": "linkedin_resumes"
        },
        {
            "name": "Indeed Resume Dataset", 
            "url": "https://github.com/OmkarPathak/Resume-Matcher-Datasets.git",
            "target": "indeed_resumes"
        },
        {
            "name": "Tech Resume Collection",
            "url": "https://github.com/karpathy/resume.git",
            "target": "tech_resumes"
        },
        {
            "name": "Modern Resume Formats",
            "url": "https://github.com/datacreative/Resume-Parser-Dataset.git",
            "target": "modern_resumes"
        },
        {
            "name": "International Companies",
            "url": "https://github.com/finos/awesome-fintech-companies.git", 
            "target": "international_companies"
        }
    ]
    
    for dataset in datasets:
        download_dataset(**dataset)
        print()
    
    print("🎉 Download process completed!")
    print("\n📊 Summary of additional datasets:")
    print("  • LinkedIn Resume Dataset - Professional formats")
    print("  • Indeed Resume Dataset - Diverse industry formats")
    print("  • Tech Resume Collection - Startup/tech formats")
    print("  • Modern Resume Formats - Recent formatting trends")
    print("  • International Companies - Global company coverage")

if __name__ == "__main__":
    main()
