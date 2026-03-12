#!/usr/bin/env python3
"""
Test Enhanced Work Experience Parser for 100% Coverage
"""

import sys
import os
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'backend'))

from app.services.parser.work_experience_enhanced import EnhancedWorkExperienceParser
from app.services.parser.company_standardizer import CompanyStandardizer
import json

def test_all_formats():
    """Test all resume formats for 100% coverage"""
    
    parser = EnhancedWorkExperienceParser()
    standardizer = CompanyStandardizer()
    
    # Test cases for all formats
    test_cases = [
        {
            'name': 'Client/Role/Location Format',
            'text': '''PROFESSIONAL EXPERIENCE
Client: Nike | Location: Beaverton, OR
Role: Senior Developer | Jan 2022 - Current
• Developed web applications
• Led team of 5 developers

Client: Adidas | Location: Portland, OR
Role: Full Stack Developer | Mar 2020 - Dec 2021
• Built e-commerce platform
• Implemented CI/CD pipelines''',
            'expected_jobs': 2
        },
        {
            'name': 'Company/Role/Location Format',
            'text': '''PROFESSIONAL EXPERIENCE
Company: Microsoft | Location: Redmond, WA
Role: Software Engineer | Jun 2020 - Present
• Developed Windows applications
• Worked on Azure services

Company: Google | Location: Mountain View, CA
Role: Senior Engineer | Jan 2018 - May 2020
• Built search algorithms
• Improved system performance''',
            'expected_jobs': 2
        },
        {
            'name': 'Company: Date Range (Location) Format',
            'text': '''PROFESSIONAL EXPERIENCE
HCA Healthcare: November 2022 - Current (Location: Nashville, TN)
Site Reliability Engineer
• Designed HIPAA-compliant infrastructure
• Maintained 99.95% uptime

American Express: January 2020 - October 2022 (Location: New York, NY)
Site Reliability Engineer
• Built PCI-DSS compliant systems
• Led infrastructure team''',
            'expected_jobs': 2
        },
        {
            'name': 'Company (Client: ...) | Date | Location Format',
            'text': '''PROFESSIONAL EXPERIENCE
Cigna Health (Client: Express Scripts) | 2022 - Present | Bloomfield, CT
Principal QA Automation Architect
• Built enterprise testing framework
• Reduced test execution time

Goldman Sachs (Client: Marcus by Goldman Sachs) | 2019 - 2022 | New York, NY
Lead QA Automation Engineer
• Designed testing strategies
• Mentored junior engineers''',
            'expected_jobs': 2
        },
        {
            'name': '## Company: Date Range (Location) Format',
            'text': '''PROFESSIONAL EXPERIENCE
## HCA Healthcare: November 2022 - Current (Location: Nashville, TN)
Site Reliability Engineer
• Deployed cloud infrastructure
• Ensured system reliability

## American Express: January 2020 - October 2022 (Location: New York, NY)
Site Reliability Engineer
• Maintained trading systems
• Optimized performance''',
            'expected_jobs': 2
        },
        {
            'name': 'Standard Company | Title Format',
            'text': '''PROFESSIONAL EXPERIENCE
Apple Inc. | Senior Software Engineer | Cupertino, CA | 2020 - Present
• Developed iOS applications
• Led mobile team

Microsoft Corp. | Software Engineer | Redmond, WA | 2018 - 2020
• Built Windows features
• Collaborated with product teams''',
            'expected_jobs': 2
        },
        {
            'name': 'Bullet Company Date Format',
            'text': '''PROFESSIONAL EXPERIENCE
• Amazon.com | Jan 2021 - Present | Seattle, WA
Senior Cloud Architect
• Designed scalable systems
• Reduced infrastructure costs

• Facebook | Jun 2019 - Dec 2020 | Menlo Park, CA
Software Engineer
• Built social features
• Improved user experience''',
            'expected_jobs': 2
        },
        {
            'name': 'Dash Separated Format',
            'text': '''PROFESSIONAL EXPERIENCE
Senior Product Manager — Amazon — Jan 2020 - Present
• Launched new products
• Managed cross-functional teams

Software Engineer — Google — Jun 2018 - Dec 2019
• Developed search features
• Optimized algorithms''',
            'expected_jobs': 2
        },
        {
            'name': 'Slash Separated Format',
            'text': '''PROFESSIONAL EXPERIENCE
Data Scientist / Netflix / 2021 - Present
• Built recommendation systems
• Analyzed user behavior

Backend Engineer / Spotify / 2019 - 2021
• Developed music streaming features
• Improved system performance''',
            'expected_jobs': 2
        },
        {
            'name': 'Parentheses Location Format',
            'text': '''PROFESSIONAL EXPERIENCE
Twitter (San Francisco, CA) 2020 - Present
Senior Software Engineer
• Built real-time features
• Improved system scalability

Airbnb (San Francisco, CA) 2018 - 2020
Software Engineer
• Developed booking platform
• Enhanced user experience''',
            'expected_jobs': 2
        },
        {
            'name': 'At Company Format',
            'text': '''PROFESSIONAL EXPERIENCE
Senior Engineer at Apple Inc. (2020 - Present)
• Developed iOS features
• Led mobile initiatives

Developer at Microsoft Corp. (2018 - 2020)
• Built Windows applications
• Collaborated with product teams''',
            'expected_jobs': 2
        },
        {
            'name': 'From To Format',
            'text': '''PROFESSIONAL EXPERIENCE
From Jan 2020 to Present: Microsoft - Software Engineer
• Developed cloud services
• Improved system reliability

From Jun 2018 to Dec 2019: Google - Developer
• Built search features
• Optimized performance''',
            'expected_jobs': 2
        },
        {
            'name': 'Date Company Title Format',
            'text': '''PROFESSIONAL EXPERIENCE
2020 - Present: Apple Inc. | Senior Software Engineer
• Led iOS development
• Mentored junior engineers

2018 - 2020: Google | Software Engineer
• Built search infrastructure
• Improved algorithms''',
            'expected_jobs': 2
        },
        {
            'name': 'Company Location Date Format',
            'text': '''PROFESSIONAL EXPERIENCE
Apple Inc. | Cupertino, CA | 2020 - Present
Senior Software Engineer
• Developed iOS applications
• Led mobile team

Google | Mountain View, CA | 2018 - 2020
Software Engineer
• Built search features
• Optimized performance''',
            'expected_jobs': 2
        }
    ]
    
    print("🧪 Testing Enhanced Work Experience Parser")
    print("=" * 60)
    
    total_tests = len(test_cases)
    passed_tests = 0
    failed_tests = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 Test {i}/{total_tests}: {test_case['name']}")
        print("-" * 40)
        
        try:
            # Parse the text
            jobs = parser.parse_experience_section_enhanced(test_case['text'])
            
            # Check if expected number of jobs found
            if len(jobs) == test_case['expected_jobs']:
                print(f"✅ PASSED: Found {len(jobs)} jobs (expected {test_case['expected_jobs']})")
                passed_tests += 1
                
                # Show parsed jobs
                for j, job in enumerate(jobs, 1):
                    print(f"   Job {j}: {job.company} | {job.title} | {job.location}")
                    
                    # Test company standardization
                    standardized = standardizer.standardize_company(job.company)
                    if standardized['confidence'] > 0.8:
                        print(f"          📊 Standardized: {standardized['name']} (confidence: {standardized['confidence']:.2f})")
            else:
                print(f"❌ FAILED: Found {len(jobs)} jobs (expected {test_case['expected_jobs']})")
                failed_tests.append(test_case['name'])
                
        except Exception as e:
            print(f"❌ ERROR: {e}")
            failed_tests.append(test_case['name'])
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {len(failed_tests)}")
    print(f"Success Rate: {passed_tests/total_tests*100:.1f}%")
    
    if failed_tests:
        print(f"\n❌ Failed Tests:")
        for test in failed_tests:
            print(f"   • {test}")
    
    # Company standardizer statistics
    print(f"\n📈 Company Standardizer Stats:")
    stats = standardizer.get_statistics()
    print(f"   Total Companies: {stats['total_companies']}")
    print(f"   Fortune 500: {stats['fortune500_companies']}")
    print(f"   Sources: {list(stats['sources'].keys())}")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    success = test_all_formats()
    sys.exit(0 if success else 1)
