"""
Usage (run from backend/ directory):

  poetry run python scripts/build_ground_truth.py \\
    --resumes-dir ./test_resumes \\
    --output ./tests/data/ground_truth.json \\
    --limit 50

  # Or use existing fixtures:
  poetry run python scripts/build_ground_truth.py \\
    --resumes-dir ./tests/fixtures/resumes \\
    --output ./tests/data/ground_truth.json \\
    --limit 50

Create test_resumes/ and add PDF/DOCX/TXT files, or use tests/fixtures/resumes.
Runs the parser on each resume and outputs side-by-side JSON for manual labeling.
Fill in the "expected" field by hand.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.services.parser.contact_extractor import ContactExtractor
from app.services.parser.extract_text import extract_text
from app.services.parser.normalize import normalize_resume_text
from app.services.parser.section_parser import SectionParser
from app.services.parser.skill_extractor import SkillExtractor
from app.services.parser.work_experience_parser import JobEntry, WorkExperienceParser


def _get_section_content(block) -> str:
    """Extract content from SectionResult or dict."""
    if block is None:
        return ""
    if isinstance(block, dict):
        return str(block.get("content", "") or "")
    return str(getattr(block, "content", "") or "")


def _job_to_dict(job: JobEntry) -> dict:
    """Convert JobEntry to JSON-serializable dict."""
    return {
        "company": job.company,
        "title": job.title,
        "start_date": job.start_date.isoformat() if job.start_date else None,
        "end_date": job.end_date.isoformat() if job.end_date else None,
        "description": job.description or "",
        "bullets": job.bullets or [],
    }


def parse_resume_file(path: str) -> dict:
    ext = Path(path).suffix.lower().lstrip(".")
    extracted = extract_text(Path(path))
    raw = extracted.text
    source_fmt = ext if ext in ("pdf", "docx", "doc") else ("ocr" if ext in ("png", "jpg", "jpeg") else None)
    text = normalize_resume_text(raw, source_format=source_fmt)

    section_parser = SectionParser(use_spacy=False)
    sections = section_parser.parse(text)

    contact_extractor = ContactExtractor()
    contact = contact_extractor.extract_all(text)

    exp_block = sections.get("experience")
    exp_text = _get_section_content(exp_block)
    if not exp_text:
        exp_text = text

    work_parser = WorkExperienceParser()
    jobs = work_parser.parse_experience_section(exp_text)

    skill_extractor = SkillExtractor(use_spacy=False)
    skills = skill_extractor.extract_from_raw_text(text)
    skill_names = [m.normalized_name or m.name for m in skills]

    name = contact.name.name if contact.name else None
    email = contact.emails[0].email if contact.emails else None
    phone = contact.phones[0].phone if contact.phones else None

    return {
        "file": path,
        "format": ext,
        "parsed": {
            "name": name or "",
            "email": email or "",
            "phone": phone or "",
            "work_experience": [_job_to_dict(j) for j in jobs],
            "skills": skill_names,
            "sections_detected": list(sections.keys()),
        },
        "expected": {
            "name": "",
            "email": "",
            "phone": "",
            "work_experience": [],
            "skills": [],
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build ground truth JSON from resumes for manual labeling."
    )
    parser.add_argument("--resumes-dir", required=True, help="Directory containing resume files")
    parser.add_argument(
        "--output",
        default="tests/data/ground_truth.json",
        help="Output JSON path (default: tests/data/ground_truth.json)",
    )
    parser.add_argument("--limit", type=int, default=50, help="Max number of resumes to process")
    args = parser.parse_args()

    resumes_dir = Path(args.resumes_dir)
    if not resumes_dir.exists():
        print(f"Error: Directory not found: {resumes_dir}")
        sys.exit(1)

    extensions = {".pdf", ".docx", ".doc", ".txt", ".png", ".jpg", ".jpeg"}
    resumes = [
        r
        for r in resumes_dir.rglob("*")
        if r.is_file()
        and r.suffix.lower() in extensions
        and not r.name.startswith("~$")  # Skip Word/Excel temp lock files
    ][: args.limit]

    results = []
    for r in resumes:
        try:
            result = parse_resume_file(str(r))
            results.append(result)
            print(f"OK  {r.name}")
        except Exception as e:
            print(f"ERR {r.name}: {e}")
            results.append({"file": str(r), "error": str(e)})

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, default=str, ensure_ascii=False)

    print(f"\nSaved {len(results)} entries to {output_path}")
    print("Next: open the JSON and fill in 'expected' fields manually.")
    print("Aim for 50 diverse resumes: 10 PDF, 10 DOCX, 5 DOC, 5 OCR/image, 10 TXT, 10 edge cases.")


if __name__ == "__main__":
    main()
