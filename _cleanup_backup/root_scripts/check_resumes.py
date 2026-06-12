#!/usr/bin/env python3
"""
Check how many unique resumes were actually labeled in Label Studio
"""

import json
import os

# Check each JSON file
files = ['37_label.json', 'project-11-at-2026-04-03-09-38-4ee4e2ef.json', 'project-12-at-2026-04-03-09-49-b617be70.json']

total_unique_resumes = set()

for file in files:
    file_path = f'data/raw/{file}'
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
            
        # Collect unique IDs
        ids = set()
        if isinstance(data, list):
            for item in data:
                if 'id' in item:
                    ids.add(item['id'])
                else:
                    # If no ID, use index as unique identifier
                    ids.add(f'{file}_{data.index(item)}')
        
        print(f'{file}:')
        print(f'  Total entries: {len(data)}')
        print(f'  Unique IDs: {len(ids)}')
        print(f'  Sample IDs: {list(ids)[:5]}')
        
        total_unique_resumes.update(ids)
        print()
        
    except Exception as e:
        print(f'{file}: Error - {e}')

print(f'TOTAL UNIQUE RESUMES ACROSS ALL FILES: {len(total_unique_resumes)}')

# Also check if these are multiple annotations per resume
print("\nChecking if these are multiple annotations per resume...")
for file in files[:1]:  # Check first file
    file_path = f'data/raw/{file}'
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
            
        if isinstance(data, list) and len(data) > 0:
            # Check first few items
            print(f"\n{file} - First 3 entries:")
            for i, item in enumerate(data[:3]):
                print(f"  Entry {i+1}:")
                print(f"    ID: {item.get('id', 'No ID')}")
                print(f"    Text length: {len(item.get('text', ''))}")
                print(f"    Labels: {len(item.get('label', []))}")
                if item.get('label'):
                    print(f"    Sample label: {item['label'][0].get('labels', ['No label'])[0] if item['label'] else 'No labels'}")
                print()
                
    except Exception as e:
        print(f'Error checking {file}: {e}')
