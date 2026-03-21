import os
import sys
import json
import logging
import asyncio
from pathlib import Path

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

# Set log level to DEBUG for more info
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

from app.services.parser.hybrid_parser_service import HybridParserService
from app.services.parser.extract_text import extract_text
from app.services.parser.section_parser import SectionParser
from app.core.config import get_settings

settings = get_settings()

def test_resume_sync(parser, filepath):
    logger.info(f"Testing resume: {filepath}")
    try:
        filename = os.path.basename(filepath)
        
        # 1. Extract text
        logger.debug(f"Starting text extraction for {filename}")
        extracted = extract_text(Path(filepath))
        logger.debug(f"Extraction complete. Text length: {len(extracted.text) if extracted.text else 0}")
        if not extracted.text:
            logger.error(f"Failed to extract text from {filename}")
            return False
            
        # 2. Segment into sections
        logger.debug("Starting section parsing")
        section_parser = SectionParser(use_spacy=True)
        sections_obj = section_parser.parse(extracted.text)
        logger.debug(f"Sections found: {list(sections_obj.keys())}")
        
        # 3. Convert SectionResult to Dict[str, str]
        section_dict = {k: v.content for k, v in sections_obj.items()}
        
        # 4. Parse with HybridParserService (sync)
        logger.debug("Starting hybrid parsing")
        result = parser.parse_resume(section_dict, layout_blocks=extracted.layout_blocks)
        logger.debug("Parsing complete")
        
        # 5. Check results
        jobs = result.get("work_experience", [])
        logger.info(f"SUCCESS: {filename} - Found {len(jobs)} jobs")
        for i, job in enumerate(jobs):
            # job is likely a JobEntry object or a dict
            if hasattr(job, "company"):
                logger.info(f"  Job {i+1}: {job.company} - {job.job_title} ({job.start_date} to {job.end_date})")
            else:
                logger.info(f"  Job {i+1}: {job.get('company')} - {job.get('job_title')} ({job.get('start_date')} to {job.get('end_date')})")
        
        # Check if JSON serializable
        from dataclasses import asdict, is_dataclass
        
        def sanitize(obj):
            if isinstance(obj, dict):
                return {k: sanitize(v) for k, v in obj.items()}
            if isinstance(obj, list):
                return [sanitize(v) for v in obj]
            if is_dataclass(obj):
                return asdict(obj)
            return obj
            
        sanitized = sanitize(result)
        json.dumps(sanitized)
        logger.debug("JSON serialization check passed")
        
        return True
    except Exception as e:
        logger.error(f"FAILED: {filepath} - {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    import argparse
    parser_arg = argparse.ArgumentParser()
    parser_arg.add_argument("--file", help="Specific file to test")
    parser_arg.add_argument("--all", action="store_true", help="Test all files in resumes directory")
    args = parser_arg.parse_args()

    parser = HybridParserService()
    resumes_dir = r"C:\Lalataksha V Company\Main-branch\Lakshya-LLM-Resume-Parser\resumes"
    
    if args.file:
        test_files = [args.file]
    elif args.all:
        test_files = [f for f in os.listdir(resumes_dir) if f.endswith(('.pdf', '.docx', '.doc'))]
    else:
        # Default set of representative files
        test_files = [
            "ALEX JOHNSON.pdf",
            "01_Arjun_Mehta_Full_Resume.docx",
            "Resume_NEW_01_Arjun_Mehta_TwoColumn.docx",
            "Aarav R. Kulkarni_resume_special_fonts_characters.docx",
            "ALEXANDER MORGAN AI_Engineer 5+.docx"
        ]
    
    results = []
    for filename in test_files:
        filepath = os.path.join(resumes_dir, filename)
        if os.path.exists(filepath):
            success = test_resume_sync(parser, filepath)
            results.append((filename, success))
        else:
            logger.warning(f"File not found: {filepath}")
            
    print("\n--- Test Results ---")
    pass_count = 0
    fail_count = 0
    for filename, success in results:
        status = "PASS" if success else "FAIL"
        print(f"{filename}: {status}")
        if success: pass_count += 1
        else: fail_count += 1
    
    print(f"\nSummary: {pass_count} Passed, {fail_count} Failed")

if __name__ == "__main__":
    asyncio.run(main())
