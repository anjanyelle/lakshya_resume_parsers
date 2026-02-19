import json
from pathlib import Path

import pytest

from app.services.llm_service import LLMParsingService, LLMResponse
from app.services.parser.extract_text import extract_text


_FIXTURES_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "resumes"


def _case_dirs() -> list[Path]:
    if not _FIXTURES_DIR.exists():
        return []
    return sorted(
        [
            path
            for path in _FIXTURES_DIR.iterdir()
            if path.is_dir() and path.name.startswith("sample_")
        ]
    )


def test_resume_fixture_cases_present():
    assert _case_dirs(), f"No sample_* case directories found under {_FIXTURES_DIR}"


@pytest.mark.parametrize("case_dir", _case_dirs(), ids=lambda p: p.name)
def test_resume_fixture_case_has_required_files(case_dir: Path):
    originals = list(case_dir.glob("original.*"))
    assert len(originals) == 1, f"Expected exactly one original.* file in {case_dir}"
    assert (case_dir / "truth.json").exists(), f"Missing truth.json in {case_dir}"


@pytest.mark.parametrize("case_dir", _case_dirs(), ids=lambda p: p.name)
def test_resume_fixture_case_matches_truth(case_dir: Path, monkeypatch):
    original_path = next(case_dir.glob("original.*"))
    truth_path = case_dir / "truth.json"

    truth = json.loads(truth_path.read_text(encoding="utf-8"))

    required_keys = {"contact", "work_experience", "education", "skills", "certifications"}
    assert required_keys.issubset(set(truth.keys()))

    extracted = extract_text(original_path)
    assert extracted.text

    service = LLMParsingService()

    calls: dict[str, object] = {"count": 0, "prompt": "", "task": "", "tasks": []}

    def _fake_call(prompt: str, task: str) -> LLMResponse:
        calls["count"] = int(calls["count"]) + 1
        calls["prompt"] = prompt
        calls["task"] = task
        calls["tasks"].append(task)
        return LLMResponse(content=json.dumps(truth, ensure_ascii=False))

    monkeypatch.setattr(service, "_call_llm", _fake_call)

    result = service.extract_structured_resume(extracted.text)

    assert calls["count"] >= 1
    assert any(
        isinstance(t, str) and t.startswith("structured_resume")
        for t in (calls.get("tasks") or [])
    )
    assert isinstance(calls["prompt"], str)
    assert result == truth
