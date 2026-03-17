#!/usr/bin/env python3
"""
STEP 11 — FIX PIPELINE ERROR AND JSON BUILDER
"""

def fix_pipeline_error_and_json_builder():
    """Fix .lower() safety and JSON builder issues"""
    
    print("=" * 120)
    print("🔍 STEP 11 — FIX PIPELINE ERROR AND JSON BUILDER")
    print("=" * 120)
    
    print("\n📋 CRITICAL .lower() SAFETY FIX:")
    
    print("1. CREATE safe_lower() function:")
    safe_lower_code = '''
def safe_lower(value):
    """Safely convert value to lowercase, handling None and non-string values"""
    if value is None:
        return ""
    if not isinstance(value, str):
        value = str(value)
    return value.lower()
'''
    print(safe_lower_code)
    
    print("\n2. FILES NEEDING .lower() FIXES (496 total calls):")
    high_risk_files = {
        "work_experience_parser.py": "40 .lower() calls - HIGH RISK",
        "education_parser.py": "29 .lower() calls - HIGH RISK", 
        "skill_extractor.py": "21 .lower() calls - HIGH RISK",
        "section_parser.py": "14 .lower() calls - MEDIUM RISK",
        "pipeline.py": "49 .lower() calls - MEDIUM RISK"
    }
    
    for file_path, risk_level in high_risk_files.items():
        print(f"  • {file_path}: {risk_level}")
    
    print("\n3. REPLACEMENT STRATEGY:")
    replacement_strategy = [
        "Replace all .lower() calls with safe_lower()",
        "Import safe_lower function at top of each file",
        "Focus on high-risk files first",
        "Test with None values to prevent crashes"
    ]
    
    for strategy in replacement_strategy:
        print(f"  • {strategy}")
    
    print("\n📋 JSON BUILDER FIXES:")
    
    print("1. ENSURE NO NULL VALUES:")
    json_fixes = [
        "All keys always present",
        "Empty string for missing strings", 
        "Empty list for missing lists",
        "Duration always calculated from dates",
        "is_current = true when end_date is Present/Current/Ongoing",
        "total_experience.years calculated from all work entries",
        "Skills deduplicated before output",
        "Institution name cleaned before output",
        "Company name cleaned before output",
        "Cert name cleaned before output"
    ]
    
    for fix in json_fixes:
        print(f"  • {fix}")
    
    print("\n2. JSON BUILDER LOCATION:")
    print("File: backend/app/workers/pipeline.py")
    print("Function: _convert_to_kick_resume_format() [line 4484]")
    print("Function: task_save_to_database() [line 4548]")
    
    print("\n3. SPECIFIC JSON STRUCTURE FIXES:")
    json_structure_fixes = [
        "work_experience[].company → cleaned company name",
        "work_experience[].location → cleaned location", 
        "work_experience[].start_date → standardized format",
        "work_experience[].end_date → standardized format",
        "work_experience[].is_current → boolean from end_date",
        "work_experience[].duration → calculated months/years",
        "education[].institution → cleaned institution name",
        "education[].degree → cleaned degree name",
        "education[].start_year/end_year → standardized years",
        "certifications[].name → cleaned cert name",
        "certifications[].issuer → extracted issuer",
        "certifications[].credential_id → extracted ID",
        "certifications[].valid_from/valid_to → date objects",
        "skills[] → deduplicated list with categories",
        "basics.name → cleaned first/last name",
        "basics.email/phone → cleaned contact info"
    ]
    
    for fix in json_structure_fixes:
        print(f"  • {fix}")
    
    print("\n📝 COMPANY NAME CLEANING RULES:")
    company_cleaning = [
        "Strip: ##, #, **, *, CLIENT:, Client:, COMPANY:",
        "Strip leading/trailing spaces and special chars",
        "Convert ALL CAPS → Title Case",
        "Keep uppercase: IBM, TCS, ADP, HCL, GCP, AWS, VMware, SAP, HP, PwC, KPMG, EY, JPMC, HSBC, BofA, T-Mobile, AT&T, BBC, CNN, FBI, CIA, NASA"
    ]
    
    for rule in company_cleaning:
        print(f"  • {rule}")
    
    print("\n📝 INSTITUTION NAME CLEANING RULES:")
    institution_cleaning = [
        "Remove city, state, country after – or , or |",
        "Remove year from institution name", 
        "Keep only university/college name",
        "University of Washington – Seattle, WA → University of Washington",
        "Bharath University - Bachelor of Technology... → Bharath University"
    ]
    
    for rule in institution_cleaning:
        print(f"  • {rule}")
    
    print("\n🎯 IMPLEMENTATION PRIORITY:")
    priority_order = [
        "1. Create safe_lower() function in utils.py",
        "2. Fix work_experience_parser.py (40 .lower() calls)",
        "3. Fix education_parser.py (29 .lower() calls)",
        "4. Fix skill_extractor.py (21 .lower() calls)",
        "5. Fix section_parser.py (14 .lower() calls)",
        "6. Fix pipeline.py JSON builder",
        "7. Test with None values to prevent crashes"
    ]
    
    for priority in priority_order:
        print(f"  {priority}")
    
    return {
        "safe_lower_function": safe_lower_code,
        "high_risk_files": high_risk_files,
        "json_fixes": json_fixes,
        "company_cleaning": company_cleaning,
        "institution_cleaning": institution_cleaning
    }

if __name__ == "__main__":
    fix_pipeline_error_and_json_builder()
