#!/usr/bin/env python3
"""
STEP 9 — EXTEND PROJECTS PARSER
"""

def extend_projects_parser():
    """Add new projects parsing formats to projects parser"""
    
    print("=" * 120)
    print("🔍 STEP 9 — EXTEND PROJECTS PARSER")
    print("=" * 120)
    
    print("\n📋 FORMATS TO ADD:")
    
    formats = {
        "HEADER_FIELDS": {
            "patterns": [
                r'Project:\s*"([^"]+)"\s*[-–—]\s*(.+?)$',  # Project: "Name" – Description
                r'•\s*Company:\s*(.+?)$',  # Company: Name
                r'•\s*Role:\s*(.+?)$',  # Role: Title
                r'•\s*Budget:\s*(.+?)$',  # Budget: Amount
                r'•\s*Challenge:\s*(.+?)$',  # Challenge: Description
                r'•\s*Solution:\s*(.+?)$',  # Solution: Description
                r'•\s*Outcome:\s*(.+?)$'  # Outcome: Result
            ],
            "example": 'Project: "Iron Dome" – Zero Trust Architecture\n• Company: Obsidian Shield Defense\n• Role: Principal Architect\n• Budget: $4.8M\n• Challenge: ...\n• Solution: ...\n• Outcome: ...',
            "description": "Extract project details from header+fields format"
        },
        
        "INLINE_TITLE": {
            "pattern": r'^([^|]+)\s*\|\s*([^|]+)\s*\|\s*(.+?)$',
            "example": "Iron Dome | Obsidian Shield Defense | Principal Architect",
            "description": "Extract project name, company, role from inline format"
        },
        
        "GITHUB_LINK": {
            "patterns": [
                r'^(.+?)\s*\|\s*(?:https?://)?(?:www\.)?github\.com/([^/\s]+)(?:/([^/\s]+))?',  # GitHub URL
                r'Tech:\s*(.+?)$'  # Technologies line
            ],
            "example": "Personal Finance App | github.com/user/finance-app\nTech: React, Node.js, PostgreSQL",
            "description": "Extract project name, GitHub URL, technologies"
        },
        
        "ACADEMIC_PROJECT": {
            "patterns": [
                r'^(?:Final Year Project|Capstone Project|Thesis Project):\s*(.+?)$',  # Project name
                r'Technologies?:\s*(.+?)$',  # Technologies
                r'(?:Advisor|Supervisor):\s*(.+?)$',  # Advisor
                r'(?:Duration|Period):\s*(.+?)$'  # Duration
            ],
            "example": "Final Year Project: ML-based Resume Parser\nTechnologies: Python, spaCy, scikit-learn\nAdvisor: Dr. Smith\nDuration: 6 months",
            "description": "Extract academic project details"
        },
        
        "MULTI_LINE_PROJECT": {
            "patterns": [
                r'^(.+?)$',  # Project name (first line)
                r'^(.+?)$',  # Company/Organization (second line)
                r'^(.+?)$',  # Role/Position (third line)
                r'^(.+?)$',  # Duration (fourth line)
                r'^(.+?)$'  # Description (fifth line)
            ],
            "example": "E-Commerce Platform\nTech Solutions Inc.\nFull Stack Developer\nJan 2022 - Jun 2022\nBuilt a complete e-commerce solution using React and Node.js",
            "description": "Extract from multi-line project format"
        },
        
        "BULLET_PROJECTS": {
            "patterns": [
                r'^[\s]*[•\-*–—·]\s*(.+?)$',  # Bullet point
                r'^(.+?)\s*\[-–—]\s*(.+?)$',  # Project - Description
                r'^(.+?)\s*\|\s*(.+?)$'  # Project | Details
            ],
            "example": "• Built RESTful API using Spring Boot and MySQL\n• Developed responsive frontend with React and TypeScript\n• Implemented CI/CD pipeline using Jenkins and Docker",
            "description": "Extract from bullet point project descriptions"
        },
        
        "TIMELINE_PROJECT": {
            "patterns": [
                r'^(.+?)\s*\((\d{4}[-–]\d{4})\)',  # Project with year range
                r'^(.+?)\s*\((\d{4})\)',  # Project with single year
                r'^(.+?)\s*\((.+?)\)'  # Project with custom date
            ],
            "example": "Cloud Migration Project (2021-2022)\nData Analytics Dashboard (2022)\nMobile App Development (Q1 2023)",
            "description": "Extract project name and timeline"
        },
        
        "TEAM_PROJECT": {
            "patterns": [
                r'^(?:Team|Group)\s*Size:\s*(\d+)',  # Team size
                r'^(?:My\s*)?Role:\s*(.+?)$',  # Role in team
                r'^(?:Team\s*)?Lead(?:er)?:\s*(.+?)$',  # Team leader
                r'^(?:Collaboration|Teamwork):\s*(.+?)$'  # Collaboration details
            ],
            "example": "Team Size: 5\nMy Role: Backend Developer\nTeam Leader: John Doe\nCollaboration: Agile methodology with daily standups",
            "description": "Extract team-based project information"
        },
        
        "ACHIEVEMENT_PROJECT": {
            "patterns": [
                r'^(?:Achievement|Result|Impact):\s*(.+?)$',  # Achievement
                r'^(?:Metric|KPI|Performance):\s*(.+?)$',  # Metrics
                r'^(?:Award|Recognition):\s*(.+?)$',  # Awards
                r'^(?:Success|Outcome):\s*(.+?)$'  # Success metrics
            ],
            "example": "Achievement: Reduced processing time by 60%\nMetric: Improved user satisfaction from 75% to 95%\nAward: Best Project of the Year",
            "description": "Extract achievements and metrics from projects"
        }
    }
    
    for format_name, format_info in formats.items():
        print(f"\n  FORMAT {format_name}:")
        print(f"    Patterns: {format_info.get('patterns', format_info.get('pattern', 'Single pattern'))}")
        print(f"    Example: {format_info['example']}")
        print(f"    Description: {format_info['description']}")
    
    print("\n📋 PROJECT FIELDS TO EXTRACT:")
    fields = [
        "name: Project title/name",
        "company: Organization/company",
        "role: Position/contribution",
        "description: Detailed description",
        "technologies: List of technologies used",
        "url: GitHub/Portfolio links",
        "duration: Start and end dates",
        "team_size: Number of team members",
        "budget: Project budget if available",
        "outcome: Results and achievements",
        "challenge: Problems addressed",
        "solution: Approach taken",
        "advisor: Academic advisor (for student projects)",
        "award: Recognition received"
    ]
    
    for field in fields:
        print(f"  • {field}")
    
    print("\n📝 PROJECT CLEANING RULES:")
    cleaning_rules = [
        "Remove quotes from project names",
        "Standardize date formats",
        "Extract technologies from descriptions",
        "Clean company names (same rules as work experience)",
        "Normalize role titles",
        "Remove duplicate technologies",
        "Extract URLs and validate format",
        "Clean bullet points from descriptions",
        "Handle special characters in project names"
    ]
    
    for rule in cleaning_rules:
        print(f"  • {rule}")
    
    print("\n📋 PROJECT DETECTION STRATEGY:")
    detection_strategy = [
        "1. Look for PROJECTS section header",
        "2. Identify project entry boundaries",
        "3. Extract project names from various formats",
        "4. Parse project details using multiple patterns",
        "5. Extract technologies from dedicated lines or descriptions",
        "6. Handle academic vs professional projects differently",
        "7. Extract URLs and validate them",
        "8. Clean and normalize all extracted data",
        "9. Validate minimum required fields (name, description)"
    ]
    
    for strategy in detection_strategy:
        print(f"  {strategy}")
    
    print("\n🎯 IMPLEMENTATION LOCATION:")
    print("File: backend/app/services/parser/projects_parser.py")
    print("Function: parse_projects() [around line 50]")
    print("Add these patterns before existing project detection logic")
    
    return formats

if __name__ == "__main__":
    extend_projects_parser()
