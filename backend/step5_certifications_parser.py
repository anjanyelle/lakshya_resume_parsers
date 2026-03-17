#!/usr/bin/env python3
"""
STEP 5 — EXTEND CERTIFICATIONS PARSER
"""

def extend_certifications_parser():
    """Add new certification parsing formats to certification_parser.py"""
    
    print("=" * 120)
    print("🔍 STEP 5 — EXTEND CERTIFICATIONS PARSER")
    print("=" * 120)
    
    print("\n📋 FORMATS TO ADD:")
    
    formats = {
        "ACRONYM_DASH_FULL_NAME": {
            "pattern": r'^(.+?)\s*[-–—]\s*(.+?)\s*\((.+?)\)$',
            "example": "CISSP – Certified Information Systems Security Professional (ISC)²",
            "description": "Extract acronym, full name, and issuer from dash format"
        },
        
        "WITH_LICENSE_NUMBER": {
            "patterns": [
                r'License\s*#?\s*(\w+)',
                r'Credential\s*(?:ID)?\s*:?\s*([\w-]+)',
                r'ID\s*:?\s*([\w-]+)'
            ],
            "example": "CISSP – Certified... (ISC)² | License #559201",
            "description": "Extract license/credential ID without creating separate cert"
        },
        
        "WITH_DATE_RANGE": {
            "pattern": r'^(.+?)\s*\|\s*(\d{4})\s*[-–]\s*(\d{7})',
            "example": "AWS Certified Developer – Associate | 2024 – 2027",
            "description": "Extract cert name and validity dates"
        },
        
        "ISSUED_BY_NEXT_LINE": {
            "pattern": r'^(.+?)\s*\nIssued by:\s*(.+?)\s*\nValid:\s*(\d{4}[-–]\d{7})',
            "example": "AWS Certified Developer\nIssued by: Amazon Web Services\nValid: 2024-2027",
            "description": "Handle multi-line certification format"
        },
        
        "SIMPLE_LIST": {
            "pattern": r'^(.+?)$',
            "example": "AWS Certified Developer - Associate",
            "description": "One cert per line format"
        },
        
        "NUMBERED_LIST": {
            "pattern": r'^\d+\.\s*(.+?)$',
            "example": "1. AWS Certified Solutions Architect",
            "description": "Strip number prefix from numbered list"
        },
        
        "BULLET_LIST": {
            "pattern": r'^[\s]*[•\-*–—·]\s*(.+?)$',
            "example": "• CISSP – Certified Information Systems Security Professional",
            "description": "Strip bullet prefix from bullet list"
        },
        
        "WITH_YEAR_ONLY": {
            "patterns": [
                r'\((\d{4})\)',
                r'[-–]\s*(\d{4})$'
            ],
            "example": "AWS Certified Developer (2024)",
            "description": "Extract year from parentheses or end of line"
        },
        
        "COMMA_SEPARATED": {
            "pattern": r'^(.+?),\s*(.+?),\s*(.+?),\s*(.+?)$',
            "example": "CISSP, CISM, CISA, GCIH, GCFA",
            "description": "Split comma-separated certifications"
        },
        
        "COLON_SEPARATED": {
            "pattern": r'^Certification:\s*(.+?)$',
            "example": "Certification: AWS Solutions Architect",
            "description": "Extract from colon-separated format"
        },
        
        "IN_PROGRESS": {
            "patterns": [
                r'\(In Progress\)',
                r'\(Expected \d{4}\)',
                r'\(Ongoing\)'
            ],
            "example": "AWS Certified Developer (In Progress)",
            "description": "Handle in-progress certifications"
        }
    }
    
    for format_name, format_info in formats.items():
        print(f"\n  FORMAT {format_name}:")
        print(f"    Pattern: {format_info.get('pattern', format_info.get('patterns', 'Multiple patterns'))}")
        print(f"    Example: {format_info['example']}")
        print(f"    Description: {format_info['description']}")
    
    print("\n📋 ISSUER DETECTION RULES:")
    issuer_rules = [
        "(ISC)² or (ISC2) → ISC2",
        "(ISACA) → ISACA", 
        "(SANS Institute) or (SANS) → SANS Institute",
        "(PMI) → PMI",
        "(Google) → Google",
        "(Microsoft) → Microsoft",
        "(Amazon) or (AWS) → Amazon Web Services",
        "(Oracle) → Oracle",
        "(Cisco) → Cisco",
        "(CompTIA) → CompTIA",
        "(Linux Foundation) → Linux Foundation",
        "(HashiCorp) → HashiCorp",
        "(Kubernetes) or (CNCF) → CNCF",
        "(Red Hat) → Red Hat"
    ]
    
    for rule in issuer_rules:
        print(f"  • {rule}")
    
    print("\n📋 NAME-BASED ISSUER DETECTION:")
    name_based_issuers = [
        "AWS or Azure → Amazon Web Services/Microsoft",
        "Google or GCP → Google",
        "Oracle → Oracle",
        "Cisco or CCNA → Cisco",
        "PMP → PMI",
        "CISSP or CCSP → ISC2",
        "CISM or CISA or CRISC → ISACA",
        "GCIH or GCFA or GPEN → SANS Institute",
        "RHCE or RHCSA → Red Hat",
        "CKA or CKAD → CNCF"
    ]
    
    for rule in name_based_issuers:
        print(f"  • {rule}")
    
    print("\n🎯 IMPLEMENTATION LOCATION:")
    print("File: backend/app/services/parser/certification_parser.py")
    print("Function: parse_certifications() [around line 50]")
    print("Add these patterns before existing cert detection logic")
    
    print("\n📝 NAME CLEANING RULES:")
    cleaning_rules = [
        "Remove issuer in brackets from name end",
        "Remove license number from name",
        "Remove dates from name",
        "Trim dashes and spaces",
        "DO NOT create 'License #559201' as separate cert"
    ]
    
    for rule in cleaning_rules:
        print(f"  • {rule}")
    
    return formats

if __name__ == "__main__":
    extend_certifications_parser()
