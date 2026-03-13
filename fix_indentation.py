#!/usr/bin/env python3

with open('c:\\Users\\Rajes\\OneDrive\\Desktop\\Lakshya_Resume_paser_NEW!\\Lakshya-LLM-Resume-Parser\\backend\\app\\services\\parser\\work_experience_parser.py', 'r') as f:
    lines = f.readlines()
    
# Fix line 1163 - replace tabs with spaces
for i, line in enumerate(lines):
    if i == 1163:
        # Replace tab with 8 spaces
        lines[i] = line.replace('\t        logger.debug(f"Parsing header: {header[:100]}...")\n', '        logger.debug(f"Parsing header: {header[:100]}...")\n')
        break

with open('c:\\Users\\Rajes\\OneDrive\\Desktop\\Lakshya_Resume_paser_NEW!\\Lakshya-LLM-Resume-Parser\\backend\\app\\services\\parser\\work_experience_parser.py', 'w') as f:
    f.writelines(lines)

print("Fixed indentation issue in line 1163")
