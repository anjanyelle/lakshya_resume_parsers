import os
import json
import logging
from pathlib import Path
from tqdm import tqdm
import pandas as pd
from app.services.parser.work_experience_parser import WorkExperienceParser
from app.services.parser.extract_text import extract_text
from app.services.parser.section_parser import SectionParser

# Setup logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

def test_batch_resumes(resumes_dir: str, output_file: str):
    resumes_path = Path(resumes_dir)
    parser = WorkExperienceParser()
    section_parser = SectionParser()
    
    results = []
    
    resume_files = list(resumes_path.glob("*.pdf")) + list(resumes_path.glob("*.docx"))
    # resume_files = resume_files[:20]  # Limit for faster testing
    print(f"Found {len(resume_files)} resumes to test. Processing...")
    
    for resume_file in tqdm(resume_files):
        try:
            extracted = extract_text(resume_file)
            sections = section_parser.parse(extracted.text)
            
            exp_content = ""
            if "experience" in sections:
                exp_content = sections["experience"].content
            else:
                exp_content = extracted.text # Fallback to full text if section not found
            
            jobs = parser.parse_experience_section(exp_content)
            
            results.append({
                "filename": resume_file.name,
                "job_count": len(jobs),
                "companies": [j.company for j in jobs],
                "titles": [j.title for j in jobs],
                "error": None
            })
        except Exception as e:
            results.append({
                "filename": resume_file.name,
                "job_count": 0,
                "companies": [],
                "titles": [],
                "error": str(e)
            })
            
    # Save results
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    
    print(f"Batch test completed. Results saved to {output_file}")
    
    # Print summary
    df = pd.DataFrame(results)
    print("\n--- Summary ---")
    print(f"Total processed: {len(df)}")
    print(f"Total jobs found: {df['job_count'].sum()}")
    print(f"Average jobs per resume: {df['job_count'].mean():.2f}")
    print(f"Resumes with 0 jobs: {len(df[df['job_count'] == 0])}")
    print(f"Resumes with errors: {df['error'].notnull().sum()}")

if __name__ == "__main__":
    RESUMES_DIR = r"c:\Lalataksha V Company\Main-branch\Lakshya-LLM-Resume-Parser\resumes"
    OUTPUT_FILE = "batch_test_results_v4.json"
    test_batch_resumes(RESUMES_DIR, OUTPUT_FILE)
