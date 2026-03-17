#!/usr/bin/env python3
"""
Find Jogendra's resume data in database
"""

import os
import psycopg2
import json
from dotenv import load_dotenv

def find_jogendra_data():
    load_dotenv()
    db_url = os.getenv('DATABASE_URL').replace('postgresql+psycopg2://', 'postgresql://')
    conn = psycopg2.connect(db_url)
    cursor = conn.cursor()

    # Check table structure first
    cursor.execute('''
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'parsing_jobs' 
        ORDER BY ordinal_position
    ''')

    columns = cursor.fetchall()
    print('📋 Table Structure:')
    for col in columns:
        print(f'  {col[0]}: {col[1]}')

    # Get the latest parsing job
    cursor.execute('''
        SELECT id, parsed_data 
        FROM parsing_jobs 
        WHERE parsed_data::jsonb->'contact'->'name'->>'name' ILIKE '%Jogendra%'
        OR parsed_data::jsonb->'work'->0->>'jobTitle' ILIKE '%Site Reliability%'
        ORDER BY id DESC 
        LIMIT 1
    ''')

    result = cursor.fetchone()

    if result:
        job_id, parsed_data = result
        print('🎯 JOGENDRA AYATHA RESUME DATA FOUND!')
        print(f'🆔 Job ID: {job_id}')
        print(f'📊 JSON Keys: {list(parsed_data.keys())}')
        print(f'📊 Work Entries: {len(parsed_data.get("work", []))}')
        print(f'📊 Skills: {len(parsed_data.get("skills", []))}')
        
        # Show work experience structure
        work_data = parsed_data.get("work", [])
        if work_data:
            print('\n💼 WORK EXPERIENCE STRUCTURE:')
            for i, job in enumerate(work_data[:2]):  # Show first 2 jobs
                print(f'  Job {i+1}:')
                print(f'    company: {job.get("company", "NULL")}')
                print(f'    title: {job.get("jobTitle", "NULL")}')
                print(f'    location: {job.get("city", "NULL")}')
                print(f'    dates: {job.get("startDate", "NULL")} to {job.get("endDate", "NULL")}')
        
        # Show skills structure
        skills_data = parsed_data.get("skills", [])
        if skills_data:
            print('\n🔧 SKILLS STRUCTURE:')
            for i, skill in enumerate(skills_data[:5]):  # Show first 5 skills
                print(f'  Skill {i+1}:')
                print(f'    name: {skill.get("name", "NULL")}')
                print(f'    category: {skill.get("category", "NULL")}')
                print(f'    confidence: {skill.get("confidence", "NULL")}')
        
        # Show contact structure
        contact_data = parsed_data.get("contact", {})
        if contact_data:
            print('\n📞 CONTACT STRUCTURE:')
            print(f'  name: {contact_data.get("name", {})}')
            print(f'  email: {contact_data.get("emails", [])}')
            print(f'  phone: {contact_data.get("phones", [])}')
        
        # Show sections structure
        sections_data = parsed_data.get("sections", {})
        if sections_data:
            print('\n📋 SECTIONS STRUCTURE:')
            for section_key, section_data in sections_data.items():
                print(f'  {section_key}: {type(section_data)}')
        
        return job_id, parsed_data
    else:
        print('❌ No Jogendra data found')
        return None, None

    conn.close()

if __name__ == "__main__":
    find_jogendra_data()
