import sys
import os
import logging
import json

# Add current directory to path
sys.path.insert(0, os.getcwd())

from parsers.deberta_ner_parser import DeBERTaNerParser

# Configure logging
logging.basicConfig(level=logging.INFO)

def test_connection():
    parser = DeBERTaNerParser()
    if not parser.is_loaded:
        print("Model not loaded, cannot test connection accurately.")
        return

    sample_text = """
WORK EXPERIENCE
Software Engineer
Google
Jan 2020 - Present
Working on Search engine.

Data Analyst
Amazon
Jun 2018 - Dec 2019
Analyzing user data.

EDUCATION
Bachelor of Technology in Computer Science
IIT Bombay
2014 - 2018

Master of Science
Stanford University
2020 - 2022
"""

    print("\nParsing sample text...")
    result = parser.parse_text(sample_text)
    
    print("\n--- WORK EXPERIENCE ---")
    for i, exp in enumerate(result.get('work_experience', []), 1):
        print(f"Exp {i}: {exp}")
        
    print("\n--- EDUCATION ---")
    for i, edu in enumerate(result.get('education', []), 1):
        print(f"Edu {i}: {edu}")

if __name__ == "__main__":
    test_connection()
