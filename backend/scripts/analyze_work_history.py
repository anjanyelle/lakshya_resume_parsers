
import os
import sys
import json
from pathlib import Path
import logging

# Add backend to sys.path
backend_path = Path(__file__).resolve().parents[1]
sys.path.append(str(backend_path))

from app.services.parser.extract_text import extract_text
from app.services.parser.section_parser import SectionParser
from app.services.parser.work_experience_parser import WorkExperienceParser
from app.services.parser.normalize import normalize_resume_text

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_analysis():
    resumes_dir = Path(r"C:\Lalataksha V Company\Main-branch\Lakshya-LLM-Resume-Parser\resumes")
    target_resumes = [
        "ARAVIND CHOWDARY KOLLI_.QA(8 pages).pdf",
        "Detailed Senior .NET CV.pdf",
        "Alistair Caldwell .NET Engineering Resume.pdf",
        "Senior Full Stack Developer Resume.pdf",
        "01_Marcus_Chen_DevOps_Engineer.docx",
        "Arjun_Mehta_Lead_Data_Engineer_8Pages_US_Style.docx"
    ]
    
    with open("analysis_results.txt", "w", encoding="utf-8") as f:
        for filename in target_resumes:
            file_path = resumes_dir / filename
            if file_path.exists():
                analyze_resume(file_path, f)
                f.flush()
            else:
                f.write(f"[!] File not found: {file_path}\n")
                f.flush()

def analyze_resume(file_path, out_file):
    out_file.write(f"\n{'='*80}\n")
    out_file.write(f"ANALYZING: {file_path.name}\n")
    out_file.write(f"{'='*80}\n")
    
    try:
        # 1. Extract Text
        ext = extract_text(file_path)
        text = ext.text
        
        # 2. Section Parsing
        section_parser = SectionParser()
        sections = section_parser.parse(text)
        
        exp_result = sections.get("experience")
        if not exp_result:
            out_file.write("[!] No experience section found.\n")
            return
            
        exp_text = exp_result.content
        out_file.write(f"Experience Section Length: {len(exp_text)} characters\n")
        
        # 3. Work Experience Parsing
        we_parser = WorkExperienceParser()
        jobs = we_parser.parse_experience_section(exp_text)
        
        out_file.write(f"Found {len(jobs)} jobs.\n")
        for i, job in enumerate(jobs):
            out_file.write(f"\n--- Job {i+1} ---\n")
            out_file.write(f"Company: {job.company}\n")
            out_file.write(f"Title:   {job.title}\n")
            out_file.write(f"Dates:   {job.start_date} to {job.end_date} (Current: {job.is_current})\n")
            out_file.write(f"Loc:     {job.location}\n")
            out_file.write(f"Conf:    {job.confidence:.2f}\n")
            
    except Exception as e:
        out_file.write(f"[ERROR] Failed to analyze {file_path.name}: {e}\n")
        import traceback
        out_file.write(traceback.format_exc())

if __name__ == "__main__":
    run_analysis()
