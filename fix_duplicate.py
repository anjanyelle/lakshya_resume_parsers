#!/usr/bin/env python3

with open('c:\\Users\\Rajes\\OneDrive\\Desktop\\Lakshya_Resume_paser_NEW!\\Lakshya-LLM-Resume-Parser\\backend\\app\\services\\parser\\work_experience_parser.py', 'r') as f:
    content = f.read()
    lines = content.split('\n')
    
# Remove duplicate function definition - keep only the properly indented one
new_lines = []
for i, line in enumerate(lines):
    if i == 1161:
        # Skip the first duplicate (wrong indentation)
        continue
    elif i == 1162:
        # Keep the second duplicate (correct indentation)
        new_lines.append(line)
    else:
        new_lines.append(line)

with open('c:\\Users\\Rajes\\OneDrive\\Desktop\\Lakshya_Resume_paser_NEW!\\Lakshya-LLM-Resume-Parser\\backend\\app\\services\\parser\\work_experience_parser.py', 'w') as f:
    f.write('\n'.join(new_lines))

print("Removed duplicate function definition")
