#!/usr/bin/env python3

with open('c:\\Users\\Rajes\\OneDrive\\Desktop\\Lakshya_Resume_paser_NEW!\\Lakshya-LLM-Resume-Parser\\backend\\app\\services\\parser\\work_experience_parser.py', 'r', encoding='utf-8', errors='replace') as f:
    content = f.read()
    
# Fix the extract_individual_jobs function to handle the resume format
# Replace PATTERN 2 with correct regex for "Company: Date Range" format
old_pattern = '''        # PATTERN 2: Company: Date Range format
        company_date_pattern = re.compile(r'\\n\\s*Company\\s*:\\s*[^\\n]+\\n', re.IGNORECASE)'''

new_pattern = '''        # PATTERN 2: Company: Date Range format  
        company_date_pattern = re.compile(r'^([^:]+):\\s*([^:]+):\\s*[^-\\n]+-\\s*[^-\\n]+', re.MULTILINE)'''

content = content.replace(old_pattern, new_pattern)

# Also fix the split logic
old_split = '''        if company_date_pattern.search(text):
            logger.info("Found Company: Date Range format, splitting")
            parts = re.split(r'\\n\\s*Company\\s*:', text, flags=re.IGNORECASE)'''

new_split = '''        if company_date_pattern.search(text):
            logger.info("Found Company: Date Range format, splitting")
            parts = re.split(r'\\n(?=[^:]+:[^:]+:)', text)'''

content = content.replace(old_split, new_split)

with open('c:\\Users\\Rajes\\OneDrive\\Desktop\\Lakshya_Resume_paser_NEW!\\Lakshya-LLM-Resume-Parser\\backend\\app\\services\\parser\\work_experience_parser.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed job parsing patterns for Company: Date Range format")
