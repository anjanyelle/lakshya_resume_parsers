import sys
import os
import re
from pathlib import Path

# Add backend and parent directories to path
current_dir = Path(__file__).resolve().parent
sys.path.append(str(current_dir.parent))
sys.path.append(str(current_dir.parent / "backend"))

from app.services.parser.work_experience_parser import WorkExperienceParser
from app.services.parser.section_parser import SectionParser
from app.services.parser.extract_text import extract_text

LOG_FILE = Path("C:/tmp/diag_results.txt")

def log(msg):
    print(msg)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(msg + "\n")

def diagnose_segmentation(content):
    log("\n=== SEGMENTATION DIAGNOSIS ===")
    parser = SectionParser()
    scored_sections = parser.parse(content)
    
    for section_name, section_result in scored_sections.items():
        if section_result and section_result.content:
            text = section_result.content
            lines = text.splitlines()
            log(f"Section: {section_name.upper().ljust(15)} | Lines: {str(section_result.start_line).rjust(3)}-{str(section_result.end_line).ljust(3)} | Content: {len(lines)} lines")

def diagnose_dates():
    log("\n=== DATE EXTRACTION DIAGNOSIS ===")
    parser = WorkExperienceParser()
    samples = [
        "Aug 2023 - Present", 
        "2020–2023", 
        "Mar 2016 - Dec 2019", 
        "2018", 
        "July 2013 - Feb 2016",
        "05/2021 to 08/2023",
        "Jan' 22 - Currently",
        "Dec 2020 - Ongoing",
        "Present - 2024",
        "2022-2023",
        "May 2021",
        "2019 - present"
    ]
    for s in samples:
        try:
            start, end, current = parser._parse_dates(s)
            log(f"Input: {s.ljust(25)} | Start: {str(start).ljust(12)} | End: {str(end).ljust(12)} | Current: {current}")
        except Exception as e:
            log(f"Input: {s.ljust(25)} | FAILED: {e}")

def diagnose_grouping(content):
    log("\n=== GROUPING DIAGNOSIS ===")
    parser = WorkExperienceParser()
    section_parser = SectionParser()
    scored_sections = section_parser.parse(content)
    
    exp_text = ""
    for key in ["experience", "work_experience", "employment"]:
        if key in scored_sections and scored_sections[key].content:
            exp_text = scored_sections[key].content
            log(f"Using {key} section for grouping test.")
            break
            
    if not exp_text:
        log("No experience section detected!")
        return

    lines = [ln.strip() for ln in exp_text.splitlines() if ln.strip()]
    job_blocks = parser._group_lines_to_jobs(lines)
    
    log(f"Detected {len(job_blocks)} job blocks.")
    for i, block in enumerate(job_blocks):
        log(f"\n--- Block {i+1} ---")
        # Handle list of tuples (idx, text)
        block_lines = [item[1] if isinstance(item, tuple) else item for item in block]
        preview = "\n".join(block_lines[:3])
        log(preview + ("\n..." if len(block_lines) > 3 else ""))

if __name__ == "__main__":
    if LOG_FILE.exists():
        try:
            LOG_FILE.unlink()
        except:
            pass
    
    resume_path_str = sys.argv[1] if len(sys.argv) > 1 else None
    
    diagnose_dates()
    
    if resume_path_str:
        resume_path = Path(resume_path_str)
        log(f"\nProcessing: {resume_path}")
        try:
            extracted = extract_text(resume_path)
            content = extracted.text
            diagnose_segmentation(content)
            diagnose_grouping(content)
        except Exception as e:
            log(f"Error processing resume: {e}")
            import traceback
            traceback.print_exc()
    else:
        log("\nPass a resume path to test segmentation and grouping.")
