#!/usr/bin/env python3
"""
Test script to verify end-to-end logging is working correctly
"""

import sys
import os

# Add ai-service to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ai-service'))

from parsers.master_parser import MasterParser
from utils.logger import generate_request_id

def test_logging():
    """Test the logging functionality with a sample resume"""
    
    # Sample resume text with work experience
    resume_text = """
    WORK EXPERIENCE
    
    Full Stack Developer
    NextGen Software Pvt Ltd
    Mar 2023 - Present
    Developing scalable web applications using React.js, Node.js, and MongoDB.
    
    React Developer
    CodeCraft Technologies Pvt Ltd
    Jul 2021 - Feb 2023
    Worked on UI components, state management, and API integrations.
    
    EDUCATION
    
    B.Tech in Information Technology
    Osmania University
    2017 - 2021
    """
    
    print("=" * 80)
    print("TESTING END-TO-END LOGGING")
    print("=" * 80)
    
    # Generate request ID
    request_id = generate_request_id()
    print(f"\n📋 Request ID: {request_id}")
    print(f"📁 Log file: ai-service/logs/resume_parser.log\n")
    
    # Initialize parser
    print("🔧 Initializing MasterParser...")
    parser = MasterParser()
    
    # Parse the resume
    print("🚀 Starting parse...\n")
    result = parser.parse_text(
        text=resume_text,
        candidate_id="test_candidate_001",
        request_id=request_id
    )
    
    # Display results
    print("\n" + "=" * 80)
    print("PARSE RESULTS")
    print("=" * 80)
    
    print(f"\n✅ Status: {result.get('status', 'unknown')}")
    print(f"📊 Work Experience Count: {len(result.get('work_experience', []))}")
    print(f"🎓 Education Count: {len(result.get('education', []))}")
    print(f"💼 Companies: {result.get('companies', [])}")
    print(f"🎯 Job Titles: {result.get('job_titles', [])}")
    
    if result.get('work_experience'):
        print("\n📋 Work Experience Details:")
        for i, exp in enumerate(result.get('work_experience', []), 1):
            print(f"  {i}. {exp.get('title', 'N/A')} at {exp.get('company', 'N/A')}")
    
    if result.get('education'):
        print("\n🎓 Education Details:")
        for i, edu in enumerate(result.get('education', []), 1):
            print(f"  {i}. {edu.get('degree', 'N/A')} from {edu.get('institution', 'N/A')}")
    
    print("\n" + "=" * 80)
    print("LOG VERIFICATION")
    print("=" * 80)
    
    log_file = "ai-service/logs/resume_parser.log"
    if os.path.exists(log_file):
        print(f"\n✅ Log file created: {log_file}")
        
        # Read and display relevant log entries
        with open(log_file, 'r') as f:
            lines = f.readlines()
            
        # Filter logs for this request
        request_logs = [line for line in lines if request_id in line]
        
        print(f"📊 Total log entries for this request: {len(request_logs)}")
        
        # Show key log entries
        print("\n🔍 Key Log Entries:")
        for line in request_logs:
            if any(keyword in line for keyword in [
                'PARSE REQUEST STARTED',
                'SECTION EXTRACTION',
                'MODEL INFERENCE',
                'EXPERIENCE EXTRACTION',
                'PARSE REQUEST COMPLETED',
                'WARNING'
            ]):
                import json
                try:
                    log_entry = json.loads(line)
                    print(f"  • {log_entry.get('message', 'N/A')}")
                except:
                    pass
        
        print(f"\n💡 To view all logs for this request:")
        print(f"   grep '{request_id}' {log_file} | jq .")
        
    else:
        print(f"\n❌ Log file not found: {log_file}")
    
    print("\n" + "=" * 80)
    print("TEST COMPLETED")
    print("=" * 80)
    
    return result


def test_missing_work_experience():
    """Test logging when work experience is missing"""
    
    # Resume without work experience section
    resume_text = """
    John Doe
    john.doe@email.com
    
    EDUCATION
    
    B.Tech in Computer Science
    JNTU Hyderabad
    2017 - 2021
    
    SKILLS
    
    Python, JavaScript, React, Node.js
    """
    
    print("\n\n" + "=" * 80)
    print("TESTING MISSING WORK EXPERIENCE WARNING")
    print("=" * 80)
    
    request_id = generate_request_id()
    print(f"\n📋 Request ID: {request_id}\n")
    
    parser = MasterParser()
    result = parser.parse_text(
        text=resume_text,
        candidate_id="test_candidate_002",
        request_id=request_id
    )
    
    print(f"\n📊 Work Experience Count: {len(result.get('work_experience', []))}")
    
    # Check for warnings in logs
    log_file = "ai-service/logs/resume_parser.log"
    if os.path.exists(log_file):
        with open(log_file, 'r') as f:
            lines = f.readlines()
        
        warnings = [line for line in lines if request_id in line and 'WARNING' in line]
        
        if warnings:
            print(f"\n⚠️  Found {len(warnings)} warning(s):")
            for warning in warnings:
                import json
                try:
                    log_entry = json.loads(warning)
                    print(f"  • {log_entry.get('message', 'N/A')}")
                except:
                    pass
        else:
            print("\n✅ No warnings found (unexpected)")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    print("\n🧪 LOGGING SYSTEM TEST SUITE\n")
    
    # Test 1: Normal parsing with work experience
    test_logging()
    
    # Test 2: Missing work experience
    test_missing_work_experience()
    
    print("\n\n✅ All tests completed!")
    print("\n📖 See LOGGING_SETUP_GUIDE.md for detailed documentation")
