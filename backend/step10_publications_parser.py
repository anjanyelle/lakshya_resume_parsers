#!/usr/bin/env python3
"""
STEP 10 — EXTEND PUBLICATIONS PARSER
"""

def extend_publications_parser():
    """Add new publications parsing formats to publications parser"""
    
    print("=" * 120)
    print("🔍 STEP 10 — EXTEND PUBLICATIONS PARSER")
    print("=" * 120)
    
    print("\n📋 FORMATS TO ADD:")
    
    formats = {
        "KEYNOTE": {
            "patterns": [
                r'Keynote\s+Speaker,\s*(.+?)\s*(\d{4}):',  # Keynote Speaker, Conference Year:
                r'Session:\s*(.+?)$',  # Session: Title
                r'Topic:\s*(.+?)$',  # Topic: Description
                r'Venue:\s*(.+?)$'  # Venue: Conference name
            ],
            "example": "Keynote Speaker, RSA Conference 2024:\nSession: The CISO as a Business Leader",
            "description": "Extract keynote speaker information"
        },
        
        "PANELIST": {
            "patterns": [
                r'Panelist,\s*(.+?)\s*(\d{4}):',  # Panelist, Conference Year:
                r'Topic:\s*(.+?)$',  # Topic: Description
                r'Venue:\s*(.+?)$',  # Venue: Conference name
                r'Moderator:\s*(.+?)$'  # Moderator: Name
            ],
            "example": "Panelist, Black Hat USA 2023:\nTopic: Defending Critical Infrastructure",
            "description": "Extract panelist information"
        },
        
        "AUTHOR": {
            "patterns": [
                r'Author:\s*(.+?)\s*[-–—]\s*(.+?)$',  # Author: Name - Title
                r'^(.+?)\s*[-–—]\s*(.+?)\s*[-–—]\s*(.+?)$',  # Name - Title - Publisher
                r'ISBN:\s*(.+?)$',  # ISBN: Number
                r'Published:\s*(\d{4})'  # Published: Year
            ],
            "example": "Author: The Handbook of SOC Automation – O'Reilly Media",
            "description": "Extract author and book information"
        },
        
        "PODCAST": {
            "patterns": [
                r'Podcast\s+Guest:\s*(.+?)\s*[-–—]\s*(.+?)$',  # Podcast Guest: Show - Episode
                r'Episode\s*(\d+):',  # Episode Number
                r'Title:\s*(.+?)$',  # Title: Episode title
                r'Date:\s*(.+?)$'  # Date: Publication date
            ],
            "example": "Podcast Guest: Blueprint for Defense – Episode 45",
            "description": "Extract podcast guest information"
        },
        
        "RESEARCH_PAPER": {
            "patterns": [
                r'([A-Za-z]+,\s*[A-Z]\.\s*[A-Za-z]+)\s*\((\d{4})\)\.\s*(.+?)\.',  # Author (Year). Title.
                r'(.+?)\s*,\s*(\d+)\((\d+)\),\s*(\d+)-(\d+)\.',  # Journal, Volume(Issue), pages
                r'DOI:\s*(.+?)$',  # DOI: Identifier
                r'ISSN:\s*(.+?)$'  # ISSN: Identifier
            ],
            "example": "Smith, J. (2020). Title of Paper. Journal Name, 12(3), 45-67",
            "description": "Extract research paper information"
        },
        
        "CONFERENCE_PAPER": {
            "patterns": [
                r'Presented\s+at:\s*(.+?)\s*(\d{4})',  # Presented at: Conference Year
                r'Proceedings\s+of\s*(.+?)',  # Proceedings of: Conference
                r'Pages:\s*(\d+)-(\d+)',  # Pages: range
                r'Publisher:\s*(.+?)$'  # Publisher: Name
            ],
            "example": "Presented at: International Conference on AI 2023\nProceedings of: ICAI 2023",
            "description": "Extract conference paper information"
        },
        
        "JOURNAL_ARTICLE": {
            "patterns": [
                r'Published\s+in:\s*(.+?)',  # Published in: Journal
                r'Volume:\s*(\d+)',  # Volume: number
                r'Issue:\s*(\d+)',  # Issue: number
                r'Pages:\s*(\d+)-(\d+)',  # Pages: range
                r'Peer-reviewed\s*article'  # Peer-reviewed indicator
            ],
            "example": "Published in: IEEE Transactions on Software Engineering\nVolume: 45\nIssue: 3",
            "description": "Extract journal article information"
        },
        
        "BOOK_CHAPTER": {
            "patterns": [
                r'Chapter\s+(\d+):\s*(.+?)',  # Chapter X: Title
                r'In:\s*(.+?)\s*\((Ed\.?)\)',  # In: Book (Ed.)
                r'Publisher:\s*(.+?)',  # Publisher: Name
                r'Pages:\s*(\d+)-(\d+)'  # Pages: range
            ],
            "example": "Chapter 5: Advanced Security Techniques\nIn: Cybersecurity Handbook (Ed.)\nPublisher: Academic Press",
            "description": "Extract book chapter information"
        },
        
        "PATENT": {
            "patterns": [
                r'Patent\s*#?(\d+):',  # Patent #12345:
                r'Title:\s*(.+?)',  # Title: Patent title
                r'Filed:\s*(.+?)',  # Filed: Date
                r'Granted:\s*(.+?)',  # Granted: Date
                r'US\s*Patent\s*(\d+)'  # US Patent number
            ],
            "example": "Patent #12345: Title: Advanced Authentication System\nFiled: Jan 15, 2021\nGranted: Jun 20, 2023",
            "description": "Extract patent information"
        },
        
        "BLOG_ARTICLE": {
            "patterns": [
                r'Blog:\s*(.+?)',  # Blog: Platform
                r'Title:\s*(.+?)',  # Title: Article title
                r'Published:\s*(.+?)',  # Published: Date
                r'URL:\s*(.+?)$'  # URL: Link
            ],
            "example": "Blog: Medium\nTitle: Understanding Cloud Security\nPublished: March 15, 2023\nURL: medium.com/@author/article",
            "description": "Extract blog article information"
        },
        
        "ONLINE_ARTICLE": {
            "patterns": [
                r'Published\s+online:\s*(.+?)',  # Published online: Platform
                r'Website:\s*(.+?)',  # Website: Platform name
                r'Date:\s*(.+?)',  # Date: Publication date
                r'Views:\s*(\d+)',  # Views: Number
                r'URL:\s*(.+?)$'  # URL: Link
            ],
            "example": "Published online: TechCrunch\nDate: February 28, 2023\nViews: 15,000",
            "description": "Extract online article information"
        }
    }
    
    for format_name, format_info in formats.items():
        print(f"\n  FORMAT {format_name}:")
        print(f"    Patterns: {format_info['patterns']}")
        print(f"    Example: {format_info['example']}")
        print(f"    Description: {format_info['description']}")
    
    print("\n📋 PUBLICATION FIELDS TO EXTRACT:")
    fields = [
        "type: keynote, panelist, author, podcast, research_paper, conference_paper, journal_article, book_chapter, patent, blog_article, online_article",
        "title: Publication title",
        "authors: List of authors",
        "venue: Conference/journal name",
        "year: Publication year",
        "date: Full publication date",
        "pages: Page range",
        "volume: Volume number",
        "issue: Issue number",
        "publisher: Publisher name",
        "isbn: ISBN number",
        "issn: ISSN number",
        "doi: DOI identifier",
        "url: Online URL",
        "episode: Episode number (for podcasts)",
        "session: Session title (for keynotes)",
        "topic: Topic description",
        "patent_number: Patent number",
        "filed_date: Patent filing date",
        "granted_date: Patent grant date",
        "views: View count (for online articles)"
    ]
    
    for field in fields:
        print(f"  • {field}")
    
    print("\n📝 PUBLICATION CLEANING RULES:")
    cleaning_rules = [
        "Standardize author names (Last, First → First Last)",
        "Normalize publication types",
        "Extract year from various date formats",
        "Clean venue names (remove conference acronyms)",
        "Validate ISBN/ISSN/DOI formats",
        "Normalize URLs (ensure https://)",
        "Remove duplicate publications",
        "Clean page numbers and ranges",
        "Handle special characters in titles"
    ]
    
    for rule in cleaning_rules:
        print(f"  • {rule}")
    
    print("\n📋 PUBLICATION DETECTION STRATEGY:")
    detection_strategy = [
        "1. Look for PUBLICATIONS section header",
        "2. Identify publication entry boundaries",
        "3. Detect publication type from patterns",
        "4. Extract publication details using type-specific patterns",
        "5. Handle academic vs professional publications",
        "6. Extract URLs and validate them",
        "7. Clean and normalize all extracted data",
        "8. Validate minimum required fields (title, type)",
        "9. Sort publications by year (descending)"
    ]
    
    for strategy in detection_strategy:
        print(f"  {strategy}")
    
    print("\n🎯 IMPLEMENTATION LOCATION:")
    print("File: backend/app/services/parser/publications_parser.py")
    print("Function: parse_publications() [around line 50]")
    print("Add these patterns before existing publication detection logic")
    
    return formats

if __name__ == "__main__":
    extend_publications_parser()
