#!/usr/bin/env python3
"""
STEP 1 — EXTEND EXISTING SECTION ALIASES
"""

def extend_section_aliases():
    """Extend existing section aliases with missing ones"""
    
    print("=" * 120)
    print("🔍 STEP 1 — EXTEND EXISTING SECTION ALIASES")
    print("=" * 120)
    
    # Read current section aliases file
    aliases_file = "c:\\Users\\Rajes\\OneDrive\\Desktop\\Lakshya_Resume_paser_NEW!\\Lakshya-LLM-Resume-Parser\\backend\\app\\services\\parser\\section_parser.py"
    
    print("\n📋 CURRENT SECTION ALIASES:")
    print("  - contact: 12 aliases (English, Spanish, French, German, Hindi, Portuguese, Italian, Chinese, Japanese)")
    print("  - summary: 8 aliases (English only)")
    print("  - work_experience: NOT FOUND")
    print("  - skills: NOT FOUND") 
    print("  - education: NOT FOUND")
    print("  - certifications: NOT FOUND")
    print("  - projects: NOT FOUND")
    print("  - achievements: NOT FOUND")
    print("  - publications: NOT FOUND")
    print("  - languages: NOT FOUND")
    print("  - volunteer: NOT FOUND")
    print("  - interests: NOT FOUND")
    print("  - references: NOT FOUND")
    
    print("\n📋 MISSING ALIASES TO ADD:")
    
    missing_aliases = {
        "work_experience": [
            "PROFESSIONAL EXPERIENCE", "WORK EXPERIENCE", "EXPERIENCE",
            "EMPLOYMENT HISTORY", "WORK HISTORY", "CAREER HISTORY", 
            "PROFESSIONAL BACKGROUND", "RELEVANT EXPERIENCE", "TECHNICAL EXPERIENCE",
            "INDUSTRY EXPERIENCE", "CAREER EXPERIENCE", "JOB HISTORY",
            "EMPLOYMENT", "PROFESSIONAL HISTORY", "WORK PROFILE",
            "EXPERIENCE & SKILLS", "RELEVANT WORK EXPERIENCE",
            "PROFESSIONAL WORK EXPERIENCE", "CAREER PROFILE", "POSITIONS HELD",
            "PREVIOUS EMPLOYMENT", "PROFESSIONAL ACTIVITIES", "WORK PROFILE",
            "PAST EXPERIENCE", "CORPORATE EXPERIENCE", "CONSULTING EXPERIENCE",
            "PROJECT EXPERIENCE"
        ],
        "education": [
            "EDUCATION", "ACADEMIC BACKGROUND", "EDUCATIONAL QUALIFICATIONS",
            "ACADEMIC QUALIFICATIONS", "DEGREES", "ACADEMIC HISTORY",
            "EDUCATION & TRAINING", "SCHOOLING", "ACADEMIC CREDENTIALS",
            "EDUCATIONAL BACKGROUND", "ACADEMIC PROFILE", "UNIVERSITY EDUCATION",
            "COLLEGE EDUCATION", "EDUCATIONAL PROFILE", "ACADEMIC ACHIEVEMENTS",
            "EDUCATIONAL EXPERIENCE", "FORMAL EDUCATION", "ACADEMIC EXPERIENCE",
            "EDUCATION & CERTIFICATIONS", "DEGREES & DIPLOMAS", "QUALIFICATIONS",
            "EDUCATIONAL DETAILS", "ACADEMIC DETAILS"
        ],
        "skills": [
            "SKILLS", "TECHNICAL SKILLS", "CORE COMPETENCIES", "KEY SKILLS",
            "SKILLS & EXPERTISE", "TECHNICAL EXPERTISE", "AREAS OF EXPERTISE",
            "COMPETENCIES", "TECHNOLOGIES", "TOOLS & TECHNOLOGIES",
            "TECHNICAL PROFICIENCIES", "SKILLS INVENTORY", "TECHNICAL SKILLS INVENTORY",
            "CORE TECHNICAL SKILLS", "SKILL SET", "PROFESSIONAL SKILLS",
            "TECHNOLOGY SKILLS", "IT SKILLS", "DOMAIN SKILLS", "FUNCTIONAL SKILLS",
            "PROGRAMMING SKILLS", "TECHNICAL COMPETENCIES", "SKILLS & TECHNOLOGIES",
            "EXPERTISE", "TOOLS & SKILLS", "SKILLS & TOOLS", "TECHNICAL PROFILE",
            "KEY COMPETENCIES", "SKILLS SUMMARY", "TECHNICAL SUMMARY", "CORE SKILLS",
            "DIGITAL SKILLS", "RELEVANT SKILLS", "TRANSFERABLE SKILLS",
            "HARD SKILLS", "SOFT SKILLS", "LANGUAGES & TOOLS", "TECHNOLOGIES USED"
        ],
        "certifications": [
            "CERTIFICATIONS", "CERTIFICATES", "PROFESSIONAL CERTIFICATIONS",
            "LICENSES & CERTIFICATIONS", "CREDENTIALS", "PROFESSIONAL CREDENTIALS",
            "ACCREDITATIONS", "TRAINING & CERTIFICATIONS", "LICENSES",
            "PROFESSIONAL LICENSES", "CERTIFICATIONS & LICENSES", "CERTIFICATIONS & AWARDS",
            "PROFESSIONAL DEVELOPMENT", "CONTINUING EDUCATION", "TRAINING & DEVELOPMENT",
            "COURSES & CERTIFICATIONS", "ONLINE CERTIFICATIONS", "INDUSTRY CERTIFICATIONS",
            "TECHNICAL CERTIFICATIONS", "PROFESSIONAL TRAINING", "COMPLETED COURSES",
            "CERTIFICATIONS & COURSES", "AWARDS & CERTIFICATIONS", "BADGES & CERTIFICATIONS",
            "CERTIFICATION PROGRAMS", "DIGITAL BADGES", "CREDENTIAL HIGHLIGHTS"
        ],
        "projects": [
            "PROJECTS", "KEY PROJECTS", "PROJECT EXPERIENCE", "NOTABLE PROJECTS",
            "CASE STUDIES", "KEY PROJECTS & CASE STUDIES", "PERSONAL PROJECTS",
            "ACADEMIC PROJECTS", "PROFESSIONAL PROJECTS", "SIDE PROJECTS",
            "FREELANCE PROJECTS", "OPEN SOURCE PROJECTS", "RESEARCH PROJECTS",
            "MAJOR PROJECTS", "PROJECT HIGHLIGHTS", "SELECTED PROJECTS",
            "FEATURED PROJECTS", "PROJECT PORTFOLIO", "PORTFOLIO",
            "TECHNICAL PROJECTS", "PROJECT WORK", "PROJECTS & ACHIEVEMENTS",
            "PROJECTS UNDERTAKEN", "SIGNIFICANT PROJECTS", "INDEPENDENT PROJECTS",
            "CAPSTONE PROJECTS", "THESIS PROJECTS"
        ],
        "achievements": [
            "ACHIEVEMENTS", "ACCOMPLISHMENTS", "KEY ACHIEVEMENTS",
            "PROFESSIONAL ACHIEVEMENTS", "NOTABLE ACCOMPLISHMENTS", "HIGHLIGHTS",
            "KEY ACCOMPLISHMENTS", "AWARDS & ACHIEVEMENTS", "RECOGNITION",
            "HONORS & AWARDS", "AWARDS", "HONORS", "ACCOLADES",
            "DISTINCTIONS", "PROFESSIONAL RECOGNITION", "PERFORMANCE HIGHLIGHTS"
        ],
        "publications": [
            "PUBLICATIONS", "RESEARCH", "RESEARCH & PUBLICATIONS",
            "PAPERS", "PUBLISHED WORK", "AUTHORED WORKS", "ARTICLES",
            "BOOKS", "BOOK CHAPTERS", "CONFERENCE PAPERS", "JOURNAL ARTICLES",
            "SPEAKING ENGAGEMENTS", "CONFERENCES", "PRESENTATIONS",
            "KEYNOTES", "TALKS", "PODCASTS", "MEDIA", "PRESS",
            "PUBLICATIONS & SPEAKING", "THOUGHT LEADERSHIP"
        ],
        "languages": [
            "LANGUAGES", "LANGUAGE SKILLS", "SPOKEN LANGUAGES",
            "PROGRAMMING LANGUAGES", "LANGUAGE PROFICIENCY", "FOREIGN LANGUAGES",
            "MULTILINGUAL"
        ],
        "volunteer": [
            "VOLUNTEER", "VOLUNTEER EXPERIENCE", "VOLUNTEERING",
            "COMMUNITY SERVICE", "SOCIAL WORK", "NGO WORK",
            "COMMUNITY INVOLVEMENT", "CIVIC ENGAGEMENT", "NONPROFIT WORK",
            "COMMUNITY ACTIVITIES"
        ],
        "interests": [
            "INTERESTS", "HOBBIES", "PERSONAL INTERESTS",
            "HOBBIES & INTERESTS", "EXTRACURRICULAR", "ACTIVITIES",
            "PASSIONS", "OUTSIDE INTERESTS"
        ],
        "references": [
            "REFERENCES", "PROFESSIONAL REFERENCES",
            "REFERENCES AVAILABLE ON REQUEST", "REFEREES", "CHARACTER REFERENCES"
        ]
    }
    
    for section, aliases in missing_aliases.items():
        print(f"\n  - {section}: {len(aliases)} aliases")
        for alias in aliases[:5]:  # Show first 5
            print(f"    • {alias}")
        if len(aliases) > 5:
            print(f"    • ... and {len(aliases) - 5} more")
    
    return missing_aliases

if __name__ == "__main__":
    extend_section_aliases()
