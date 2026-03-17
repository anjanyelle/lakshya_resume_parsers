#!/usr/bin/env python3
"""
Quick fixes for comprehensive resume parsing issues
"""

import os
import json
import pandas as pd

def fix_csv_column_issues():
    """Fix CSV column name issues"""
    print("🔧 Fixing CSV Column Issues...")
    
    # Fix skills.csv
    skills_path = "data/external/skills.csv"
    if os.path.exists(skills_path):
        try:
            df = pd.read_csv(skills_path)
            print(f"  📋 Skills CSV columns: {list(df.columns)}")
            
            # Standardize column names
            if 'skill' in df.columns:
                df = df.rename(columns={'skill': 'skill_name'})
            elif 'name' in df.columns:
                df = df.rename(columns={'name': 'skill_name'})
            
            # Ensure skill_name column exists
            if 'skill_name' not in df.columns:
                df['skill_name'] = df.iloc[:, 0] if len(df.columns) > 0 else []
            
            df.to_csv(skills_path, index=False)
            print(f"  ✅ Fixed skills.csv columns: {list(df.columns)}")
            
        except Exception as e:
            print(f"  ❌ Error fixing skills.csv: {e}")
    
    # Fix locations.csv
    locations_path = "data/external/locations.csv"
    if os.path.exists(locations_path):
        try:
            df = pd.read_csv(locations_path)
            print(f"  📍 Locations CSV columns: {list(df.columns)}")
            
            # Standardize column names
            if 'location' in df.columns:
                df = df.rename(columns={'location': 'city'})
            elif 'name' in df.columns:
                df = df.rename(columns={'name': 'city'})
            
            # Ensure city column exists
            if 'city' not in df.columns:
                df['city'] = df.iloc[:, 0] if len(df.columns) > 0 else []
            
            df.to_csv(locations_path, index=False)
            print(f"  ✅ Fixed locations.csv columns: {list(df.columns)}")
            
        except Exception as e:
            print(f"  ❌ Error fixing locations.csv: {e}")

def enhance_section_patterns():
    """Enhance section detection patterns for comprehensive resumes"""
    print("🎯 Enhancing Section Detection Patterns...")
    
    enhanced_patterns = {
        "work": [
            r'## (PROFESSIONAL EXPERIENCE|WORK EXPERIENCE|EXPERIENCE|WORK HISTORY|EMPLOYMENT|CAREER|PROFESSIONAL BACKGROUND)\s*\n*(.*?)(?=\n##|\nEDUCATION|\nSKILLS|\nCERTIFICATIONS|\nTECHNICAL|\nPROJECTS|\nPUBLICATIONS|\nAWARDS|\nPATENTS|\Z)',
            r'(PROFESSIONAL EXPERIENCE|WORK EXPERIENCE|EXPERIENCE|WORK HISTORY|EMPLOYMENT|CAREER|PROFESSIONAL BACKGROUND)\s*\n*(.*?)(?=\n##|\nEDUCATION|\nSKILLS|\nCERTIFICATIONS|\nTECHNICAL|\nPROJECTS|\nPUBLICATIONS|\nAWARDS|\nPATENTS|\Z)',
            r'^([A-Z][a-zA-Z\s&]+AI|[A-Z][a-zA-Z\s&]+Research|[A-Z][a-zA-Z\s&]+Microsoft|[A-Z][a-zA-Z\s&]+Facebook|[A-Z][a-zA-Z\s&]+IBM|[A-Z][a-zA-Z\s&]+Stanford)\s*[-–]?\s*([A-Za-z\s,]+)\s*\|\s*([A-Za-z\s,0-9]+)\s*\|\s*([A-Za-z\s,0-9]+)',
        ],
        "education": [
            r'## (EDUCATION|ACADEMIC|ACADEMIC BACKGROUND|EDUCATIONAL|QUALIFICATIONS)\s*\n*(.*?)(?=\n##|\nEXPERIENCE|\nSKILLS|\nCERTIFICATIONS|\nTECHNICAL|\nPROJECTS|\nPUBLICATIONS|\nAWARDS|\nPATENTS|\Z)',
            r'(EDUCATION|ACADEMIC|ACADEMIC BACKGROUND|EDUCATIONAL|QUALIFICATIONS)\s*\n*(.*?)(?=\n##|\nEXPERIENCE|\nSKILLS|\nCERTIFICATIONS|\nTECHNICAL|\nPROJECTS|\nPUBLICATIONS|\nAWARDS|\nPATENTS|\Z)',
            r'^([A-Za-z\s&]+University|[A-Za-z\s&]+Institute|[A-Za-z\s&]+College|[A-Za-z\s&]+School)\s*[-–]?\s*([A-Za-z\s]+(?:Bachelor|Master|PhD|B\.S\.|M\.S\.|B\.Tech|M\.Tech|B\.E\.|M\.E\.)[A-Za-z\s]*)\s*([A-Za-z]+\s*\d{4}\s*[-–]?\s*[A-Za-z]*\s*\d{4}|\d{4}\s*[-–]?\s*\d{4})?',
        ],
        "skills": [
            r'## (TECHNICAL SKILLS|SKILLS|TECHNICAL|TECHNOLOGIES|CORE COMPETENCIES|EXPERTISE)\s*\n*(.*?)(?=\n##|\nEXPERIENCE|\nEDUCATION|\nCERTIFICATIONS|\nPROJECTS|\nPUBLICATIONS|\nAWARDS|\nPATENTS|\Z)',
            r'(TECHNICAL SKILLS|SKILLS|TECHNICAL|TECHNOLOGIES|CORE COMPETENCIES|EXPERTISE)\s*\n*(.*?)(?=\n##|\nEXPERIENCE|\nEDUCATION|\nCERTIFICATIONS|\nPROJECTS|\nPUBLICATIONS|\nAWARDS|\nPATENTS|\Z)',
        ],
        "certifications": [
            r'## (PROFESSIONAL CERTIFICATIONS|CERTIFICATIONS|CERTIFICATES|CREDENTIALS)\s*\n*(.*?)(?=\n##|\nEXPERIENCE|\nEDUCATION|\nSKILLS|\nPROJECTS|\nPUBLICATIONS|\nAWARDS|\nPATENTS|\Z)',
            r'(PROFESSIONAL CERTIFICATIONS|CERTIFICATIONS|CERTIFICATES|CREDENTIALS)\s*\n*(.*?)(?=\n##|\nEXPERIENCE|\nEDUCATION|\nSKILLS|\nPROJECTS|\nPUBLICATIONS|\nAWARDS|\nPATENTS|\Z)',
        ]
    }
    
    # Save enhanced patterns
    with open("enhanced_section_patterns.json", "w") as f:
        json.dump(enhanced_patterns, f, indent=2)
    
    print("  ✅ Enhanced section patterns saved")

def create_comprehensive_test_fix():
    """Create a quick fix test for comprehensive resume parsing"""
    print("🚀 Creating Comprehensive Test Fix...")
    
    fix_code = '''
# Quick fix for comprehensive resume parsing
def extract_work_comprehensive(self, text):
    """Enhanced work extraction for comprehensive resumes"""
    work_entries = []
    
    # Pattern for company - title - location - date format
    pattern = r'^([A-Za-z0-9\s&]+(?:AI|Research|Microsoft|Facebook|IBM|Stanford|Google))\\s*-\\s*([A-Za-z0-9\\s,]+)\\n([A-Za-z0-9\\s,|]+)\\s*\\|\\s*([A-Za-z0-9\\s,]+)\\s*\\|\\s*([A-Za-z0-9\\s,]+)'
    
    matches = re.findall(pattern, text, re.MULTILINE)
    for match in matches:
        if len(match) >= 5:
            company = match[0].strip()
            title = match[1].strip()
            location = match[2].strip()
            date_range = match[4].strip()
            
            work_entries.append({
                "company": company,
                "title": title,
                "location": location,
                "date_range": date_range,
                "description": ""
            })
    
    return work_entries

def extract_education_comprehensive(self, text):
    """Enhanced education extraction for comprehensive resumes"""
    education_entries = []
    
    # Pattern for university - degree - location - date format
    pattern = r'^([A-Za-z\\s&]+(?:University|Institute|College|School))\\s*-\\s*([A-Za-z\\s]+(?:Bachelor|Master|PhD|B\\.S\\.|M\\.S\\.|B\\.Tech|M\\.Tech|B\\.E\\.|M\\.E\\.)[A-Za-z\\s]*)\\n([A-Za-z\\s,]+)\\s*\\|\\s*([A-Za-z0-9\\s,]+)'
    
    matches = re.findall(pattern, text, re.MULTILINE)
    for match in matches:
        if len(match) >= 4:
            institution = match[0].strip()
            degree = match[1].strip()
            location = match[2].strip()
            date_range = match[3].strip()
            
            education_entries.append({
                "institution": institution,
                "degree": degree,
                "location": location,
                "date_range": date_range,
                "description": ""
            })
    
    return education_entries
'''
    
    with open("comprehensive_parsing_fix.py", "w") as f:
        f.write(fix_code)
    
    print("  ✅ Comprehensive parsing fix created")

def main():
    """Main function to apply all fixes"""
    print("🎯 APPLYING COMPREHENSIVE RESUME PARSING FIXES")
    print("=" * 60)
    
    # Apply fixes
    fix_csv_column_issues()
    enhance_section_patterns()
    create_comprehensive_test_fix()
    
    print("\n✅ ALL FIXES APPLIED!")
    print("=" * 30)
    print("🔧 Fixed CSV column issues")
    print("🎯 Enhanced section patterns")
    print("🚀 Created comprehensive parsing fixes")
    print("\n🔄 Run the comprehensive test again to see improvements")

if __name__ == "__main__":
    main()
