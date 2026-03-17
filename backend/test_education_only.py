#!/usr/bin/env python3
"""
Test education parsing only
"""

import sys
sys.path.append('app')
from app.services.enhanced_pipeline_final import EnhancedResumePipelineFinal
import re

def test_education_only():
    print('🧪 TESTING EDUCATION PARSING ONLY')
    print('=' * 60)
    
    # Test education text
    education_text = '''
EDUCATION:
•	Bachelor of Technology in Computer Science & Engineering at Koneru Lakshmaiah University 2010-2014
'''
    
    print(f'📄 Education Text:')
    print(education_text.strip())
    print()
    
    # Test patterns
    edu_patterns = [
        # Chandra's format: Bachelor of Technology in Computer Science & Engineering at Koneru Lakshmaiah University 2010-2014
        r'([A-Za-z\s]+(?:Bachelor|Master|PhD|Associate)[A-Za-z\s]*(?:in|of)[A-Za-z\s]*)\s+at\s+([A-Za-z\s]+(?:University|College|Institute|Technology)[A-Za-z\s]*)\s+(\d{4}[–-]\d{4})',
        # Rahul's format: Degree – University, Location, Date
        r'(.+?)\s*[–-]\s*(.+?)\s*,\s*(.+?)\s*,\s*(\d{4}[–-]\d{4})',
        # Backup pattern
        r'(.+?)\s*[–-]\s*(.+?)\s*,\s*(.+?)\s*,\s*(\d{4}[–-]\d{4})'
    ]
    
    print(f'🔍 Testing {len(edu_patterns)} patterns:')
    
    for i, pattern in enumerate(edu_patterns):
        print(f'\n  Pattern {i+1}: {pattern}')
        matches = re.findall(pattern, education_text)
        print(f'  Matches: {len(matches)}')
        for match in matches:
            print(f'    - {match}')
            if len(match) == 4:
                degree, university, location, date = match
                print(f'      Degree: {degree.strip()}')
                print(f'      University: {university.strip()}')
                print(f'      Location: {location.strip()}')
                print(f'      Date: {date.strip()}')
            elif len(match) == 3:
                degree, university, date = match
                print(f'      Degree: {degree.strip()}')
                print(f'      University: {university.strip()}')
                print(f'      Date: {date.strip()}')
    
    # Test with pipeline
    print('\n🤖 Testing with Pipeline:')
    pipeline = EnhancedResumePipelineFinal()
    education_entries = pipeline._extract_education(education_text)
    print(f'Total education entries: {len(education_entries)}')
    for i, edu in enumerate(education_entries):
        print(f'  Edu {i+1}: {edu}')

if __name__ == "__main__":
    test_education_only()
