#!/usr/bin/env python3
"""
Setup script for accuracy testing framework
Creates test dataset structure and sample ground truth data
"""

import json
import os
from pathlib import Path

def create_test_dataset_structure():
    """Create the test dataset directory structure."""
    base_dir = Path("test_dataset")
    
    # Create directories
    directories = [
        "resumes/simple_resumes",
        "resumes/complex_resumes", 
        "resumes/multilingual_resumes",
        "resumes/image_resumes",
        "resumes/entry_level_resumes",
        "resumes/executive_resumes",
        "resumes/edge_cases",
        "ground_truth"
    ]
    
    for directory in directories:
        (base_dir / directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created: {base_dir / directory}")

def create_sample_ground_truth():
    """Create sample ground truth data for testing."""
    
    sample_ground_truth = {
        "sample_resume_001": {
            "raw_text": "John Doe\njohn.doe@email.com\n+1-555-123-4567\n\nExperience:\nSoftware Engineer at Tech Corp\nJanuary 2020 - Present\nDeveloped scalable web applications using Python and React\n\nEducation:\nBachelor of Science in Computer Science\nUniversity of Technology\n2016 - 2020",
            "sections": {
                "Experience": "Software Engineer at Tech Corp\nJanuary 2020 - Present\nDeveloped scalable web applications using Python and React",
                "Education": "Bachelor of Science in Computer Science\nUniversity of Technology\n2016 - 2020"
            },
            "name": "John Doe",
            "email": "john.doe@email.com",
            "phone": "+1-555-123-4567",
            "work_experience": [
                {
                    "company": "Tech Corp",
                    "job_title": "Software Engineer",
                    "start_date": "01/2020",
                    "end_date": "12/2024",
                    "description": "Developed scalable web applications using Python and React",
                    "location": ""
                }
            ],
            "education": [
                {
                    "institution": "University of Technology",
                    "degree": "Bachelor's",
                    "field_of_study": "Computer Science",
                    "start_date": "09/2016",
                    "end_date": "05/2020",
                    "gpa": "",
                    "location": ""
                }
            ],
            "skills": ["Python", "React", "Web Development"]
        }
    }
    
    # Save ground truth files
    ground_truth_dir = Path("test_dataset/ground_truth")
    
    with open(ground_truth_dir / "simple_resumes_gt.json", "w") as f:
        json.dump(sample_ground_truth, f, indent=2)
    
    print(f"✅ Created sample ground truth: {ground_truth_dir / 'simple_resumes_gt.json'}")

def create_test_runner_script():
    """Create a script to run accuracy tests."""
    script_content = '''#!/usr/bin/env python3
"""
Run accuracy tests against ground truth data
"""

import sys
sys.path.insert(0, '/path/to/ai-service')

from parsers.master_parser import MasterParser
from utils.accuracy_tester import AccuracyTester
import json

def main():
    # Initialize parser and tester
    parser = MasterParser()
    tester = AccuracyTester(parser)
    
    # Run test suite
    results = tester.run_test_suite(
        'test_dataset/resumes',
        'test_dataset/ground_truth/simple_resumes_gt.json'
    )
    
    # Generate report
    report_path = tester.generate_report()
    
    print(f"✅ Accuracy tests completed")
    print(f"📄 Report saved to: {report_path}")
    print(f"📊 Success rate: {results['aggregate_metrics']['success_rate']:.2%}")
    print(f"🎯 Average accuracy: {results['aggregate_metrics']['average_overall_accuracy']:.2%}")

if __name__ == '__main__':
    main()
'''
    
    script_path = Path("scripts/run_accuracy_tests.py")
    with open(script_path, "w") as f:
        f.write(script_content)
    
    # Make executable
    os.chmod(script_path, 0o755)
    print(f"✅ Created test runner: {script_path}")

def main():
    print("🚀 Setting up accuracy testing framework...")
    
    create_test_dataset_structure()
    create_sample_ground_truth()
    create_test_runner_script()
    
    print("\n✅ Accuracy testing framework setup complete!")
    print("\nNext steps:")
    print("1. Add your resume files to test_dataset/resumes/ directories")
    print("2. Create ground truth data in test_dataset/ground_truth/")
    print("3. Run: python scripts/run_accuracy_tests.py")

if __name__ == "__main__":
    main()
