import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.parser.education_parser import EducationParser
import logging

logging.basicConfig(level=logging.DEBUG)

def test_edu():
    parser = EducationParser()
    # Sample text that might be failing
    text = """
    Bachelor of Technology in Computer Science
    Georgia Institute of Technology, Atlanta, GA
    2018 - 2022 | GPA: 3.8/4.0
    
    Master of Science in AI
    Stanford University
    2022 - 2024
    """
    
    print("Parsing text...")
    entries = parser.parse(text)
    print(f"Found {len(entries)} entries")
    for i, e in enumerate(entries):
        print(f"Entry {i+1}: {e.institution}, {e.degree}, {e.end_date}")

if __name__ == "__main__":
    test_edu()
