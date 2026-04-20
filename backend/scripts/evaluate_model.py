"""
Resume Parser Evaluation Script
================================
Evaluates the work history parsing pipeline against all resumes.
Checks both the heuristic parser and (optionally) the DeBERTa NER model.

Usage:
  # Evaluate all resumes (heuristic parser only):
  python scripts/evaluate_model.py --resumes-dir ../resumes

  # Evaluate with DeBERTa NER model:
  python scripts/evaluate_model.py --resumes-dir ../resumes --model-dir models/deberta-ner/final

  # Output as JSON report:
  python scripts/evaluate_model.py --resumes-dir ../resumes --report report.json
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.services.parser.contact_extractor import ContactExtractor
from app.services.parser.extract_text import extract_text
from app.services.parser.normalize import normalize_resume_text
from app.services.parser.section_parser import SectionParser
from app.services.parser.skill_extractor import SkillExtractor
from app.services.parser.work_experience_parser import JobEntry, WorkExperienceParser


def _get_section_content(block) -> str:
    if block is None:
        return ""
    if isinstance(block, dict):
        return str(block.get("content", "") or "")
    return str(getattr(block, "content", "") or "")


def _job_to_dict(job: JobEntry) -> dict:
    return {
        "company": job.company,
        "title": job.title,
        "location": job.location,
        "start_date": job.start_date.isoformat() if job.start_date else None,
        "end_date": job.end_date.isoformat() if job.end_date else None,
        "is_current": job.is_current,
        "bullets_count": len(job.bullets or []),
        "confidence": job.confidence,
    }


def parse_resume(path: Path, model_dir: str | None = None) -> dict:
    """Parse a single resume and return structured results."""
    ext = path.suffix.lower().lstrip(".")
    try:
        extracted = extract_text(path)
        raw = extracted.text
    except Exception as e:
        return {"file": str(path), "error": f"extract_text failed: {e}"}

    source_fmt = ext if ext in ("pdf", "docx", "doc") else None
    text = normalize_resume_text(raw, source_format=source_fmt)

    section_parser = SectionParser(use_spacy=False)
    sections = section_parser.parse(text)

    contact_extractor = ContactExtractor()
    contact = contact_extractor.extract_all(text)

    exp_text = _get_section_content(sections.get("experience")) or text

    work_parser = WorkExperienceParser()
    t0 = time.perf_counter()
    jobs = work_parser.parse_experience_section(exp_text, source_format=source_fmt)
    parse_ms = (time.perf_counter() - t0) * 1000

    # Transformer NER enhancement (optional)
    ner_enhancements = []
    if model_dir:
        try:
            from app.services.parser.deberta_ner import TransformerNER
            ner = TransformerNER(model_dir)
            ner_enhancements = ner.extract_entities(exp_text)
        except Exception as e:
            ner_enhancements = [{"error": str(e)}]

    skill_extractor = SkillExtractor(use_spacy=False)
    skills = skill_extractor.extract_from_raw_text(text)
    skill_names = [m.normalized_name or m.name for m in skills]

    # Quality checks
    issues = []
    for job in jobs:
        comp = str(job.company or "").strip()
        title = str(job.title or "").strip()
        if comp.startswith("##"):
            issues.append(f"Company starts with ##: '{comp}'")
        if comp.lower() in ("duration", "period", "dates", "timeline", "experience"):
            issues.append(f"Company is a placeholder: '{comp}'")
        if title and "," in title and len(title) < 30:
            issues.append(f"Title looks like location: '{title}'")
        if comp and " - " in comp and len(comp) > 30:
            issues.append(f"Company may embed title: '{comp}'")
        if not job.start_date and not job.end_date and not job.is_current:
            issues.append(f"No dates for: '{comp}' / '{title}'")

    # Skill quality check
    bad_skills = [s for s in skill_names if " - " in s and len(s) > 8]

    return {
        "file": path.name,
        "format": ext,
        "name": contact.name.name if contact.name else None,
        "email": contact.emails[0].email if contact.emails else None,
        "sections": list(sections.keys()),
        "work_history": [_job_to_dict(j) for j in jobs],
        "work_history_count": len(jobs),
        "skills_count": len(skill_names),
        "bad_skills": bad_skills[:5],
        "parse_ms": round(parse_ms, 1),
        "issues": issues,
        "ner_enhancements": ner_enhancements[:3] if ner_enhancements else [],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate resume parser on all resumes.")
    parser.add_argument("--resumes-dir", default="../resumes", help="Directory with resume files")
    parser.add_argument("--model-dir", default=None, help="Path to fine-tuned DeBERTa model (optional)")
    parser.add_argument("--report", default=None, help="Save JSON report to this path")
    parser.add_argument("--limit", type=int, default=100)
    args = parser.parse_args()

    resumes_dir = Path(args.resumes_dir)
    if not resumes_dir.exists():
        print(f"[ERROR] Directory not found: {resumes_dir}")
        sys.exit(1)

    extensions = {".pdf", ".docx", ".doc"}
    resumes = [
        r for r in resumes_dir.rglob("*")
        if r.is_file() and r.suffix.lower() in extensions and not r.name.startswith("~$")
    ][: args.limit]

    print(f"\n[*] Evaluating {len(resumes)} resumes from {resumes_dir}")
    if args.model_dir:
        print(f"   DeBERTa model: {args.model_dir}")
    print()

    results: list[dict] = []
    total_jobs = 0
    total_issues = 0
    total_bad_skills = 0
    errors = 0

    for r in resumes:
        result = parse_resume(r, model_dir=args.model_dir)
        results.append(result)

        if "error" in result:
            print(f"  [ER] {r.name}: {result['error']}")
            errors += 1
            continue

        wh_count = result["work_history_count"]
        issues = result["issues"]
        bad = result["bad_skills"]
        total_jobs += wh_count
        total_issues += len(issues)
        total_bad_skills += len(bad)

        status = "[OK]" if wh_count > 0 and not issues else "[!!]" if wh_count > 0 else "[ER]"
        print(f"  {status} {r.name[:50]:<50}  jobs={wh_count}  issues={len(issues)}  {result['parse_ms']}ms")
        for issue in issues[:2]:
            print(f"       >> {issue}")

    print(f"\n{'='*65}")
    print(f"  Total resumes  : {len(resumes)}")
    print(f"  Errors         : {errors}")
    print(f"  Total jobs     : {total_jobs}")
    print(f"  Total issues   : {total_issues}")
    print(f"  Bad skills     : {total_bad_skills}")
    print(f"  Avg jobs/resume: {total_jobs / max(len(resumes) - errors, 1):.1f}")
    print(f"{'='*65}")

    if total_issues == 0:
        print("\n[OK] No parsing issues detected!")
    else:
        print(f"\n[!!] {total_issues} issues detected -- review above for details.")

    if args.report:
        report_path = Path(args.report)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump({
                "summary": {
                    "total_resumes": len(resumes),
                    "errors": errors,
                    "total_jobs": total_jobs,
                    "total_issues": total_issues,
                    "total_bad_skills": total_bad_skills,
                },
                "results": results,
            }, f, indent=2, default=str)
        print(f"\n[SAVED] Report saved to {args.report}")


if __name__ == "__main__":
    main()
