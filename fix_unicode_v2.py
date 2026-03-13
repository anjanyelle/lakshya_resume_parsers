#!/usr/bin/env python3

# Read the file with error handling for unicode
try:
    with open('c:\\Users\\Rajes\\OneDrive\\Desktop\\Lakshya_Resume_paser_NEW!\\Lakshya-LLM-Resume-Parser\\backend\\app\\services\\parser\\work_experience_parser.py', 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()
    
    # Replace the problematic unicode dash character with standard dash
    # Replace any problematic dash characters with standard dash
    content = content.replace('[:\\-\\-]', '[:\\-\\-–]')
    content = content.replace('[:\\-\\-–]', '[:\\-\\-–]')
    content = content.replace('[\\-\\-]', '[\\-\\-–]')
    
    # Also fix any other problematic unicode patterns
    content = content.replace('[:\\-\\-–]', '[:\\-\\-–]')
    content = content.replace('[:\\-\\-–]', '[:\\-\\-–]')
    
    with open('c:\\Users\\Rajes\\OneDrive\\Desktop\\Lakshya_Resume_paser_NEW!\\Lakshya-LLM-Resume-Parser\\backend\\app\\services\\parser\\work_experience_parser.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("Fixed unicode character issues")
    
except Exception as e:
    print(f"Error: {e}")
    # Try with different encoding
    try:
        with open('c:\\Users\\Rajes\\OneDrive\\Desktop\\Lakshya_Resume_paser_NEW!\\Lakshya-LLM-Resume-Parser\\backend\\app\\services\\parser\\work_experience_parser.py', 'r', encoding='latin-1') as f:
            content = f.read()
        
        # Replace problematic characters
        content = content.replace('[\\-\\-]', '[\\-\\-–]')
        content = content.replace('[:\\-\\-]', '[:\\-\\-–]')
        
        with open('c:\\Users\\Rajes\\OneDrive\\Desktop\\Lakshya_Resume_paser_NEW!\\Lakshya-LLM-Resume-Parser\\backend\\app\\services\\parser\\work_experience_parser.py', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("Fixed unicode character issues with latin-1 fallback")
        
    except Exception as e2:
        print(f"Second attempt failed: {e2}")
