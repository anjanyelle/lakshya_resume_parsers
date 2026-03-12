#!/usr/bin/env python3
"""
Update Backend Parsers to Use New Dataset-Integrated Files
"""

import os
import re
from pathlib import Path

def update_skill_extractor():
    """Update skill_extractor.py to use new company and job title mappings"""
    
    file_path = Path("backend/app/services/parser/skill_extractor.py")
    
    # Add import for new datasets
    import_addition = '''
# Import dataset-integrated mappings
try:
    from app.data.taxonomy.company_mappings import COMPANY_MAPPINGS
    from app.data.taxonomy.job_titles_mappings import JOB_TITLE_MAPPINGS
except ImportError:
    COMPANY_MAPPINGS = {}
    JOB_TITLE_MAPPINGS = {}

'''
    
    # Read existing file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add imports after existing imports
    import_position = content.find("logger = logging.getLogger(__name__)")
    if import_position != -1:
        content = content[:import_position] + import_addition + content[import_position:]
    
    # Add company normalization function
    company_function = '''
def normalize_company_name(text: str) -> str:
    """Normalize company name using dataset mappings"""
    if not text or not isinstance(text, str):
        return text
    
    text_lower = text.lower().replace(" ", "").replace(",", "").replace(".", "")
    
    # Check against dataset mappings
    for normalized, company in COMPANY_MAPPINGS.items():
        if normalized in text_lower or text_lower in normalized:
            return company
    
    return text.strip()

'''
    
    # Add job title normalization function
    job_title_function = '''
def normalize_job_title(text: str) -> str:
    """Normalize job title using dataset mappings"""
    if not text or not isinstance(text, str):
        return text
    
    text_lower = text.lower().replace(" ", "").replace("-", "").replace("/", "")
    
    # Check against dataset mappings
    for normalized, title in JOB_TITLE_MAPPINGS.items():
        if normalized in text_lower or text_lower in normalized:
            return title
    
    return text.strip()

'''
    
    # Add functions before existing functions
    function_position = content.find("def clean_text_for_skills")
    if function_position != -1:
        content = content[:function_position] + company_function + job_title_function + content[function_position:]
    
    # Write updated file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Updated skill_extractor.py with dataset mappings")

def update_certification_parser():
    """Update certification_parser.py to use new certification database"""
    
    file_path = Path("backend/app/services/parser/certification_parser.py")
    
    # Add import for new certification database
    import_addition = '''
# Import dataset-integrated certification database
try:
    from app.data.taxonomy.certifications_top import CERTIFICATION_DATABASE, CERTIFICATION_ALIASES
except ImportError:
    CERTIFICATION_DATABASE = []
    CERTIFICATION_ALIASES = {}

'''
    
    # Read existing file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add imports after existing imports
    import_position = content.find("logger = logging.getLogger(__name__)")
    if import_position != -1:
        content = content[:import_position] + import_addition + content[import_position:]
    
    # Add enhanced certification lookup function
    lookup_function = '''
def lookup_certification(cert_name: str) -> dict:
    """Lookup certification using dataset database"""
    if not cert_name:
        return {}
    
    cert_lower = cert_name.lower().replace(" ", " ").replace("-", " ").replace(".", "")
    
    # Check aliases first
    for alias, full_name in CERTIFICATION_ALIASES.items():
        if alias in cert_lower or cert_lower in alias:
            # Find full certification details
            for cert in CERTIFICATION_DATABASE:
                if cert.get("name") == full_name:
                    return cert
            break
    
    # Direct database search
    for cert in CERTIFICATION_DATABASE:
        name_lower = cert.get("name", "").lower().replace(" ", " ").replace("-", " ").replace(".", "")
        if name_lower in cert_lower or cert_lower in name_lower:
            return cert
    
    return {}

'''
    
    # Add function before existing functions
    function_position = content.find("class CertificationParser")
    if function_position != -1:
        content = content[:function_position] + lookup_function + content[function_position:]
    
    # Write updated file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Updated certification_parser.py with dataset database")

def update_work_experience_parser():
    """Update work_experience_parser.py to use new company mappings"""
    
    file_path = Path("backend/app/services/parser/work_experience_parser.py")
    
    # Add import for new company mappings
    import_addition = '''
# Import dataset-integrated company mappings
try:
    from app.data.taxonomy.company_mappings import COMPANY_MAPPINGS
except ImportError:
    COMPANY_MAPPINGS = {}

'''
    
    # Read existing file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add imports after existing imports
    import_position = content.find("logger = logging.getLogger(__name__")
    if import_position != -1:
        content = content[:import_position] + import_addition + content[import_position:]
    
    # Add company normalization function
    company_function = '''
def normalize_company_name(text: str) -> str:
    """Normalize company name using dataset mappings"""
    if not text or not isinstance(text, str):
        return text
    
    text_lower = text.lower().replace(" ", "").replace(",", "").replace(".", "")
    
    # Check against dataset mappings
    for normalized, company in COMPANY_MAPPINGS.items():
        if normalized in text_lower or text_lower in normalized:
            return company
    
    return text.strip()

'''
    
    # Add function before existing functions
    function_position = content.find("class WorkExperienceParser")
    if function_position != -1:
        content = content[:function_position] + company_function + content[function_position:]
    
    # Write updated file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Updated work_experience_parser.py with company mappings")

def main():
    """Update all backend parsers to use new datasets"""
    
    print("🔧 UPDATING BACKEND PARSERS TO USE DATASETS")
    print("=" * 50)
    
    try:
        update_skill_extractor()
        update_certification_parser()
        update_work_experience_parser()
        
        print("\n✅ All backend parsers updated successfully!")
        print("\n🎯 NEXT STEPS:")
        print("1. Restart your backend application")
        print("2. Test with real resume data")
        print("3. Monitor accuracy improvements")
        
    except Exception as e:
        print(f"❌ Error updating parsers: {e}")
        print("Please check file paths and permissions")

if __name__ == "__main__":
    main()
