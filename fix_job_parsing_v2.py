#!/usr/bin/env python3

with open('c:\\Users\\Rajes\\OneDrive\\Desktop\\Lakshya_Resume_paser_NEW!\\Lakshya-LLM-Resume-Parser\\backend\\app\\services\\parser\\work_experience_parser.py', 'r', encoding='utf-8', errors='replace') as f:
    content = f.read()
    
# Fix the extract_individual_jobs function with the correct patterns
# Replace the entire PATTERN 2 section
old_pattern_section = '''        # PATTERN 2: Company: Date Range format  
        company_date_pattern = re.compile(r'^([^:]+):\s*([^:]+):\s*[^-\\n]+-\\s*[^-\\n]+', re.MULTILINE)
        if company_date_pattern.search(text):
            logger.info("Found Company: Date Range format, splitting")
            parts = re.split(r'\\n(?=[^:]+:[^:]+:)', text)
            company_blocks = []
            for p in parts[1:]:  # Skip first empty part
                p_strip = p.strip()
                if p_strip:
                    company_blocks.append(p_strip)
            if len(company_blocks) >= 1:
                return company_blocks'''

new_pattern_section = '''        # PATTERN 2: Company: Date Range (Location: City, State) format
        # Format: "Humana: August 2023 - Current (Location: Louisville, KY)"
        company_date_pattern = re.compile(r'^[^:]+:\s*[A-Z][a-z]+\s+\d{4}\s*-\s*[^-\n]+', re.MULTILINE)
        if company_date_pattern.search(text):
            logger.info("Found Company: Date Range format, splitting")
            # Split by company names that match the pattern
            parts = re.split(r'\n(?=[A-Z][a-zA-Z\s&]+:\s*[A-Z][a-z]+\s*\d{4})', text)
            company_blocks = []
            for p in parts:
                p_strip = p.strip()
                if p_strip:
                    company_blocks.append(p_strip)
            if len(company_blocks) >= 1:
                return company_blocks'''

content = content.replace(old_pattern_section, new_pattern_section)

with open('c:\\Users\\Rajes\\OneDrive\\Desktop\\Lakshya_Resume_paser_NEW!\\Lakshya-LLM-Resume-Parser\\backend\\app\\services\\parser\\work_experience_parser.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed job parsing patterns for Company: Date Range (Location) format")
