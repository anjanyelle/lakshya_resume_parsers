"""
Ground truth evaluation script. Runs the resume parser against fixtures with
expected.json/truth.json and reports accuracy metrics.

Usage (run from backend/ directory):

  poetry run python scripts/run_ground_truth_eval.py

  # Custom fixtures and output:
  poetry run python scripts/run_ground_truth_eval.py \\
    --fixtures-dir ./tests/fixtures/resumes \\
    --output ./tests/reports/accuracy_report.json

  # Fail if overall score drops below threshold:
  poetry run python scripts/run_ground_truth_eval.py --fail-below 0.5

Fixture structure: each case is a subdirectory with:
  - resume.pdf | resume.docx | resume.doc | original.*
  - expected.json | truth.json (ground truth)
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Ensure backend app is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.services.accuracy_report import generate_accuracy_report


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run ground truth evaluation against resume parser fixtures.",
    )
    parser.add_argument(
        "--fixtures-dir",
        type=Path,
        default=None,
        help="Directory with case subdirs (resume + expected.json/truth.json). "
        "Default: tests/fixtures/resumes",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=None,
        help="Write JSON report to this path (e.g. tests/reports/accuracy_report.json)",
    )
    parser.add_argument(
        "--fail-below",
        type=float,
        default=None,
        metavar="THRESHOLD",
        help="Exit with code 1 if overall score is below this value (0.0–1.0)",
    )
    parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Only print overall score and exit code",
    )
    args = parser.parse_args()

    backend_root = Path(__file__).resolve().parent.parent
    fixtures_dir = args.fixtures_dir or (backend_root / "tests" / "fixtures" / "resumes")
    output_path = args.output or (backend_root / "tests" / "reports" / "accuracy_report.json")

    if not fixtures_dir.exists():
        print(f"Error: fixtures directory not found: {fixtures_dir}", file=sys.stderr)
        return 1

    report = generate_accuracy_report(fixtures_dir=fixtures_dir, output_path=output_path)

    if report.case_count == 0:
        print("No evaluation cases found. Add subdirs with resume + expected.json/truth.json.", file=sys.stderr)
        return 1

    if args.quiet:
        print(f"overall={report.overall:.3f} cases={report.case_count}")
    else:
        print("=" * 60)
        print("Ground Truth Evaluation Report")
        print("=" * 60)
        print(f"Cases: {report.case_count}")
        print()
        print("Summary:")
        print(f"  section_found_rate:      {report.section_found_rate:.3f}")
        print(f"  section_bleed_rate:      {report.section_bleed_rate:.3f}")
        print(f"  contact_accuracy:        {report.contact_accuracy:.3f}")
        print(f"  work_accuracy:           {report.work_accuracy:.3f}")
        print(f"  work_company_f1:         {report.work_company_f1.f1:.3f}")
        print(f"  work_title_f1:           {report.work_title_f1.f1:.3f}")
        print(f"  work_dates_accuracy:     {report.work_dates_accuracy:.3f}")
        print(f"  work_date_extraction:    {report.work_date_extraction_rate:.3f}")
        print(f"  work_entry_count_diff:   {report.work_entry_count_diff:.3f}")
        print(f"  skills_f1:               {report.skills_f1.f1:.3f}")
        print(f"  education_f1:            {report.education_f1.f1:.3f}")
        print(f"  certifications_f1:       {report.certifications_f1.f1:.3f}")
        print()
        print(f"  overall:                 {report.overall:.3f}")
        print("=" * 60)
        print(f"Report written to: {output_path}")

    if args.fail_below is not None and report.overall < args.fail_below:
        if not args.quiet:
            print(f"\nOverall score {report.overall:.3f} below threshold {args.fail_below}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
