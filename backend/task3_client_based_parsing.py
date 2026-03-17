#!/usr/bin/env python3
"""
TASK 3 - Fix client-based resume parsing (CLIENT: ROLE: format)
"""

import re
import json

def create_client_based_parser():
    """Create parser for CLIENT: ROLE: format"""
    
    print("🔧 TASK 3 - FIXING CLIENT-BASED RESUME PARSING")
    print("=" * 50)
    
    # Define regex patterns for CLIENT: ROLE: format
    client_patterns = [
        # CLIENT: Company\nROLE: Title Date Range
        r'CLIENT:\s*(.+?)\s*\nROLE:\s*(.+?)\s+(.+?)\s+(.+?)\s*-\s*(.+)',
        # CLIENT: Company\nROLE: Title Date Range (multi-word dates)
        r'CLIENT:\s*(.+?)\s*\nROLE:\s*(.+?)\s+(.+?)\s+(.+?)\s*-\s*(.+?)\s+(.+)',
        # CLIENT: Company\nROLE: Title\nDate Range
        r'CLIENT:\s*(.+?)\s*\nROLE:\s*(.+?)\s*\n(.+?)\s*-\s*(.+)',
    ]
    
    # Test data
    test_resumes = [
        """CLIENT: Home Depot
ROLE: Senior Data Analyst June 2023 - Present
- Analyzed sales data using Python and SQL
- Created dashboards with Tableau""",
        
        """CLIENT: Huntington Bank
ROLE: Data Scientist January 2020 - December 2022
- Built ML models with TensorFlow
- Processed big data with Spark""",
        
        """CLIENT: Walgreens
ROLE: Business Analyst
March 2018 - May 2021
- Improved business processes
- Analyzed customer trends""",
    ]
    
    # Parse test resumes
    results = []
    for i, resume_text in enumerate(test_resumes):
        print(f"\n📄 Resume {i+1}:")
        print(resume_text[:50] + "...")
        
        parsed = parse_client_based(resume_text, client_patterns)
        results.append(parsed)
        
        if parsed:
            print(f"✅ Parsed: {len(parsed)} jobs")
            for job in parsed:
                print(f"  - {job.get('title', 'N/A')} at {job.get('company', 'N/A')}")
        else:
            print("❌ No jobs parsed")
    
    return results

def parse_client_based(text, patterns):
    """Parse client-based resume format"""
    jobs = []
    
    for pattern in patterns:
        matches = re.finditer(pattern, text, re.MULTILINE | re.IGNORECASE)
        
        for match in matches:
            groups = match.groups()
            
            if len(groups) >= 3:
                job = {
                    'company': groups[0].strip(),
                    'title': groups[1].strip(),
                    'start_date': groups[-2].strip(),
                    'end_date': groups[-1].strip(),
                }
                jobs.append(job)
    
    return jobs

if __name__ == "__main__":
    create_client_based_parser()
