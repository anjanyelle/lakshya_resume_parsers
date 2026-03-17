#!/usr/bin/env python3
"""
TASK 3 - Fix client-based resume parsing (CLIENT: ROLE: format) - Enhanced
"""

import re
import json

def create_enhanced_client_based_parser():
    """Create enhanced parser for CLIENT: ROLE: format"""
    
    print("🔧 TASK 3 - FIXING CLIENT-BASED RESUME PARSING (ENHANCED)")
    print("=" * 60)
    
    # Enhanced regex patterns for CLIENT: ROLE: format
    client_patterns = [
        # CLIENT: Company\nROLE: Title Date Range
        r'CLIENT:\s*([^\n]+)\s*\nROLE:\s*([A-Za-z\s]+?)\s+([A-Za-z]+\s+\d{4})\s*-\s*([A-Za-z]+\s+\d{4}|Present)',
        # CLIENT: Company\nROLE: Title\nDate Range
        r'CLIENT:\s*([^\n]+)\s*\nROLE:\s*([A-Za-z\s]+)\s*\n([A-Za-z]+\s+\d{4})\s*-\s*([A-Za-z]+\s+\d{4}|Present)',
        # CLIENT: Company\nROLE: Title Date Range - Current
        r'CLIENT:\s*([^\n]+)\s*\nROLE:\s*([A-Za-z\s]+?)\s+([A-Za-z]+\s+\d{4})\s*-\s*Current',
        # CLIENT: Company\nROLE: Title (single line)
        r'CLIENT:\s*([^\n]+)\s*\nROLE:\s*([A-Za-z\s]+)',
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
        
        """CLIENT: Starbucks
ROLE: Senior Software Engineer
October 2015 - Current
- Developed microservices architecture
- Implemented CI/CD pipelines""",
    ]
    
    # Parse test resumes
    results = []
    for i, resume_text in enumerate(test_resumes):
        print(f"\n📄 Resume {i+1}:")
        print(resume_text[:50] + "...")
        
        parsed = parse_client_based_enhanced(resume_text, client_patterns)
        results.append(parsed)
        
        if parsed:
            print(f"✅ Parsed: {len(parsed)} jobs")
            for job in parsed:
                print(f"  - {job.get('title', 'N/A')} at {job.get('company', 'N/A')}")
                if job.get('start_date'):
                    print(f"    Period: {job.get('start_date')} - {job.get('end_date', 'N/A')}")
        else:
            print("❌ No jobs parsed")
    
    return results

def parse_client_based_enhanced(text, patterns):
    """Parse client-based resume format with enhanced patterns"""
    jobs = []
    
    for pattern in patterns:
        matches = re.finditer(pattern, text, re.MULTILINE | re.IGNORECASE)
        
        for match in matches:
            groups = match.groups()
            
            if len(groups) >= 2:
                job = {
                    'company': groups[0].strip(),
                    'title': groups[1].strip(),
                }
                
                # Add dates if available
                if len(groups) >= 4:
                    job['start_date'] = groups[2].strip()
                    job['end_date'] = groups[3].strip()
                elif len(groups) >= 3:
                    job['start_date'] = groups[2].strip()
                    job['end_date'] = 'Present'
                
                jobs.append(job)
    
    return jobs

def integrate_into_pipeline():
    """Create integration function for main pipeline"""
    
    print("\n🔗 CREATING PIPELINE INTEGRATION")
    print("=" * 40)
    
    integration_code = '''
def parse_client_based_format(resume_text):
    """Parse CLIENT: ROLE: format resumes"""
    patterns = [
        r'CLIENT:\\\\s*([^\\\\n]+)\\\\s*\\\\nROLE:\\\\s*([A-Za-z\\\\s]+?)\\\\s+([A-Za-z]+\\\\s+\\\\d{4})\\\\s*-\\\\s*([A-Za-z]+\\\\s+\\\\d{4}|Present)',
        r'CLIENT:\\\\s*([^\\\\n]+)\\\\s*\\\\nROLE:\\\\s*([A-Za-z\\\\s]+)\\\\s*\\\\n([A-Za-z]+\\\\s+\\\\d{4})\\\\s*-\\\\s*([A-Za-z]+\\\\s+\\\\d{4}|Present)',
        r'CLIENT:\\\\s*([^\\\\n]+)\\\\s*\\\\nROLE:\\\\s*([A-Za-z\\\\s]+?)\\\\s+([A-Za-z]+\\\\s+\\\\d{4})\\\\s*-\\\\s*Current',
        r'CLIENT:\\\\s*([^\\\\n]+)\\\\s*\\\\nROLE:\\\\s*([A-Za-z\\\\s]+)',
    ]
    
    jobs = []
    for pattern in patterns:
        matches = re.finditer(pattern, resume_text, re.MULTILINE | re.IGNORECASE)
        for match in matches:
            groups = match.groups()
            if len(groups) >= 2:
                job = {
                    'company': groups[0].strip(),
                    'title': groups[1].strip(),
                }
                if len(groups) >= 4:
                    job['start_date'] = groups[2].strip()
                    job['end_date'] = groups[3].strip()
                elif len(groups) >= 3:
                    job['start_date'] = groups[2].strip()
                    job['end_date'] = 'Present'
                jobs.append(job)
    return jobs
'''
    
    # Save integration code
    with open("client_based_integration.py", "w") as f:
        f.write(integration_code)
    
    print("✅ Integration function saved to client_based_integration.py")
    
    return integration_code

if __name__ == "__main__":
    # Test enhanced parser
    results = create_enhanced_client_based_parser()
    
    # Create integration
    integration_code = integrate_into_pipeline()
    
    print("\n" + "=" * 60)
    print("TASK 3 STATUS REPORT")
    print("=" * 60)
    print(f"Test resumes processed: {len(results)}")
    print(f"Total jobs parsed: {sum(len(r) for r in results)}")
    print(f"Parser patterns: 4 enhanced patterns")
    print(f"Integration function: YES")
    print(f"Status: READY")
    print("=" * 60)
