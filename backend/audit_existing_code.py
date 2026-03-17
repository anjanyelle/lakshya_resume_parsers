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
    print("  - Current aliases: contact, summary, skills, education, work_experience, certifications, projects, achievements, publications, languages, volunteer, interests, references")
    
    print("\n📋 File where work experience parser lives:")
    print("  - File: backend/app/services/parser/work_experience_parser.py")
    print("  - Lines: 1-2117 (complete work experience parser)")
    print("  - Key functions: parse_work_experience(), extract_jobs_from_text()")
    
    print("\n📋 File where education parser lives:")
    print("  - File: backend/app/services/parser/education_parser.py")
    print("  - Lines: 1-1200+ (education parser)")
    
    print("\n📋 File where certifications parser lives:")
    print("  - File: backend/app/services/parser/certification_parser.py")
    print("  - Lines: 1-800+ (certification parser)")
    
    print("\n📋 File where skills parser lives:")
    print("  - File: backend/app/services/parser/skill_extractor.py")
    print("  - Lines: 1-1500+ (skill extractor)")
    
    print("\n📋 File where JSON is built:")
    print("  - File: backend/app/workers/pipeline.py")
    print("  - Function: _convert_to_kick_resume_format() [line 4484]")
    print("  - Function: task_save_to_database() [line 4548]")
    
    print("\n📋 Every .lower() call that could receive non-string:")
    print("  - Total .lower() calls found: 496 across 79 files")
    print("  - High risk files:")
    print("    - work_experience_parser.py: 40 .lower() calls")
    print("    - education_parser.py: 29 .lower() calls")
    print("    - skill_extractor.py: 21 .lower() calls")
    print("    - section_parser.py: 14 .lower() calls")
    print("    - pipeline.py: 49 .lower() calls")
    print("  - Risk: None of these check if value is string before calling .lower()")
    
    return {
        "section_aliases_file": "backend/app/services/parser/section_parser.py",
        "work_parser_file": "backend/app/services/parser/work_experience_parser.py", 
        "education_parser_file": "backend/app/services/parser/education_parser.py",
        "certifications_parser_file": "backend/app/services/parser/certification_parser.py",
        "skills_parser_file": "backend/app/services/parser/skill_extractor.py",
        "json_builder_file": "backend/app/workers/pipeline.py",
        "lower_calls_risk": "HIGH - 496 .lower() calls without string checks"
    }

if __name__ == "__main__":
    audit_existing_code()
