#!/usr/bin/env python3

with open('c:\\Users\\Rajes\\OneDrive\\Desktop\\Lakshya_Resume_paser_NEW!\\Lakshya-LLM-Resume-Parser\\backend\\app\\services\\parser\\work_experience_parser.py', 'r') as f:
    content = f.read()
    lines = content.split('\n')
    
# Fix line 1161 - add proper indentation (4 spaces for class method)
for i, line in enumerate(lines):
    if i == 1161:
        # Replace with proper indentation (4 spaces from class level)
        lines[i] = '    def _parse_company_title(self, header: str) -> tuple[str | None, str | None]:'
        break

with open('c:\\Users\\Rajes\\OneDrive\\Desktop\\Lakshya_Resume_paser_NEW!\\Lakshya-LLM-Resume-Parser\\backend\\app\\services\\parser\\work_experience_parser.py', 'w') as f:
    f.writelines(lines)

print("Fixed function indentation")
