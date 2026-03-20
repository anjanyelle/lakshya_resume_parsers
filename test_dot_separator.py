#!/usr/bin/env python3

# Test script to verify dot separator parsing
import sys
import os

# Add the backend directory to Python path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

from simple_working_solution import parse_work_history_simple

# Test the problematic resume format
test_resume = '''Sr. Full Stack Java Developer · Tx(Citibank Irving, TX)

2019-05-01 → 2021-12-01

Sr. Java Developer · Il(Walgreens Deerfield, IL)

2016-08-01 → 2019-04-01'''

print('🎯 TESTING DOT SEPARATOR FORMAT')
print('=' * 50)

result = parse_work_history_simple(test_resume)

print(f'Format detected: {result.get("format_detected", "unknown")}')
print(f'Jobs found: {len(result.get("work_experience", []))}')

if result.get('work_experience'):
    for i, work in enumerate(result['work_experience'], 1):
        print(f'Job {i}:')
        print(f'  Company: {work.get("employer", "N/A")}')
        print(f'  Title: {work.get("job_title", "N/A")}')
        print(f'  Dates: {work.get("date_range", "N/A")}')
        print()

if result.get('format_detected') == 'dot_separator_format':
    print('✅ SUCCESS! Dot separator format is now working!')
else:
    print('❌ Still not detecting dot separator format correctly')
