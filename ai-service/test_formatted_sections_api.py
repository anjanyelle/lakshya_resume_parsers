#!/usr/bin/env python3
"""
Quick test script to verify formatted_sections is in the API response.
This simulates what your frontend receives.
"""

import requests
import json
from pathlib import Path

# Test with a sample resume file
test_resume = "/Users/anjanyelle/Desktop/untitled folder 3/Lakshya-LLM-Resume-Parser/backend/src/uploads/59c089ee-782c-4a62-a00a-a42a42888112_Anjan_Yelles_Resume-2.pdf"

if Path(test_resume).exists():
    print("📄 Testing API response with resume file...")
    print(f"File: {test_resume}\n")
    
    # Make request to AI service
    response = requests.post(
        'http://localhost:8000/parse',
        json={
            'file_path': test_resume,
            'candidate_id': 'test-123'
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        
        print("✅ API Response received successfully!\n")
        
        # Check if formatted_sections exists
        if 'formatted_sections' in data:
            print("🎉 formatted_sections FOUND in API response!\n")
            
            formatted = data['formatted_sections']
            
            # Display section summary
            if 'section_summary' in formatted:
                print("📊 Section Summary:")
                for section, lines in formatted['section_summary'].items():
                    print(f"  • {section}: {lines} lines")
                print()
            
            # Display sections
            if 'sections' in formatted:
                print("📋 Detected Sections:")
                for section_name in formatted['sections'].keys():
                    print(f"  • {section_name}")
                print()
            
            # Display first section as example
            if 'sections' in formatted and formatted['sections']:
                first_section = list(formatted['sections'].items())[0]
                section_name, section_content = first_section
                print(f"📝 Example - {section_name} section (first 200 chars):")
                print(section_content[:200])
                print("...\n")
            
            # Show formatted text preview
            if 'formatted_text' in formatted:
                print("📄 Formatted Text Preview (first 300 chars):")
                print(formatted['formatted_text'][:300])
                print("...\n")
            
            print("=" * 80)
            print("✅ SUCCESS! formatted_sections is working correctly!")
            print("=" * 80)
            print("\nThis data is now available in your web UI.")
            print("Open your browser console (F12) and you'll see it logged there too!")
            
        else:
            print("❌ formatted_sections NOT FOUND in API response")
            print("\nAvailable keys in response:")
            print(list(data.keys()))
    else:
        print(f"❌ API request failed: {response.status_code}")
        print(response.text)
else:
    print(f"❌ Test resume file not found: {test_resume}")
    print("\nPlease update the test_resume path in this script to point to an actual resume file.")
