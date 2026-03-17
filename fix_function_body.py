#!/usr/bin/env python3

with open('c:\\Users\\Rajes\\OneDrive\\Desktop\\Lakshya_Resume_paser_NEW!\\Lakshya-LLM-Resume-Parser\\backend\\app\\services\\parser\\work_experience_parser.py', 'r') as f:
    content = f.read()
    lines = content.split('\n')
    
# Replace the broken function with correct implementation
new_lines = []
skip_until_line = 1170  # Skip the broken function
for i, line in enumerate(lines):
    if 1160 <= i <= 1170:  # Skip the broken function
        continue
    new_lines.append(line)

# Find where to insert the correct function (before _extract_title_from_text)
for i, line in enumerate(new_lines):
    if '_extract_title_from_text' in line and 'def' in line:
        # Insert the complete function before _extract_title_from_text
        new_lines.insert(i, '')
        new_lines.insert(i+1, '    def _extract_title_from_text(self, text: str) -> str | None:')
        new_lines.insert(i+2, '        """Extract job title from text using common patterns"""')
        new_lines.insert(i+3, '        title_patterns = [')
        new_lines.insert(i+4, '            r\'(?:Senior|Junior|Lead|Principal|Staff|Associate)?\\s*(?:Software|Full[-\\s]*Stack|Backend|Frontend|Java|Python|Data)\\s*(?:Developer|Engineer|Architect|Consultant|Manager|Analyst)\',')
        new_lines.insert(i+5, '            r\'(?:Senior|Junior|Lead|Principal|Staff|Associate)?\\s*(?:Project|Product|Program)\\s*(?:Manager|Lead|Engineer)\',')
        new_lines.insert(i+6, '            r\'(?:Senior|Junior|Lead|Principal|Staff|Associate)?\\s*(?:DevOps|QA|Test|UI|UX)\\s*(?:Engineer|Developer|Designer)\',')
        new_lines.insert(i+7, '        ]')
        new_lines.insert(i+8, '        ')
        new_lines.insert(i+9, '        for pattern in title_patterns:')
        new_lines.insert(i+10, '            match = re.search(pattern, text, re.IGNORECASE)')
        new_lines.insert(i+11, '            if match:')
        new_lines.insert(i+12, '                return match.group(0).strip()')
        new_lines.insert(i+13, '        ')
        new_lines.insert(i+14, '        return None')
        break

with open('c:\\Users\\Rajes\\OneDrive\\Desktop\\Lakshya_Resume_paser_NEW!\\Lakshya-LLM-Resume-Parser\\backend\\app\\services\\parser\\work_experience_parser.py', 'w') as f:
    f.write('\n'.join(new_lines))

print("Fixed function body - replaced broken function with correct implementation")
