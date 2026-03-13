#!/usr/bin/env python3

with open('c:\\Users\\Rajes\\OneDrive\\Desktop\\Lakshya_Resume_paser_NEW!\\Lakshya-LLM-Resume-Parser\\backend\\app\\services\\parser\\work_experience_parser.py', 'r') as f:
    content = f.read()
    lines = content.split('\n')
    
# Fix line 1161-1163 - ensure proper indentation for class method
for i, line in enumerate(lines):
    if i == 1161:
        lines[i] = '    def _parse_company_title(self, header: str) -> tuple[str | None, str | None]:'
    elif i == 1162:
        lines[i] = '        """Parse company and title with enhanced client/location extraction"""'
    elif i == 1163:
        lines[i] = '        logger.debug(f"Parsing header: {header[:100]}...")'

with open('c:\\Users\\Rajes\\OneDrive\\Desktop\\Lakshya_Resume_paser_NEW!\\Lakshya-LLM-Resume-Parser\\backend\\app\\services\\parser\\work_experience_parser.py', 'w') as f:
    f.write('\n'.join(lines))

print("Fixed final indentation issue - function should now be properly indented")
