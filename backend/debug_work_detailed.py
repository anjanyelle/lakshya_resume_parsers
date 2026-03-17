# -*- coding: utf-8 -*-
"""
Debug work experience detailed parsing
"""

import re

def debug_work_detailed():
    print('🔍 DEBUGGING WORK EXPERIENCE DETAILED PARSING')
    print('=' * 60)
    
    # Test with one job entry
    job_text = '''UnitedHealth Group (Client: Optum Analytics): October 2023 - Current (Location: Eden Prairie, MN (Remote))
Role: Sr. Data Engineer
Responsibilities:
•	Designed and deployed HIPAA-compliant AWS Glue and Apache Spark ETL pipelines ingesting 50M+ daily healthcare claims, member eligibility records, and clinical encounter data from HL7 FHIR APIs and EDI 837/835 feeds into an AWS S3 data lake partitioned by payer, date, and claim type.'''
    
    print('📄 Original Job Text:')
    print(job_text)
    print()
    
    # Extract first line
    first_line = job_text.split('\n')[0].strip()
    print(f'🔍 First Line: {first_line}')
    
    # Split by colon
    if ':' in first_line:
        company_part, rest = first_line.split(':', 1)
        print(f'  Company Part: {company_part.strip()}')
        print(f'  Rest Part: {rest.strip()}')
        
        # Test date/location patterns
        date_loc_patterns = [
            r'([A-Za-z]+\s+\d{4}\s*[–-]\s*(?:Current|[A-Za-z]+\s+\d{4}))\s*\((?:Location:\s*)?([^)]+)\)',
            r'([A-Za-z]+\s+\d{4}\s*[–-]\s*(?:Current|[A-Za-z]+\s+\d{4}))\s*\((?:Location:\s*)?([^)]+)\)',
            r'([A-Za-z]+\s+\d{4}\s*[–-]\s*(?:Current|[A-Za-z]+\s+\d{4}))\s*\(([^)]+)\)',
            r'([A-Za-z]+\s+\d{4}\s*[–-]\s*(?:Current|[A-Za-z]+\s+\d{4}))\s*\(([^)]+)\)'
        ]
        
        print(f'\n🔍 Testing {len(date_loc_patterns)} patterns:')
        for i, pattern in enumerate(date_loc_patterns):
            print(f'  Pattern {i+1}: {pattern}')
            match = re.search(pattern, rest.strip())
            if match:
                date_range = match.group(1).strip()
                location = match.group(2).strip()
                print(f'    ✅ Match Found:')
                print(f'      Date Range: {date_range}')
                print(f'      Location: {location}')
                if location.startswith('Location:'):
                    location = location.replace('Location:', '').strip()
                    print(f'      Cleaned Location: {location}')
                break
            else:
                print(f'    ❌ No Match')
    
    print()
    
    # Test with different formats
    test_cases = [
        'October 2023 - Current (Location: Eden Prairie, MN (Remote))',
        'June 2021 - September 2023 (Location: Columbus, OH)',
        'August 2019 - May 2021 (Location: Bentonville, AR)'
    ]
    
    print('🔍 Testing Different Date/Location Formats:')
    for i, test_case in enumerate(test_cases):
        print(f'  Test {i+1}: {test_case}')
        for j, pattern in enumerate(date_loc_patterns):
            match = re.search(pattern, test_case)
            if match:
                date_range = match.group(1).strip()
                location = match.group(2).strip()
                print(f'    ✅ Pattern {j+1}: Date="{date_range}", Location="{location}"')
                break
        print()

if __name__ == "__main__":
    debug_work_detailed()
