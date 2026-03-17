#!/usr/bin/env python3
"""
STEP 4 — EXTEND EDUCATION PARSER
"""

def extend_education_parser():
    """Add new education parsing formats to education_parser.py"""
    
    print("=" * 120)
    print("🔍 STEP 4 — EXTEND EDUCATION PARSER")
    print("=" * 120)
    
    print("\n📋 FORMATS TO ADD:")
    
    formats = {
        "DEGREE_UNIVERSITY_YEAR": {
            "pattern": r'^(.+?)\s*[-–—]\s*(.+?)\s*$',
            "example": "Master of Science in Cybersecurity & Information Assurance\nUniversity of Washington – Seattle, WA\nGraduated: 2017",
            "description": "Extract degree, university, year from multi-line format"
        },
        
        "UNIVERSITY_DEGREE": {
            "pattern": r'^(.+?)\s*\n(.+?)\s*\n(.+?)\s*$',
            "example": "Bharath University\nBachelor of Technology Computer Science\nAugust2010 to May2014",
            "description": "Extract university, degree, dates from multi-line format"
        },
        
        "SINGLE_LINE": {
            "patterns": [
                r'^(.+?),\s*(.+?),\s*(.+?),\s*(\d{4})$',
                r'^(.+?)\s*\|\s*(.+?)\s*\|\s*(\d{4})$'
            ],
            "example": "B.Tech Computer Science, Anna University, 2014",
            "description": "Extract degree, university, year from single line"
        },
        
        "DASH_SEPARATOR": {
            "pattern": r'^(.+?)\s*[-–—]\s*(.+?)\s*$',
            "example": "Bharath University - Bachelor of Technology",
            "description": "Extract university and degree from dash-separated format"
        },
        
        "INLINE_YEAR": {
            "patterns": [
                r'^(.+?)\s*\((\d{4}[-–]\d{4})\)',
                r'^(.+?)\s*\|\s*(\d{4})\s*\|'
            ],
            "example": "Bachelor of Technology (2010-2014)",
            "description": "Extract degree and year from inline format"
        },
        
        "WITH_GPA": {
            "pattern": r'GPA\s*:?\s*([\d.]+(?:/[\d.]+)?)',
            "example": "B.S. Computer Science | Stanford | GPA 3.8 | 2016-2020",
            "description": "Extract GPA from education entries"
        },
        
        "GRADUATED_KEYWORD": {
            "pattern": r'Graduated\s*:?\s*(?:in\s+)?(\d{4})',
            "example": "Graduated: 2017",
            "description": "Extract graduation year from graduated keyword"
        },
        
        "WITH_HONOURS": {
            "patterns": [
                r'\(First Class Honours\)',
                r'\(with Distinction\)',
                r'\(Summa Cum Laude\)',
                r'\(Magna Cum Laude\)'
            ],
            "example": "Bachelor of Science (First Class Honours)",
            "description": "Extract honours from degree"
        },
        
        "DISTANCE_ONLINE": {
            "patterns": [
                r'\(Distance Learning\)',
                r'\(Online Certificate\)',
                r'\(Remote\)'
            ],
            "example": "MBA (Distance Learning) - IGNOU - 2018",
            "description": "Handle distance/online education"
        }
    }
    
    for format_name, format_info in formats.items():
        print(f"\n  FORMAT {format_name}:")
        print(f"    Pattern: {format_info.get('pattern', format_info.get('patterns', 'Multiple patterns'))}")
        print(f"    Example: {format_info['example']}")
        print(f"    Description: {format_info['description']}")
    
    print("\n📋 DEGREE DETECTION KEYWORDS:")
    degree_keywords = [
        "Bachelor of Technology", "Bachelor of Engineering",
        "Bachelor of Science", "Bachelor of Arts", 
        "Bachelor of Commerce", "Bachelor of Business Administration",
        "Bachelor of Computer Applications",
        "Master of Technology", "Master of Engineering",
        "Master of Science", "Master of Arts", "Master of Commerce",
        "Master of Business Administration", "Master of Computer Applications",
        "Master of Computer Science", "Doctor of Philosophy", "Doctor of Medicine",
        "B.Tech", "M.Tech", "B.E", "M.E", "B.Sc", "M.Sc",
        "B.Com", "M.Com", "BBA", "MBA", "BCA", "MCA",
        "B.A", "M.A", "Ph.D", "PhD", "DPhil", "EdD",
        "Associate Degree", "Diploma", "Certificate", "High School Diploma", "GED",
        "Post Graduate Diploma", "PGD", "PGDM"
    ]
    
    for keyword in degree_keywords[:10]:  # Show first 10
        print(f"  • {keyword}")
    print(f"  • ... and {len(degree_keywords) - 10} more")
    
    print("\n📋 LEVEL MAPPING:")
    level_mapping = {
        "Undergraduate": ["Bachelor", "B.Tech", "B.E", "B.Sc", "BCA", "BBA", "B.Com", "B.A", "Associate Degree", "Diploma", "High School"],
        "Postgraduate": ["Master", "M.Tech", "M.E", "M.Sc", "MBA", "MCA", "M.Com", "M.A", "PGD", "PGDM"],
        "Doctorate": ["Ph.D", "PhD", "DPhil", "Doctor", "EdD"]
    }
    
    for level, degrees in level_mapping.items():
        print(f"\n  {level}:")
        for degree in degrees[:5]:  # Show first 5
            print(f"    • {degree}")
        if len(degrees) > 5:
            print(f"    • ... and {len(degrees) - 5} more")
    
    print("\n🎯 IMPLEMENTATION LOCATION:")
    print("File: backend/app/services/parser/education_parser.py")
    print("Function: parse_education() [around line 100]")
    print("Add these patterns before existing degree detection logic")
    
    print("\n📝 INSTITUTION CLEANING:")
    cleaning_rules = [
        "Remove city, state, country after – or , or |",
        "Remove year from institution name",
        "Keep only university/college name",
        "University of Washington – Seattle, WA → University of Washington",
        "Bharath University - Bachelor of Technology... → Bharath University"
    ]
    
    for rule in cleaning_rules:
        print(f"  • {rule}")
    
    return formats

if __name__ == "__main__":
    extend_education_parser()
