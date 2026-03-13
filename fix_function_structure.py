#!/usr/bin/env python3

# Read the file and fix the broken function structure
try:
    with open('c:\\Users\\Rajes\\OneDrive\\Desktop\\Lakshya_Resume_paser_NEW!\\Lakshya-LLM-Resume-Parser\\backend\\app\\services\\parser\\work_experience_parser.py', 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()
    
    lines = content.split('\n')
    new_lines = []
    
    # Find and fix the broken extract_individual_jobs function
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Skip the broken function definition and orphaned code
        if 'def extract_individual_jobs' in line and i < 750:
            # Skip until we find a proper place to add the function
            i += 1
            while i < len(lines) and not ('def ' in lines[i] and i > 800):
                i += 1
            # Add the complete function definition here
            new_lines.extend([
                '    def extract_individual_jobs(self, text: str, source_format: str | None = None) -> list[str]:',
                '        # Enhanced client splitting for multiple formats',
                '        logger.info(f"Extracting individual jobs from text length: {len(text)}")',
                '        ',
                '        # PATTERN 1: Client: format (highest priority)',
                '        client_pattern = re.compile(r\'\\n\\s*Client\\s*[:\\-\\-–]\', re.IGNORECASE)',
                '        client_matches = client_pattern.findall(text)',
                '        ',
                '        if len(client_matches) >= 2:',
                '            logger.info(f"Found {len(client_matches)} client markers, splitting by client")',
                '            parts = client_pattern.split(text)',
                '            client_blocks = []',
                '            for p in parts:',
                '                p_strip = p.strip()',
                '                if p_strip:',
                '                    client_blocks.append(p_strip)',
                '            if len(client_blocks) >= 1:',
                '                return client_blocks',
                '        ',
                '        # PATTERN 2: Company: Date Range format',
                '        company_date_pattern = re.compile(r\'\\n\\s*Company\\s*:\\s*[^\\n]+\\n\', re.IGNORECASE)',
                '        if company_date_pattern.search(text):',
                '            logger.info("Found Company: Date Range format, splitting")',
                '            parts = re.split(r\'\\n\\s*Company\\s*:\', text, flags=re.IGNORECASE)',
                '            company_blocks = []',
                '            for p in parts[1:]:  # Skip first empty part',
                '                p_strip = p.strip()',
                '                if p_strip:',
                '                    company_blocks.append(p_strip)',
                '            if len(company_blocks) >= 1:',
                '                return company_blocks',
                '        ',
                '        # PATTERN 3: Standard job boundaries',
                '        lines = [line.strip() for line in text.splitlines() if line.strip()]',
                '        if not lines:',
                '            return []',
                '            ',
                '        boundaries = []',
                '        for idx, line in enumerate(lines):',
                '            if CLIENT_HEADER_RE.match(line):',
                '                boundaries.append(idx)',
                '                continue',
                '            if DATE_ANCHOR_RE.search(line) and idx + 1 < len(lines) and PRESENT_RE.search(lines[idx + 1]):',
                '                boundaries.append(idx)',
                '                continue',
                '        ',
                '        # Create job chunks from boundaries',
                '        if not boundaries:',
                '            return [text]',
                '            ',
                '        chunks = []',
                '        for i, start in enumerate(boundaries):',
                '            end = boundaries[i + 1] if i + 1 < len(boundaries) else len(lines)',
                '            chunk = "\\n".join(lines[start:end])',
                '            if chunk.strip():',
                '                chunks.append(chunk.strip())',
                '            ',
                '        return chunks',
                ''
            ])
            continue
        else:
            new_lines.append(line)
        i += 1
    
    # Write the fixed content
    with open('c:\\Users\\Rajes\\OneDrive\\Desktop\\Lakshya_Resume_paser_NEW!\\Lakshya-LLM-Resume-Parser\\backend\\app\\services\\parser\\work_experience_parser.py', 'w', encoding='utf-8') as f:
        f.write('\n'.join(new_lines))
    
    print("Fixed function structure - extract_individual_jobs now properly defined")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
