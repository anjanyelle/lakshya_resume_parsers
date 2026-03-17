#!/usr/bin/env python3
"""
Simple check for Jogendra's JSON data
"""

import os
import psycopg2
import json
from dotenv import load_dotenv

def check_json_simple():
    load_dotenv()
    db_url = os.getenv('DATABASE_URL').replace('postgresql+psycopg2://', 'postgresql://')
    conn = psycopg2.connect(db_url)
    cursor = conn.cursor()

    # Get Jogendra's data
    cursor.execute('''
        SELECT parsed_data 
        FROM parsing_jobs 
        WHERE parsed_data->'contact'->'name'->>'name' ILIKE '%Jogendra%'
        ORDER BY id DESC 
        LIMIT 1
    ''')

    result = cursor.fetchone()

    if result:
        parsed_data = result[0]
        print('🎯 JOGENDRA JSON ANALYSIS:')
        print(f'📊 Total keys: {list(parsed_data.keys())}')
        
        # Check for complete_resume_json
        complete_json = parsed_data.get('complete_resume_json')
        if complete_json:
            print(f'✅ complete_resume_json EXISTS: {len(str(complete_json))} chars')
        else:
            print('❌ complete_resume_json MISSING')
        
        # Check main sections
        print('\n📋 MAIN SECTIONS:')
        main_sections = ['work', 'skills', 'education', 'contact']
        for section in main_sections:
            data = parsed_data.get(section)
            if data:
                if isinstance(data, list):
                    print(f'  ✅ {section}: {len(data)} items')
                else:
                    print(f'  ✅ {section}: {type(data)}')
            else:
                print(f'  ❌ {section}: MISSING')
        
        # Show where complete_resume_json would be written
        print('\n🔍 WHERE COMPLETE_RESUME_JSON WOULD BE WRITTEN:')
        print('  In pipeline.py around line 3226-3231:')
        print('  if complete_json:')
        print('      parsed_update["complete_resume_json"] = complete_json')
        print('  else:')
        print('      parsed_update["complete_resume_json"] = None')
        
    else:
        print('❌ No Jogendra data found')

    conn.close()

if __name__ == "__main__":
    check_json_simple()
