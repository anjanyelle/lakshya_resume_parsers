#!/usr/bin/env python3
"""
STEP 3 — EXTEND WORK EXPERIENCE PARSER
"""

def extend_work_experience_parser():
    """Add new work experience parsing formats to work_experience_parser.py"""
    
    print("=" * 120)
    print("🔍 STEP 3 — EXTEND WORK EXPERIENCE PARSER")
    print("=" * 120)
    
    print("\n📋 FORMATS TO ADD:")
    
    formats = {
        "PIPE_SEPARATOR": {
            "pattern": r'^##?\s*([^|]+?)\s*\|\s*([^|\n]+)\s*$',
            "example": "OBSIDIAN SHIELD DEFENSE | Seattle, WA",
            "description": "Extract company and location from pipe-separated format"
        },
        
        "STANDARD_TWO_LINE": {
            "pattern": r'^([A-Z][^|{(\n]+?)\s{2,}([A-Z][a-zA-Z\s,]+)$',
            "example": "Bank of America   North Carolina",
            "description": "Extract company and location from two-line format"
        },
        
        "CLIENT_ROLE_CONSULTING": {
            "patterns": [
                r'CLIENT\s*:\s*(.+?)(?:\s{2,}|\t|$)',
                r'Location\s*:\s*(.+)',
                r'ROLE\s*:\s*(.+)'
            ],
            "example": "CLIENT: Home Depot     Location: Atlanta, GA",
            "description": "Extract client, location, and role from consulting format"
        },
        
        "SINGLE_LINE_COMMA_PIPE": {
            "pattern": r'^([^,]+),\s*([^|]+)\s*\|\s*([^|]+)\s*\|\s*(.+)$',
            "example": "Google, Mountain View CA | Senior SWE | Jan2019 - Dec 2021",
            "description": "Extract company, location, role, dates from single line"
        },
        
        "EM_DASH_SEPARATOR": {
            "pattern": r'^([^—–]+?)\s*[—–]\s*(.+)$',
            "example": "Amazon — Hyderabad, India",
            "description": "Extract company and location from em-dash format"
        },
        
        "DATE_IN_PARENTHESES": {
            "pattern": r'^(.+?),\s*([^(]+)\s*\((.+?)\)$',
            "example": "Netflix, Los Gatos CA (March 2022 - Present)",
            "description": "Extract company, location, dates from parentheses format"
        },
        
        "TABLE_FORMAT": {
            "pattern": r'^\|(.+)\|(.+)\|(.+)\|$',
            "example": "| Company | Role | Duration |",
            "description": "Extract from table format with pipe separators"
        },
        
        "SLASH_SEPARATED": {
            "pattern": r'^(.+?)\s*/\s*(.+?)\s*/\s*(.+?)\s*/\s*(.+)$',
            "example": "Goldman Sachs / New York / VP Engineering / 2019-2022",
            "description": "Extract from slash-separated format"
        },
        
        "ENVIRONMENT_TECH_STACK": {
            "patterns": [
                r'^(?:Environment|Technologies|Tech Stack|Tools)\s*:\s*(.+)$',
                r'^(?:Environment|Technologies|Tech Stack|Tools)\s*[-–—]\s*(.+)$'
            ],
            "example": "Environment: Java, Spring Boot, AWS, Docker",
            "description": "Extract tech stack from environment lines"
        },
        
        "BULLET_DESCRIPTION": {
            "patterns": [
                r'^[\s]*[•\-*–—·○►→✓✔]\s*(.+)$',
                r'^[\s]*\d+\.\s*(.+)$',
                r'^[\s]*[a-zA-Z]\.\s*(.+)$'
            ],
            "example": "• Led team of 5 developers",
            "description": "Extract bullet points as descriptions"
        },
        
        "ABBREVIATED_MONTHS": {
            "pattern": r"([A-Za-z]+\.?\s*'?\d{2,4})",
            "example": "Jan '20 - Dec '21",
            "description": "Handle abbreviated month formats with apostrophe"
        },
        
        "YEAR_ONLY_DATES": {
            "pattern": r'(.+?)\s+(\d{4})\s*[-–]\s*(\d{4}|Present)',
            "example": "Google 2019-2022",
            "description": "Handle year-only date formats"
        }
    }
    
    for format_name, format_info in formats.items():
        print(f"\n  FORMAT {format_name}:")
        print(f"    Pattern: {format_info.get('pattern', format_info.get('patterns', 'Multiple patterns'))}")
        print(f"    Example: {format_info['example']}")
        print(f"    Description: {format_info['description']}")
    
    print("\n🎯 IMPLEMENTATION LOCATION:")
    print("File: backend/app/services/parser/work_experience_parser.py")
    print("Function: extract_jobs_from_text() [around line 600]")
    print("Add these patterns before existing company detection logic")
    
    print("\n📝 COMPANY NAME CLEANING RULES:")
    cleaning_rules = [
        "Strip: ##, #, **, *, CLIENT:, Client:, COMPANY:",
        "Strip leading/trailing spaces and special chars",
        "Convert ALL CAPS → Title Case",
        "But keep uppercase: IBM, TCS, ADP, HCL, GCP, AWS, VMware, SAP, HP, PwC, KPMG, EY, JPMC, HSBC, BofA, T-Mobile, AT&T, BBC, CNN, FBI, CIA, NASA"
    ]
    
    for rule in cleaning_rules:
        print(f"  • {rule}")
    
    print("\n📝 ENTRY BOUNDARY DETECTION:")
    boundaries = [
        "Line matches any company+location format",
        "Line has ## prefix", 
        "Line has CLIENT: prefix",
        "Blank line followed by company-like line",
        "Line is ALL CAPS and not a bullet point",
        "Line matches known company name pattern",
        "Next line has date range pattern"
    ]
    
    for boundary in boundaries:
        print(f"  • {boundary}")
    
    return formats

if __name__ == "__main__":
    extend_work_experience_parser()
