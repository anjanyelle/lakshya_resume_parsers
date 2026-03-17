#!/usr/bin/env python3

with open('c:\\Users\\Rajes\\OneDrive\\Desktop\\Lakshya_Resume_paser_NEW!\\Lakshya-LLM-Resume-Parser\\backend\\app\\services\\parser\\work_experience_parser.py', 'r', encoding='utf-8') as f:
    content = f.read()
    
# Replace the problematic unicode dash with standard dash
content = content.replace('[\\-\\-�]', '[\\-\\-–]')

with open('c:\\Users\\Rajes\\OneDrive\\Desktop\\Lakshya_Resume_paser_NEW!\\Lakshya-LLM-Resume-Parser\\backend\\app\\services\\parser\\work_experience_parser.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed unicode character - replaced em dash with proper dash")
