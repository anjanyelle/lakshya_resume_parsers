#!/usr/bin/env python3
"""
STEP 7 — EXTEND SUMMARY EXTRACTOR
"""

def extend_summary_extractor():
    """Add new summary extraction formats to summary extractor"""
    
    print("=" * 120)
    print("🔍 STEP 7 — EXTEND SUMMARY EXTRACTOR")
    print("=" * 120)
    
    print("\n📋 FORMATS TO ADD:")
    
    formats = {
        "AFTER_SECTION_HEADER": {
            "pattern": r'^(PROFESSIONAL SUMMARY|SUMMARY|PROFILE|OBJECTIVE|ABOUT ME|CAREER SUMMARY|EXECUTIVE SUMMARY|CAREER OBJECTIVE|PROFESSIONAL PROFILE|PERSONAL PROFILE|CAREER OVERVIEW|PROFESSIONAL OVERVIEW|EXECUTIVE OVERVIEW|PROFESSIONAL OBJECTIVE|JOB OBJECTIVE|PERSONAL STATEMENT|PROFESSIONAL STATEMENT|COVER STATEMENT|PROFESSIONAL INTRODUCTION|CAREER INTRODUCTION|BRIEF PROFILE|BACKGROUND SUMMARY|WHO I AM|INTRODUCTION|HIGHLIGHTS|CAREER HIGHLIGHTS|KEY HIGHLIGHTS|PROFESSIONAL HIGHLIGHTS|PROFILE SUMMARY|ABOUT|BIO|BIOGRAPHY|PROFESSIONAL BIO)\s*[:]*\s*(.+?)$',
            "example": "PROFESSIONAL SUMMARY\nExperienced software engineer with 10+ years...",
            "description": "Extract summary after section header"
        },
        
        "AFTER_CONTACT_INFO": {
            "pattern": r'^(.+?)\n(.+?)\n(.+?)$',
            "example": "John Doe\njohn@example.com | (555) 123-4567 | LinkedIn\nExperienced software engineer with expertise in...",
            "description": "Extract first paragraph before any section header"
        },
        
        "MIXED_BULLETS_PARAGRAPHS": {
            "patterns": [
                r'^[\s]*[•\-*–—·]\s*(.+?)$',
                r'^[\s]*\d+\.\s*(.+?)$',
                r'^(.+?)$'
            ],
            "example": "• 10+ years experience in software development\n• Expert in Python, Java, and cloud technologies\n• Led teams of 5-10 engineers",
            "description": "Extract and join bullets and paragraphs"
        },
        
        "INLINE_WITH_HEADER": {
            "pattern": r'^(SUMMARY|PROFILE|OBJECTIVE|ABOUT|CAREER SUMMARY|EXECUTIVE SUMMARY|PROFESSIONAL SUMMARY)\s*:\s*(.+?)$',
            "example": "SUMMARY: 10+ years experience in software development...",
            "description": "Extract text after colon in same line"
        },
        
        "MULTIPLE_PARAGRAPHS": {
            "pattern": r'^(.+?)(?:\n\n|\r\n\r\n)(.+?)(?:\n\n|\r\n\r\n)(.+?)$',
            "example": "Experienced software engineer with 10+ years...\n\nSpecialized in cloud architecture...\n\nPassionate about mentoring...",
            "description": "Extract and join multiple paragraphs"
        }
    }
    
    for format_name, format_info in formats.items():
        print(f"\n  FORMAT {format_name}:")
        print(f"    Pattern: {format_info.get('pattern', format_info.get('patterns', 'Multiple patterns'))}")
        print(f"    Example: {format_info['example']}")
        print(f"    Description: {format_info['description']}")
    
    print("\n📝 SUMMARY CLEANING RULES:")
    cleaning_rules = [
        "Remove section header label from summary text",
        "Remove bullet point markers (•, -, *, 1., 2., etc.)",
        "Remove leading/trailing whitespace",
        "Remove duplicate newlines",
        "Normalize spacing between words",
        "Do NOT truncate — keep full summary text",
        "Preserve original formatting as much as possible",
        "Remove email/phone if accidentally included"
    ]
    
    for rule in cleaning_rules:
        print(f"  • {rule}")
    
    print("\n📋 SUMMARY DETECTION STRATEGY:")
    detection_strategy = [
        "1. Look for section headers (SUMMARY, PROFILE, OBJECTIVE, etc.)",
        "2. Extract first paragraph after contact info if no header",
        "3. Handle mixed bullet/paragraph formats",
        "4. Join multiple paragraphs with spaces",
        "5. Clean and normalize extracted text",
        "6. Validate minimum length (at least 10 characters)",
        "7. Remove duplicate or irrelevant content"
    ]
    
    for strategy in detection_strategy:
        print(f"  {strategy}")
    
    print("\n🎯 IMPLEMENTATION LOCATION:")
    print("File: backend/app/services/parser/summary_extractor.py")
    print("Function: extract_summary() [around line 50]")
    print("Add these patterns before existing summary detection logic")
    
    print("\n📋 SECTION HEADERS TO DETECT:")
    headers = [
        "PROFESSIONAL SUMMARY", "SUMMARY", "PROFILE", "OBJECTIVE", "ABOUT ME",
        "CAREER SUMMARY", "EXECUTIVE SUMMARY", "CAREER OBJECTIVE", 
        "PROFESSIONAL PROFILE", "PERSONAL PROFILE", "CAREER OVERVIEW",
        "PROFESSIONAL OVERVIEW", "EXECUTIVE OVERVIEW", "PROFESSIONAL OBJECTIVE",
        "JOB OBJECTIVE", "PERSONAL STATEMENT", "PROFESSIONAL STATEMENT",
        "COVER STATEMENT", "PROFESSIONAL INTRODUCTION", "CAREER INTRODUCTION",
        "BRIEF PROFILE", "BACKGROUND SUMMARY", "WHO I AM", "INTRODUCTION",
        "HIGHLIGHTS", "CAREER HIGHLIGHTS", "KEY HIGHLIGHTS",
        "PROFESSIONAL HIGHLIGHTS", "PROFILE SUMMARY", "ABOUT", "BIO",
        "BIOGRAPHY", "PROFESSIONAL BIO"
    ]
    
    for header in headers[:10]:  # Show first 10
        print(f"  • {header}")
    if len(headers) > 10:
        print(f"  • ... and {len(headers) - 10} more")
    
    return formats

if __name__ == "__main__":
    extend_summary_extractor()
