#!/usr/bin/env python3
"""
ADD MISSING SECTION ALIASES
"""

def add_missing_aliases():
    """Add missing section aliases to section_parser.py"""
    
    # Read the current file
    file_path = "c:\\Users\\Rajes\\OneDrive\\Desktop\\Lakshya_Resume_paser_NEW!\\Lakshya-LLM-Resume-Parser\\backend\\app\\services\\parser\\section_parser.py"
    
    print("🔧 ADDING MISSING SECTION ALIASES")
    print(f"📁 File: {file_path}")
    
    # Missing aliases to add
    missing_work_experience = [
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
    ]
    
    missing_education = [
        "EDUCATION", "ACADEMIC BACKGROUND", "EDUCATIONAL QUALIFICATIONS",
        "ACADEMIC QUALIFICATIONS", "DEGREES", "ACADEMIC HISTORY",
        "EDUCATION & TRAINING", "SCHOOLING", "ACADEMIC CREDENTIALS",
        "EDUCATIONAL BACKGROUND", "ACADEMIC PROFILE", "UNIVERSITY EDUCATION",
        "COLLEGE EDUCATION", "EDUCATIONAL PROFILE", "ACADEMIC ACHIEVEMENTS",
        "EDUCATIONAL EXPERIENCE", "FORMAL EDUCATION", "ACADEMIC EXPERIENCE",
        "EDUCATION & CERTIFICATIONS", "DEGREES & DIPLOMAS", "QUALIFICATIONS",
        "EDUCATIONAL DETAILS", "ACADEMIC DETAILS"
    ]
    
    missing_skills = [
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
    ]
    
    missing_certifications = [
        "CERTIFICATIONS", "CERTIFICATES", "PROFESSIONAL CERTIFICATIONS",
        "LICENSES & CERTIFICATIONS", "CREDENTIALS", "PROFESSIONAL CREDENTIALS",
        "ACCREDITATIONS", "TRAINING & CERTIFICATIONS", "LICENSES",
        "PROFESSIONAL LICENSES", "CERTIFICATIONS & LICENSES", "CERTIFICATIONS & AWARDS",
        "PROFESSIONAL DEVELOPMENT", "CONTINUING EDUCATION", "TRAINING & DEVELOPMENT",
        "COURSES & CERTIFICATIONS", "ONLINE CERTIFICATIONS", "INDUSTRY CERTIFICATIONS",
        "TECHNICAL CERTIFICATIONS", "PROFESSIONAL TRAINING", "COMPLETED COURSES",
        "CERTIFICATIONS & COURSES", "AWARDS & CERTIFICATIONS", "BADGES & CERTIFICATIONS",
        "CERTIFICATION PROGRAMS", "DIGITAL BADGES", "CREDENTIAL HIGHLIGHTS"
    ]
    
    missing_projects = [
        "PROJECTS", "KEY PROJECTS", "PROJECT EXPERIENCE", "NOTABLE PROJECTS",
        "CASE STUDIES", "KEY PROJECTS & CASE STUDIES", "PERSONAL PROJECTS",
        "ACADEMIC PROJECTS", "PROFESSIONAL PROJECTS", "SIDE PROJECTS",
        "FREELANCE PROJECTS", "OPEN SOURCE PROJECTS", "RESEARCH PROJECTS",
        "MAJOR PROJECTS", "PROJECT HIGHLIGHTS", "SELECTED PROJECTS",
        "FEATURED PROJECTS", "PROJECT PORTFOLIO", "PORTFOLIO",
        "TECHNICAL PROJECTS", "PROJECT WORK", "PROJECTS & ACHIEVEMENTS",
        "PROJECTS UNDERTAKEN", "SIGNIFICANT PROJECTS", "INDEPENDENT PROJECTS",
        "CAPSTONE PROJECTS", "THESIS PROJECTS"
    ]
    
    missing_achievements = [
        "ACHIEVEMENTS", "ACCOMPLISHMENTS", "KEY ACHIEVEMENTS",
        "PROFESSIONAL ACHIEVEMENTS", "NOTABLE ACCOMPLISHMENTS", "HIGHLIGHTS",
        "KEY ACCOMPLISHMENTS", "AWARDS & ACHIEVEMENTS", "RECOGNITION",
        "HONORS & AWARDS", "AWARDS", "HONORS", "ACCOLADES",
        "DISTINCTIONS", "PROFESSIONAL RECOGNITION", "PERFORMANCE HIGHLIGHTS"
    ]
    
    missing_publications = [
        "PUBLICATIONS", "RESEARCH", "RESEARCH & PUBLICATIONS",
        "PAPERS", "PUBLISHED WORK", "AUTHORED WORKS", "ARTICLES",
        "BOOKS", "BOOK CHAPTERS", "CONFERENCE PAPERS", "JOURNAL ARTICLES",
        "SPEAKING ENGAGEMENTS", "CONFERENCES", "PRESENTATIONS",
        "KEYNOTES", "TALKS", "PODCASTS", "MEDIA", "PRESS",
        "PUBLICATIONS & SPEAKING", "THOUGHT LEADERSHIP"
    ]
    
    missing_languages = [
        "LANGUAGES", "LANGUAGE SKILLS", "SPOKEN LANGUAGES",
        "PROGRAMMING LANGUAGES", "LANGUAGE PROFICIENCY", "FOREIGN LANGUAGES",
        "MULTILINGUAL"
    ]
    
    missing_volunteer = [
        "VOLUNTEER", "VOLUNTEER EXPERIENCE", "VOLUNTEERING",
        "COMMUNITY SERVICE", "SOCIAL WORK", "NGO WORK",
        "COMMUNITY INVOLVEMENT", "CIVIC ENGAGEMENT", "NONPROFIT WORK",
        "COMMUNITY ACTIVITIES"
    ]
    
    missing_interests = [
        "INTERESTS", "HOBBIES", "PERSONAL INTERESTS",
        "HOBBIES & INTERESTS", "EXTRACURRICULAR", "ACTIVITIES",
        "PASSIONS", "OUTSIDE INTERESTS"
    ]
    
    missing_references = [
        "REFERENCES", "PROFESSIONAL REFERENCES",
        "REFERENCES AVAILABLE ON REQUEST", "REFEREES", "CHARACTER REFERENCES"
    ]
    
    print("\n📝 UPDATES TO MAKE:")
    print("1. Add these work experience aliases to SECTION_ALIASES['experience']:")
    for alias in missing_work_experience:
        print(f'        "{alias}",')
    
    print("\n2. Add these education aliases to SECTION_ALIASES['education']:")
    for alias in missing_education:
        print(f'        "{alias}",')
    
    print("\n3. Add these skills aliases to SECTION_ALIASES['skills']:")
    for alias in missing_skills:
        print(f'        "{alias}",')
    
    print("\n4. Add these certifications aliases to SECTION_ALIASES['certifications']:")
    for alias in missing_certifications:
        print(f'        "{alias}",')
    
    print("\n5. Add these projects aliases to SECTION_ALIASES['projects']:")
    for alias in missing_projects:
        print(f'        "{alias}",')
    
    print("\n6. Add these achievements aliases to SECTION_ALIASES['achievements']:")
    for alias in missing_achievements:
        print(f'        "{alias}",')
    
    print("\n7. Add these publications aliases to SECTION_ALIASES['publications']:")
    for alias in missing_publications:
        print(f'        "{alias}",')
    
    print("\n8. Add these languages aliases to SECTION_ALIASES['languages']:")
    for alias in missing_languages:
        print(f'        "{alias}",')
    
    print("\n9. Add these volunteer aliases to SECTION_ALIASES['volunteer']:")
    for alias in missing_volunteer:
        print(f'        "{alias}",')
    
    print("\n10. Add these interests aliases to SECTION_ALIASES['interests']:")
    for alias in missing_interests:
        print(f'        "{alias}",')
    
    print("\n11. Add these references aliases to SECTION_ALIASES['references']:")
    for alias in missing_references:
        print(f'        "{alias}",')
    
    print("\n🎯 LOCATION IN FILE:")
    print("Find line 485 in section_parser.py")
    print("Add new sections after existing 'experience' section")
    print("Make sure to close the SECTION_ALIASES dictionary properly")
    
    return {
        "work_experience": missing_work_experience,
        "education": missing_education,
        "skills": missing_skills,
        "certifications": missing_certifications,
        "projects": missing_projects,
        "achievements": missing_achievements,
        "publications": missing_publications,
        "languages": missing_languages,
        "volunteer": missing_volunteer,
        "interests": missing_interests,
        "references": missing_references
    }

if __name__ == "__main__":
    add_missing_aliases()
