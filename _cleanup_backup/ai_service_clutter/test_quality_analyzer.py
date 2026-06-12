#!/usr/bin/env python3
"""
Test script to verify TextQualityAnalyzer is working correctly.
"""

import sys
sys.path.insert(0, '/Users/anjanyelle/Desktop/untitled folder 3/Lakshya-LLM-Resume-Parser/ai-service')

from parsers.text_quality_analyzer import TextQualityAnalyzer

# Sample data
original_text = """
John Doe
john.doe@email.com
+1234567890

PROFESSIONAL EXPERIENCE
Senior Software Engineer at Google
January 2020 - Present
• Developed scalable microservices using Python and Go
• Led team of 5 engineers
• Improved system performance by 40%

Software Engineer at Microsoft
June 2018 - December 2019
• Built cloud infrastructure using Azure
• Implemented CI/CD pipelines

EDUCATION
Bachelor of Science in Computer Science
Stanford University
2014 - 2018

SKILLS
Python, Java, Go, Docker, Kubernetes, AWS, Azure
"""

parsed_data = {
    'name': 'John Doe',
    'email': 'john.doe@email.com',
    'phone': '+1234567890',
    'skills': ['Python', 'Java', 'Go', 'Docker', 'Kubernetes'],
    'work_experience': [
        {
            'job_title': 'Senior Software Engineer',
            'company_name': 'Google',
            'description': 'Developed scalable microservices',
            'start_date': '2020-01-01',
            'end_date': None,
            'is_current': True
        },
        {
            'job_title': 'Software Engineer',
            'company_name': 'Microsoft',
            'description': 'Built cloud infrastructure',
            'start_date': '2018-06-01',
            'end_date': '2019-12-31',
            'is_current': False
        }
    ],
    'education': [
        {
            'degree': 'Bachelor of Science',
            'field_of_study': 'Computer Science',
            'institution': 'Stanford University',
            'start_year': 2014,
            'end_year': 2018
        }
    ]
}

sections = {
    'experience': 'Senior Software Engineer at Google...',
    'education': 'Bachelor of Science in Computer Science...',
    'skills': 'Python, Java, Go, Docker, Kubernetes, AWS, Azure'
}

# Test the analyzer
print("=" * 60)
print("Testing TextQualityAnalyzer")
print("=" * 60)

analyzer = TextQualityAnalyzer()
quality_report = analyzer.analyze_extraction_quality(original_text, parsed_data, sections)

print("\n📊 EXTRACTION QUALITY REPORT:")
print(f"  Extraction Quality: {quality_report['extraction_quality_percentage']}%")
print(f"  Text Similarity: {quality_report['text_similarity_percentage']}%")
print(f"  Text Loss: {quality_report['text_loss_percentage']}%")
print(f"  Missing Keywords: {len(quality_report['missing_keywords'])} keywords")
print(f"  Top 10 Missing: {quality_report['missing_keywords'][:10]}")
print(f"  Missing Sections: {quality_report['missing_sections']}")
print(f"  Structure Loss: {quality_report['structure_loss']}")
print(f"  Recommendation: {quality_report['recommendation']}")

print("\n📈 METRICS:")
for key, value in quality_report['metrics'].items():
    print(f"  {key}: {value}")

print("\n✅ Test completed successfully!")
