#!/usr/bin/env python3

import psycopg2
import json
from app.core.config import get_settings

def check_complete_json():
    settings = get_settings()
    
    # Fix DATABASE_URL format for psycopg2
    db_url = settings.DATABASE_URL
    if db_url.startswith('postgresql+psycopg2://'):
        db_url = db_url.replace('postgresql+psycopg2://', 'postgresql://')
    conn = psycopg2.connect(db_url)
    cursor = conn.cursor()
    
    # Get the latest parsing job
    cursor.execute('''
        SELECT parsed_data 
        FROM public.parsing_jobs 
        ORDER BY started_at DESC 
        LIMIT 1
    ''')
    result = cursor.fetchone()
    
    if result:
        parsed_data = result[0]
        complete_json = parsed_data.get('complete_resume_json', {})
        
        print("=== COMPLETE RESUME JSON ANALYSIS ===")
        print(f"Total sections: {len(complete_json)}")
        print(f"Sections: {list(complete_json.keys())}")
        
        work_data = complete_json.get('work', [])
        print(f"\n=== WORK EXPERIENCE ===")
        print(f"Total work entries: {len(work_data)}")
        
        for i, entry in enumerate(work_data[:3]):  # Show first 3 entries
            print(f"\nEntry {i+1}:")
            print(f"  Company: {entry.get('company', 'MISSING')}")
            print(f"  Title: {entry.get('title', 'MISSING')}")
            print(f"  Start: {entry.get('startDate', 'MISSING')}")
            print(f"  End: {entry.get('endDate', 'MISSING')}")
            print(f"  Location: {entry.get('location', 'MISSING')}")
            print(f"  Description length: {len(entry.get('description', ''))}")
        
        # Check other data sources
        print(f"\n=== OTHER DATA SOURCES ===")
        print(f"work_experience count: {len(parsed_data.get('work_experience', []))}")
        print(f"work count: {len(parsed_data.get('work', []))}")
        
    else:
        print("No data found")
    
    conn.close()

if __name__ == "__main__":
    check_complete_json()
