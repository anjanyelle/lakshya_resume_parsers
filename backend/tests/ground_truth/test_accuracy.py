from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.services.parser.contact_extractor import ContactExtractor
from app.services.parser.skill_extractor import SkillExtractor


def _metrics(tp: int, fp: int, fn: int) -> dict[str, float]:
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if precision + recall else 0.0
    return {"precision": precision, "recall": recall, "f1": f1}


@pytest.mark.ground_truth
def test_ground_truth_accuracy():
    data_path = Path(__file__).resolve().parent / "resumes.json"
    baseline_path = Path(__file__).resolve().parent / "baseline.json"
    data = json.loads(data_path.read_text(encoding="utf-8"))
    baseline = json.loads(baseline_path.read_text(encoding="utf-8"))

    extractor = ContactExtractor(default_region="US")
    taxonomy_path = (
        Path(__file__).resolve().parents[2]
        / "app"
        / "data"
        / "taxonomy"
        / "skills_seed.json"
    )
    skill_extractor = SkillExtractor(taxonomy_path=str(taxonomy_path), use_spacy=False)

    totals = {"email": {"tp": 0, "fp": 0, "fn": 0}, "phone": {"tp": 0, "fp": 0, "fn": 0},
              "name": {"tp": 0, "fp": 0, "fn": 0}, "skills": {"tp": 0, "fp": 0, "fn": 0}}

    for entry in data:
        text = entry["text"]
        expected = entry["expected"]

        emails = extractor.extract_emails(text)
        phones = extractor.extract_phones(text)
        name = extractor.extract_name(text).name
        skills = skill_extractor.extract_from_skills_section(text)

        extracted_email = emails[0].email if emails else None
        extracted_phone = phones[0].phone if phones else None
        extracted_name = name
        extracted_skills = {s.normalized_name for s in skills}

        exp_email = expected.get("email")
        exp_phone = expected.get("phone")
        exp_name = expected.get("name")
        exp_skills = set(expected.get("skills", []))

        totals["email"]["tp"] += int(extracted_email == exp_email)
        totals["email"]["fp"] += int(extracted_email not in {None, exp_email})
        totals["email"]["fn"] += int(extracted_email is None)

        totals["phone"]["tp"] += int(extracted_phone == exp_phone)
        totals["phone"]["fp"] += int(extracted_phone not in {None, exp_phone})
        totals["phone"]["fn"] += int(extracted_phone is None)

        totals["name"]["tp"] += int(extracted_name == exp_name)
        totals["name"]["fp"] += int(extracted_name not in {None, exp_name})
        totals["name"]["fn"] += int(extracted_name is None)

        totals["skills"]["tp"] += len(extracted_skills & exp_skills)
        totals["skills"]["fp"] += len(extracted_skills - exp_skills)
        totals["skills"]["fn"] += len(exp_skills - extracted_skills)

    report = {key: _metrics(**values) for key, values in totals.items()}

    for key, metrics in report.items():
        assert metrics["f1"] >= baseline[key]["f1"], f"{key} F1 regression detected"

    report_path = Path("tests/reports/accuracy_report.json")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
