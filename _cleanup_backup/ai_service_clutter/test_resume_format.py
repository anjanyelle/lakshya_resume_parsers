#!/usr/bin/env python3
"""
Test with your actual resume format
"""

from test_model_accuracy import test_model_with_text

def test_resume_format():
    """Test with your actual resume format"""
    
    examples = [
        # Your actual resume format
        "Software Developer\nLalataksha Consulting Services Pvt Ltd\nJan 2024 - Present\nDeveloped and maintained web applications using React.js",
        
        "React Developer\nGatnix Technologies Pvt Ltd\nJun 2022 - Dec 2023\nImplemented dynamic forms and dashboards",
        
        "Junior Web Developer\nDisha IT Consultant\nApr 2021 - May 2022\nBuilt static and dynamic web pages",
        
        # Education format
        "Bachelor of Technology\nComputer Science Engineering\nYour College Name\n2017 - 2021",
        
        # Test variations
        "Senior Software Engineer\nMicrosoft Corporation\nSeattle, WA\nJan 2020 - Present\nLed development of cloud applications",
        
        "Data Scientist\nAmazon Web Services\nSan Francisco, CA\nJun 2018 - Dec 2019\nBuilt machine learning models"
    ]
    
    print("="*80)
    print("TESTING YOUR RESUME FORMAT")
    print("="*80)
    
    for i, example in enumerate(examples, 1):
        print(f"\n{'='*80}")
        print(f"EXAMPLE {i}:")
        print(f"{'='*80}")
        print(example)
        print("-" * 80)
        
        entities = test_model_with_text(example, show_details=False)
        
        # Check for key entities
        companies = [e['text'] for e in entities if e['label'] == 'COMPANY']
        roles = [e['text'] for e in entities if e['label'] == 'ROLE']
        dates = [e['text'] for e in entities if e['label'] in ['START_DATE', 'END_DATE']]
        
        print(f"\nKey Extracted:")
        print(f"  Companies: {companies}")
        print(f"  Roles: {roles}")
        print(f"  Dates: {dates}")
        
        print("\n" + "="*80)
        input("Press Enter to continue...")

if __name__ == "__main__":
    test_resume_format()
