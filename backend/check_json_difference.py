#!/usr/bin/env python3
"""
Check difference between parsed_data and complete_resume_json
"""

import os
import psycopg2
import json
from dotenv import load_dotenv

def check_json_difference():
    load_dotenv()
    db_url = os.getenv('DATABASE_URL').replace('postgresql+psycopg2://', 'postgresql://')
    conn = psycopg2.connect(db_url)
    cursor = conn.cursor()

    # Get Jogendra's data
    cursor.execute('''
        SELECT parsed_data 
        FROM parsing_jobs 
        WHERE id = '61da6913-39c2-408a-9bf8-f2c749c68e3e'
    ''')

    result = cursor.fetchone()

    if result:
        parsed_data = result[0]
        print('🎯 ANALYZING PARSED_DATA:')
        print(f'📊 parsed_data keys: {list(parsed_data.keys())}')
        print(f'📏 parsed_data size: {len(str(parsed_data))} chars')
        
        # Check if complete_resume_json exists in parsed_data
        complete_json = parsed_data.get('complete_resume_json')
        if complete_json:
            print(f'📊 complete_resume_json keys: {list(complete_json.keys())}')
            print(f'🤔 Are they identical? {parsed_data == complete_json}')
            print(f'📏 complete_json size: {len(str(complete_json))} chars')
        else:
            print('❌ complete_resume_json is missing from parsed_data')
            
            # Check specific sections
            print('\n📋 SECTION ANALYSIS:')
            sections_to_check = ['work', 'skills', 'education', 'contact']
            
            for section in sections_to_check:
                parsed_section = parsed_data.get(section, 'MISSING')
                print(f'  {section}: {type(parsed_section)} - {len(parsed_section) if isinstance(parsed_section, list) else "N/A"} items')
    else:
        print('❌ No Jogendra data found')

    conn.close()

if __name__ == "__main__":
    check_json_difference()
