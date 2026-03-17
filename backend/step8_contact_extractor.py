#!/usr/bin/env python3
"""
STEP 8 — EXTEND CONTACT INFO EXTRACTOR
"""

def extend_contact_info_extractor():
    """Add new contact info extraction formats to contact extractor"""
    
    print("=" * 120)
    print("🔍 STEP 8 — EXTEND CONTACT INFO EXTRACTOR")
    print("=" * 120)
    
    print("\n📋 FORMATS TO ADD:")
    
    formats = {
        "NAME_FORMATS": {
            "patterns": [
                r'^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)$',  # Title Case
                r'^([A-Z][A-Z\s]+)$',  # ALL CAPS
                r'^([A-Z][a-z]+\s+[A-Z]\.\s*[A-Z][a-z]+)$',  # With middle initial
                r'^(?:Dr\.?|Prof\.?|Mr\.?|Ms\.?|Mrs\.?)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)$',  # With prefix
                r'^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\s*,\s*(?:Ph\.?D|Master|MBA|B\.?S|M\.?S)$',  # With suffix
                r'^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\s*\|\s*.+?$',  # With extra info
            ],
            "examples": [
                "John Doe",
                "JOHN DOE", 
                "John T. Doe",
                "Dr. John Doe",
                "John Doe, PhD",
                "John Doe | LinkedIn"
            ],
            "description": "Extract name from various formats"
        },
        
        "EMAIL_FORMATS": {
            "pattern": r'\b[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}\b',
            "examples": [
                "john.doe@company.com",
                "john+tag@domain.com",
                "john@sub.domain.com",
                "first.last@company.co.uk"
            ],
            "description": "Extract email addresses with various formats"
        },
        
        "PHONE_FORMATS": {
            "patterns": [
                r'\+?1?\s*\(?(\d{3})\)?[-.\s]*(\d{3})[-.\s]*(\d{4})',  # US format
                r'\+?(\d{1,3})[-.\s]*(\d{1,4})[-.\s]*(\d{1,4})[-.\s]*(\d{1,9})',  # International
                r'\+?\d{10,15}',  # Simple international
            ],
            "examples": [
                "+1 (206) 555-0142",
                "(206) 555-0142", 
                "206-555-0142",
                "206.555.0142",
                "+18595679177",
                "+91 98765 43210"
            ],
            "description": "Extract phone numbers in various formats"
        },
        
        "LINKEDIN_FORMATS": {
            "patterns": [
                r'(?:https?://)?(?:www\.)?linkedin\.com/in/([a-zA-Z0-9-]+)/?',
                r'(?:LinkedIn|LI):\s*(?:https?://)?(?:www\.)?linkedin\.com/in/([a-zA-Z0-9-]+)/?',
                r'linkedin\.com/in/([a-zA-Z0-9-]+)'
            ],
            "examples": [
                "linkedin.com/in/johndoe",
                "www.linkedin.com/in/johndoe",
                "https://linkedin.com/in/johndoe",
                "LinkedIn: linkedin.com/in/johndoe",
                "LI: linkedin.com/in/johndoe"
            ],
            "description": "Extract LinkedIn profile URLs"
        },
        
        "GITHUB_FORMATS": {
            "patterns": [
                r'(?:https?://)?(?:www\.)?github\.com/([a-zA-Z0-9-]+)/?',
                r'GitHub:\s*(?:https?://)?(?:www\.)?github\.com/([a-zA-Z0-9-]+)/?',
                r'github\.com/([a-zA-Z0-9-]+)'
            ],
            "examples": [
                "github.com/johndoe",
                "www.github.com/johndoe",
                "https://github.com/johndoe",
                "GitHub: github.com/johndoe"
            ],
            "description": "Extract GitHub profile URLs"
        },
        
        "LOCATION_FORMATS": {
            "patterns": [
                r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*),\s*([A-Z]{2})',  # City, State
                r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*),\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',  # City, Country
                r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*),\s*([A-Z]{2})\s*(\d{5})',  # City, State ZIP
                r'(?:Location|Located in|Based in):\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*,\s*(?:[A-Z]{2}|[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*))',  # With label
                r'(San Francisco Bay Area|New York Metropolitan Area|Remote)',  # Special cases
            ],
            "examples": [
                "Seattle, WA",
                "Seattle, Washington",
                "Seattle, WA 98101",
                "Location: Seattle, Washington",
                "San Francisco Bay Area",
                "Remote"
            ],
            "description": "Extract location in various formats"
        }
    }
    
    for format_name, format_info in formats.items():
        print(f"\n  FORMAT {format_name}:")
        print(f"    Patterns: {format_info.get('patterns', format_info.get('pattern', 'Single pattern'))}")
        print(f"    Examples: {format_info['examples']}")
        print(f"    Description: {format_info['description']}")
    
    print("\n📝 CONTACT INFO CLEANING RULES:")
    cleaning_rules = [
        "Remove extra whitespace from names",
        "Standardize phone format (remove extra spaces, dashes)",
        "Normalize URLs (ensure https:// prefix)",
        "Extract city and state from location",
        "Handle special location cases (Bay Area, Remote)",
        "Remove duplicate contact information",
        "Validate email format",
        "Extract username from social media URLs"
    ]
    
    for rule in cleaning_rules:
        print(f"  • {rule}")
    
    print("\n📋 CONTACT DETECTION STRATEGY:")
    detection_strategy = [
        "1. Scan entire resume for contact patterns",
        "2. Prioritize contact info at top of resume",
        "3. Extract name from first line if it looks like a name",
        "4. Find email addresses using regex pattern",
        "5. Extract phone numbers in various formats",
        "6. Find LinkedIn and GitHub profiles",
        "7. Extract location information",
        "8. Clean and normalize all extracted data",
        "9. Validate extracted information"
    ]
    
    for strategy in detection_strategy:
        print(f"  {strategy}")
    
    print("\n🎯 IMPLEMENTATION LOCATION:")
    print("File: backend/app/services/parser/contact_extractor.py")
    print("Function: extract_contact_info() [around line 50]")
    print("Add these patterns before existing contact detection logic")
    
    return formats

if __name__ == "__main__":
    extend_contact_info_extractor()
