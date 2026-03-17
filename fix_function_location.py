#!/usr/bin/env python3

with open('c:\\Users\\Rajes\\OneDrive\\Desktop\\Lakshya_Resume_paser_NEW!\\Lakshya-LLM-Resume-Parser\\backend\\app\\services\\parser\\work_experience_parser.py', 'r') as f:
    content = f.read()
    lines = content.split('\n')
    
# Remove the misplaced function and its body
new_lines = []
skip_until_line = 1220  # Skip until after the current function ends
for i, line in enumerate(lines):
    if 1161 <= i <= 1220:  # Skip the misplaced function
        continue
    new_lines.append(line)

# Add the function in the correct location (after other methods, before _extract_title_from_text)
for i, line in enumerate(new_lines):
    if '_extract_title_from_text' in line:
        # Insert the function before _extract_title_from_text
        new_lines.insert(i, '')
        new_lines.insert(i+1, '    def _parse_company_title(self, header: str) -> tuple[str | None, str | None]:')
        new_lines.insert(i+2, '        """Parse company and title with enhanced client/location extraction"""')
        new_lines.insert(i+3, '        logger.debug(f"Parsing header: {header[:100]}...")')
        new_lines.insert(i+4, '        ')
        new_lines.insert(i+5, '        # Clean header text')
        new_lines.insert(i+6, '        cleaned = self._clean_header_text(header, strip_labels=False)')
        new_lines.insert(i+7, '        if not cleaned:')
        new_lines.insert(i+8, '            return None, None')
        new_lines.insert(i+9, '        ')
        new_lines.insert(i+10, '        # PATTERN 1: Company (Location) format')
        new_lines.insert(i+11, '        location_match = re.search(r\'\\(([^)]+)\\)\', cleaned)')
        new_lines.insert(i+12, '        if location_match:')
        new_lines.insert(i+13, '            location = location_match.group(1).strip()')
        new_lines.insert(i+14, '            company = re.sub(r\'\\s*\\([^)]*\\)\', \'\', cleaned).strip()')
        new_lines.insert(i+15, '            ')
        new_lines.insert(i+16, '            # Extract title from remaining text')
        new_lines.insert(i+17, '            title = self._extract_title_from_text(company)')
        new_lines.insert(i+18, '            if title:')
        new_lines.insert(i+19, '                company = re.sub(rf\'\\s*{re.escape(title)}.*$\', \'\', company, flags=re.IGNORECASE).strip()')
        new_lines.insert(i+20, '            ')
        new_lines.insert(i+21, '            logger.info(f"Parsed: Company=\'{company}\', Location=\'{location}\', Title=\'{title}\'")')
        new_lines.insert(i+22, '            return company, title')
        new_lines.insert(i+23, '        ')
        new_lines.insert(i+24, '        # PATTERN 2: Client: / Role: format')
        new_lines.insert(i+25, '        client_match = re.search(r\'Client\\s*[:\\\\-\\\\-–]\\s*([^\\n]+)\', cleaned, re.IGNORECASE)')
        new_lines.insert(i+26, '        role_match = re.search(r\'Role\\s*[:\\\\-\\\\-–]\\s*([^\\n]+)\', cleaned, re.IGNORECASE)')
        new_lines.insert(i+27, '        ')
        new_lines.insert(i+28, '        if client_match and role_match:')
        new_lines.insert(i+29, '            company = client_match.group(1).strip()')
        new_lines.insert(i+30, '            title = role_match.group(1).strip()')
        new_lines.insert(i+31, '            ')
        new_lines.insert(i+32, '            # Extract location if present')
        new_lines.insert(i+33, '            location_match = re.search(r\'Location\\s*[:\\\\-\\\\-–]\\s*([^\\n]+)\', cleaned, re.IGNORECASE)')
        new_lines.insert(i+34, '            location = location_match.group(1).strip() if location_match else None')
        new_lines.insert(i+35, '            ')
        new_lines.insert(i+36, '            logger.info(f"Parsed: Client=\'{company}\', Role=\'{title}\', Location=\'{location}\'")')
        new_lines.insert(i+37, '            return company, title')
        new_lines.insert(i+38, '        ')
        new_lines.insert(i+39, '        # PATTERN 3: Standard Company/Title split')
        new_lines.insert(i+40, '        parts = re.split(r\'[\\|·•]\', cleaned)')
        new_lines.insert(i+41, '        if len(parts) >= 2:')
        new_lines.insert(i+42, '            company = parts[0].strip()')
        new_lines.insert(i+43, '            title = parts[1].strip()')
        new_lines.insert(i+44, '            logger.info(f"Parsed: Company=\'{company}\', Title=\'{title}\'")')
        new_lines.insert(i+45, '            return company, title')
        new_lines.insert(i+46, '        ')
        new_lines.insert(i+47, '        # PATTERN 4: Fallback - try to extract from text')
        new_lines.insert(i+48, '        title = self._extract_title_from_text(cleaned)')
        new_lines.insert(i+49, '        if title:')
        new_lines.insert(i+50, '            company = re.sub(rf\'\\s*{re.escape(title)}.*$\', \'\', cleaned, flags=re.IGNORECASE).strip()')
        new_lines.insert(i+51, '            logger.info(f"Parsed: Company=\'{company}\', Title=\'{title}\' (fallback)")')
        new_lines.insert(i+52, '            return company, title')
        new_lines.insert(i+53, '        ')
        new_lines.insert(i+54, '        return None, None')
        break

with open('c:\\Users\\Rajes\\OneDrive\\Desktop\\Lakshya_Resume_paser_NEW!\\Lakshya-LLM-Resume-Parser\\backend\\app\\services\\parser\\work_experience_parser.py', 'w') as f:
    f.write('\n'.join(new_lines))

print("Fixed function location - moved to correct place in class")
