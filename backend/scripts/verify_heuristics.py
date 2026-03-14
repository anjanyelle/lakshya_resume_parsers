import os
import json
import logging
from pathlib import Path
from app.services.parser.work_experience_parser import WorkExperienceParser
from app.services.parser.extract_text import extract_text
from app.services.parser.section_parser import SectionParser

# Setup logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

def verify_heuristics(resumes_dir: str, count: int = 10):
    resumes_path = Path(resumes_dir)
    
    # Initialize parser without HF NER for speed
    parser = WorkExperienceParser()
    parser.hf_ner_pipeline = None # Disable HF NER
    
    section_parser = SectionParser()
    
    resume_files = list(resumes_path.glob("*.pdf")) + list(resumes_path.glob("*.docx"))
    resume_files = resume_files[:count]
    
    print(f"--- Heuristic Verification on {len(resume_files)} resumes ---")
    
    for resume_file in resume_files:
        print(f"\nProcessing: {resume_file.name}")
        try:
            extracted = extract_text(resume_file)
            sections = section_parser.parse(extracted.text)
            
            exp_content = ""
            if "experience" in sections:
                exp_content = sections["experience"].content
            else:
                exp_content = extracted.text
            
            jobs = parser.parse_experience_section(exp_content)
            
            print(f"  Found {len(jobs)} jobs:")
            for j in jobs:
                print(f"    - [{j.start_date} to {j.end_date}] {j.title} at {j.company}")
                if j.location:
                    print(f"      Location: {j.location}")
                # Project Avoidance Check
                lowered = (str(j.company or "") + " " + str(j.title or "")).lower()
                if "project" in lowered or "case study" in lowered:
                    print(f"      [!] Potential Project Detected: {lowered}")
            
        except Exception as e:
            print(f"  Error: {e}")

if __name__ == "__main__":
    RESUMES_DIR = r"c:\Lalataksha V Company\Main-branch\Lakshya-LLM-Resume-Parser\resumes"
    verify_heuristics(RESUMES_DIR)
