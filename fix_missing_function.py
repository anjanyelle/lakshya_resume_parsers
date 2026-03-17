#!/usr/bin/env python3

with open('c:\\Users\\Rajes\\OneDrive\\Desktop\\Lakshya_Resume_paser_NEW!\\Lakshya-LLM-Resume-Parser\\backend\\app\\services\\parser\\work_experience_parser.py', 'r') as f:
    content = f.read()
    lines = content.split('\n')
    
# Add the missing function definition before the orphaned code
new_lines = []
for i, line in enumerate(lines):
    if i == 736:  # Before the orphaned code
        new_lines.append('    def extract_individual_jobs(self, text: str, source_format: str | None = None) -> list[str]:')
        new_lines.append('        # Enhanced client splitting for multiple formats')
        new_lines.append('        logger.info(f"Extracting individual jobs from text length: {len(text)}")')
        new_lines.append('        ')
        new_lines.append('        # PATTERN 1: Client: format (highest priority)')
        new_lines.append('        client_pattern = re.compile(r\'\\n\\s*Client\\s*[:\\-\\-–]\', re.IGNORECASE)')
        new_lines.append('        client_matches = client_pattern.findall(text)')
        new_lines.append('        ')
        new_lines.append('        if len(client_matches) >= 2:')
        new_lines.append('            logger.info(f"Found {len(client_matches)} client markers, splitting by client")')
        new_lines.append('            parts = client_pattern.split(text)')
        new_lines.append('            client_blocks = []')
        new_lines.append('            for p in parts:')
        new_lines.append('                p_strip = p.strip()')
        new_lines.append('                if p_strip:')
        new_lines.append('                    client_blocks.append(p_strip)')
        new_lines.append('            if len(client_blocks) >= 1:')
        new_lines.append('                return client_blocks')
    else:
        new_lines.append(line)

with open('c:\\Users\\Rajes\\OneDrive\\Desktop\\Lakshya_Resume_paser_NEW!\\Lakshya-LLM-Resume-Parser\\backend\\app\\services\\parser\\work_experience_parser.py', 'w') as f:
    f.write('\n'.join(new_lines))

print("Added missing function definition - extract_individual_jobs")
