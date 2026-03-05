from pathlib import Path
import sys
import time
from datetime import datetime

# Add backend to path
_BACKEND = Path(__file__).resolve().parent / "backend"
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

log("Importing extract_text...")
start = time.time()
from app.services.parser.extract_text import extract_text
log(f"extract_text imported in {time.time() - start:.2f}s")

log("Importing SectionParser...")
start = time.time()
from app.services.parser.section_parser import SectionParser
log(f"SectionParser imported in {time.time() - start:.2f}s")

log("Importing WorkExperienceParser...")
start = time.time()
from app.services.parser.work_experience_parser import WorkExperienceParser
log(f"WorkExperienceParser imported in {time.time() - start:.2f}s")

resume_path = Path("resumes/AARAV RAGHUNATH IYER_AndroidDevloper.docx")
log(f"Processing: {resume_path}")

log("Extracting text...")
start = time.time()
extracted = extract_text(resume_path)
log(f"Extraction done in {time.time() - start:.2f}s")

log("Parsing sections...")
start = time.time()
section_parser = SectionParser(use_spacy=False)
sections = section_parser.parse(extracted.text)
log(f"Sections parsed in {time.time() - start:.2f}s")

exp_text = extracted.text
if "experience" in sections:
    exp_text = sections["experience"].content
    log(f"Using experience section ({len(exp_text)} chars)")

log("Parsing work experience...")
start = time.time()
work_parser = WorkExperienceParser()
jobs = work_parser.parse_experience_section(exp_text)
log(f"Work experience parsed in {time.time() - start:.2f}s")

log(f"Found {len(jobs)} jobs:")
for j in jobs:
    print(f"  - {j.company} | {j.title} | {j.start_date} to {j.end_date}")
