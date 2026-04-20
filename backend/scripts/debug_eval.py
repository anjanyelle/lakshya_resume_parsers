import sys
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.services.parser.extract_text import extract_text
from app.services.parser.work_experience_parser import WorkExperienceParser
from app.services.parser.normalize import normalize_resume_text

def debug_parse():
    resumes_dir = Path("../resumes")
    extensions = {".pdf", ".docx", ".doc"}
    resumes = sorted([
        r for r in resumes_dir.rglob("*")
        if r.is_file() and r.suffix.lower() in extensions and not r.name.startswith("~$")
    ])
    
    print(f"[*] Found {len(resumes)} resumes.")
    
    work_parser = WorkExperienceParser()
    
    for i, r in enumerate(resumes):
        print(f"  [{i+1}/{len(resumes)}] Processing {r.name}...", end="", flush=True)
        t0 = time.perf_counter()
        try:
            # Extraction
            ext_t0 = time.perf_counter()
            extracted = extract_text(r)
            # Normalization
            norm_text = normalize_resume_text(extracted.text)
            # Parsing
            parse_t0 = time.perf_counter()
            jobs = work_parser.parse_experience_section(norm_text)
            
            elapsed = time.perf_counter() - t0
            print(f" [OK] {len(jobs)} jobs ({elapsed:.2f}s)")
        except Exception as e:
            print(f" [ERR] {e}")

if __name__ == "__main__":
    debug_parse()
