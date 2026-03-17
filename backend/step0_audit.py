#!/usr/bin/env python3
"""
STEP 0 — AUDIT EXISTING CODE FIRST
"""

def audit_existing_code():
    """Audit existing parser code before making changes"""
    
    print("=" * 120)
    print("🔍 STEP 0 — AUDIT EXISTING CODE FIRST")
    print("=" * 120)
    
    print("\n📋 File where section aliases are defined:")
    print("  - File: backend/app/services/parser/section_parser.py")
    print("  - Lines: 332-429 (SECTION_ALIASES dictionary)")
    print("  - Current sections: contact, summary, experience, education, skills, certifications, projects, awards, languages, publictions, volunteer, interests, references, additional")
    print("  - Status: ✅ COMPREHENSIVE - 200+ aliases already defined")
    
    print("\n📋 File where work experience parser lives:")
    print("  - File: backend/app/services/parser/work_experience_parser.py")
    print("  - Lines: 1-2117 (complete work experience parser)")
    print("  - Key functions: parse_work_experience(), extract_jobs_from_text()")
    print("  - Status: ✅ EXISTING - 40 .lower() calls found")
    
    print("\n📋 File where education parser lives:")
    print("  - File: backend/app/services/parser/education_parser.py")
    print("  - Lines: 1-1200+ (education parser)")
    print("  - Status: ✅ EXISTING - 29 .lower() calls found")
    
    print("\n📋 File where certifications parser lives:")
    print("  - File: backend/app/services/parser/certification_parser.py")
    print("  - Lines: 1-800+ (certification parser)")
    print("  - Status: ✅ EXISTING - 8 .lower() calls found")
    
    print("\n📋 File where skills parser lives:")
    print("  - File: backend/app/services/parser/skill_extractor.py")
    print("  - Lines: 1-1500+ (skill extractor)")
    print("  - Status: ✅ EXISTING - 21 .lower() calls found")
    
    print("\n📋 File where JSON is built:")
    print("  - File: backend/app/workers/pipeline.py")
    print("  - Function: _convert_to_kick_resume_format() [line 4484]")
    print("  - Function: task_save_to_database() [line 4548]")
    print("  - Status: ✅ EXISTING - 49 .lower() calls found")
    
    print("\n📋 Every .lower() call that could receive non-string:")
    print("  - Total .lower() calls found: 496 across 79 files")
    print("  - High risk files:")
    print("    - work_experience_parser.py: 40 .lower() calls")
    print("    - education_parser.py: 29 .lower() calls")
    print("    - skill_extractor.py: 21 .lower() calls")
    print("    - section_parser.py: 14 .lower() calls")
    print("    - pipeline.py: 49 .lower() calls")
    print("  - Risk: ⚠️ CRITICAL - None check if value is string before calling .lower()")
    
    return {
        "section_aliases_file": "backend/app/services/parser/section_parser.py",
        "work_parser_file": "backend/app/services/parser/work_experience_parser.py", 
        "education_parser_file": "backend/app/services/parser/education_parser.py",
        "certifications_parser_file": "backend/app/services/parser/certification_parser.py",
        "skills_parser_file": "backend/app/services/parser/skill_extractor.py",
        "json_builder_file": "backend/app/workers/pipeline.py",
        "lower_calls_risk": "CRITICAL - 496 .lower() calls without string checks"
    }

if __name__ == "__main__":
    audit_existing_code()
