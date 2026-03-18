import os
import sys
from pathlib import Path

# Add backend to path
sys.path.append(os.getcwd())

import logging
logging.basicConfig(level=logging.WARNING)

from app.services.parser.work_experience_parser import WorkExperienceParser
from app.services.parser.extract_text import extract_text
from app.services.parser.section_parser import SectionParser

def test_leakage():
    parser = WorkExperienceParser()
    sec_parser = SectionParser()
    
    resumes_dir = Path(r"C:\Lalataksha V Company\Main-branch\Lakshya-LLM-Resume-Parser\resumes")
    target_resumes = [
        "Anitha_Subramanian.docx",
        "Divya_Lakshmi_Parthasarathy.docx",
        "_Krishnamurthy_Sanjay.docx"
    ]
    
    for resume_name in target_resumes:
        resume_path = resumes_dir / resume_name
        if not resume_path.exists():
            print(f"File not found: {resume_path}")
            continue
            
        print(f"\n{'='*50}")
        print(f"Processing: {resume_name}")
        print(f"{'='*50}")
        
        extracted_text = extract_text(resume_path)
        sections = sec_parser.parse(extracted_text.text)
        
        # Get work experience content
        exp_section = sections.get('experience') or sections.get('work_experience')
        exp_text = exp_section.content if exp_section else ""
        
        print(f"\n--- Full Exp Text (first 500 chars) ---\n{repr(exp_text[:500])}")
            
        if not exp_text:
            print("No work experience section found.")
            continue
            
        print("\n--- Raw Chunks Found ---")
        chunks = parser.extract_individual_jobs(exp_text)
        for j, chunk in enumerate(chunks, 1):
            print(f"Chunk {j} first 100 chars: {repr(chunk[:100])}")
            
        jobs = parser.parse_experience_section(exp_text)
        
        print(f"Found {len(jobs)} jobs:")
        for i, job in enumerate(jobs, 1):
            print(f"\nJob {i}:")
            print(f"  Company: {job.company}")
            print(f"  Title: {job.title}")
            print(f"  Location: {job.location}")
            print(f"  Dates: {job.start_date} -> {job.end_date} (Current: {job.is_current})")

if __name__ == "__main__":
    test_leakage()
