#!/usr/bin/env python3
"""
Test DeBERTa NER model directly on resume text files.
This bypasses the full API and tests only the model extraction.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from parsers.deberta_ner_parser import DeBERTaNerParser
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s:%(name)s:%(message)s'
)

logger = logging.getLogger(__name__)


def test_resume_file(file_path: str):
    """Test DeBERTa model on a single resume file."""
    print("=" * 80)
    print(f"📄 Testing: {file_path}")
    print("=" * 80)
    
    # Read resume text
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            resume_text = f.read()
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return
    
    print(f"\n📝 Resume text ({len(resume_text)} chars):")
    print("-" * 80)
    print(resume_text[:500])  # First 500 chars
    if len(resume_text) > 500:
        print("... (truncated)")
    print("-" * 80)
    
    # Initialize DeBERTa parser
    print("\n🤖 Initializing DeBERTa NER parser...")
    parser = DeBERTaNerParser()
    
    # Parse the resume with DeBERTa
    print("\n🔍 Parsing resume with DeBERTa model...")
    result = parser.parse_text(resume_text)
    
    # Display results
    print("\n" + "=" * 80)
    print("📊 EXTRACTION RESULTS")
    print("=" * 80)
    
    # Companies
    companies = result.get('companies', [])
    print(f"\n🏢 Companies ({len(companies)}):")
    for i, company in enumerate(companies, 1):
        print(f"  {i}. {company}")
    
    # Job Titles
    job_titles = result.get('job_titles', [])
    print(f"\n💼 Job Titles ({len(job_titles)}):")
    for i, title in enumerate(job_titles, 1):
        print(f"  {i}. {title}")
    
    # Locations
    locations = result.get('locations', [])
    print(f"\n📍 Locations ({len(locations)}):")
    for i, loc in enumerate(locations, 1):
        print(f"  {i}. {loc}")
    
    # Dates
    dates = result.get('dates', [])
    print(f"\n📅 Dates ({len(dates)}):")
    for i, date in enumerate(dates, 1):
        print(f"  {i}. {date}")
    
    # Work Experience
    work_exp = result.get('work_experience', [])
    print(f"\n💼 Work Experience ({len(work_exp)} entries):")
    for i, exp in enumerate(work_exp, 1):
        print(f"\n  {i}. {exp.get('role', 'N/A')} at {exp.get('company', 'N/A')}")
        if exp.get('start_date') or exp.get('end_date'):
            print(f"     {exp.get('start_date', 'N/A')} - {exp.get('end_date', 'N/A')}")
        if exp.get('location'):
            print(f"     Location: {exp.get('location')}")
    
    # Education
    education = result.get('education', [])
    print(f"\n🎓 Education ({len(education)} entries):")
    for i, edu in enumerate(education, 1):
        print(f"\n  {i}. {edu.get('degree', 'N/A')}")
        if edu.get('institution'):
            print(f"     Institution: {edu.get('institution')}")
        if edu.get('field_of_study'):
            print(f"     Field: {edu.get('field_of_study')}")
        if edu.get('start_year') or edu.get('end_year'):
            print(f"     {edu.get('start_year', 'N/A')} - {edu.get('end_year', 'N/A')}")
    
    # Degrees
    degrees = result.get('degrees', [])
    print(f"\n📚 Degrees ({len(degrees)}):")
    for i, degree in enumerate(degrees, 1):
        print(f"  {i}. {degree}")
    
    # Institutions
    institutions = result.get('institutions', [])
    print(f"\n🏫 Institutions ({len(institutions)}):")
    for i, inst in enumerate(institutions, 1):
        print(f"  {i}. {inst}")
    
    # Summary
    print("\n" + "=" * 80)
    print("📈 SUMMARY")
    print("=" * 80)
    print(f"✅ Companies: {len(companies)}")
    print(f"✅ Job Titles: {len(job_titles)}")
    print(f"✅ Work Experience: {len(work_exp)}")
    print(f"✅ Education: {len(education)}")
    print(f"✅ Degrees: {len(degrees)}")
    print(f"✅ Institutions: {len(institutions)}")
    print("=" * 80)
    print()


def main():
    """Test all resume files."""
    # Get base directory
    base_dir = Path(__file__).parent.parent
    
    # Resume files to test
    resume_files = [
        base_dir / "resume1.txt",
        base_dir / "resume2.txt",
        base_dir / "resume3.txt"
    ]
    
    print("\n🚀 DeBERTa NER Model Testing")
    print("Testing resume files with DeBERTa model only (no API)")
    print()
    
    # Test each resume
    for resume_file in resume_files:
        if resume_file.exists():
            test_resume_file(str(resume_file))
        else:
            print(f"⚠️  File not found: {resume_file}")
            print()
    
    print("\n✅ Testing complete!")


if __name__ == "__main__":
    main()
