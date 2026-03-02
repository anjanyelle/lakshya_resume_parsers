
import os
import sys

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "backend")))

from app.services.parser.section_parser import SectionParser
from app.services.parser.extract_text import extract_text
from pathlib import Path

def debug_file(path_str):
    print(f"Debugging: {path_str}")
    path = Path(path_str)
    text_obj = extract_text(path)
    text = text_obj.text or ""
    print(f"Extracted length: {len(text)}")
    sp = SectionParser()
    sections = sp.parse(text)
    print(f"Sections found: {list(sections.keys())}")
    if 'experience' in sections:
        exp_text = sections['experience'].content
        from app.services.parser.work_experience_parser import WorkExperienceParser
        wp = WorkExperienceParser()
        print("--- Parsing Jobs ---")
        jobs = wp.parse_experience_section(exp_text)
        print(f"Jobs found: {len(jobs)}")
        for i, job in enumerate(jobs):
            print(f"Job {i+1}: {job.company} | {job.title} ({job.start_date} - {job.end_date})")
    else:
        print("WORK EXPERIENCE SECTION NOT FOUND")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        debug_file(sys.argv[1])
    else:
        debug_file(r"C:\Lalataksha V Company\Main-branch\Lakshya-LLM-Resume-Parser\backend\storage\ALEXANDER MORGAN AI_Engineer 5+.docx")
