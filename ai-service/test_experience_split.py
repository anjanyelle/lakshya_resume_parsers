#!/usr/bin/env python3
"""
Test experience splitting to debug why only 1 job is extracted.
"""

import sys
sys.path.insert(0, '.')
import re

# Sample experience text from user's resume
experience_text = """
Client: State Farm                                                                                                                                      Location: Bloomington, IL
Role: SR. BIG DATA ENGINEER                                                                                                                October 2022 – Current
Responsibilities:
	•	Designed and implemented end-to-end ETL pipelines using Python, PySpark, and Apache Spark

Client: Delta Airlines                                                                                                                                      Location: Atlanta, GA
Role: SR DATA ENGINEER                                                                                                           December 2019 – September 2022
Responsibilities:
	•	Designed and implemented scalable ETL pipelines using Snowflake

Client: Nike                                                                                                                                                    Location: Beaverton, OR
Role: Senior Full Stack Developer                                                                                                                 January 2023 – Current
Responsibilities:
	•	Designed and developed middle-tier business logic using Java and Spring Boot

Client: BNY Mellon                                                                                                                                      Location: New York, NY
Role: Senior Full Stack Developer                                                                                                    March 2020 – December 2022
Responsibilities:
	•	Designed and developed middle-tier APIs using Java, Spring Boot
"""

print("Testing experience extraction...")
print("=" * 80)

# Import the extraction function
from parsers.experience_extractor import extract_experience

results = extract_experience(experience_text)

print(f"\n✅ Extracted {len(results)} experiences\n")

for i, exp in enumerate(results, 1):
    print(f"{i}. {exp.get('title', 'N/A')}")
    print(f"   Company: {exp.get('company', 'N/A')}")
    print(f"   Dates: {exp.get('start_date', 'N/A')} - {exp.get('end_date', 'Present' if exp.get('is_current') else 'N/A')}")
    print()

if len(results) < 4:
    print(f"❌ PROBLEM: Expected 4 jobs, got {len(results)}")
    print("\nDebugging: Let's check the CLIENT pattern matching...")
    
    CLIENT_RE = re.compile(r'(?i)^client\s*[:\-]\s*(.+)')
    lines = experience_text.split('\n')
    
    client_lines = []
    for i, line in enumerate(lines):
        if CLIENT_RE.match(line.strip()):
            client_lines.append((i, line.strip()))
    
    print(f"\nFound {len(client_lines)} 'Client:' lines:")
    for line_num, line in client_lines:
        print(f"  Line {line_num}: {line[:80]}")
else:
    print("✅ SUCCESS: All 4 jobs extracted correctly!")
