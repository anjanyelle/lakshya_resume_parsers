import json
import os
from pathlib import Path

import pytest

from app.core.config import get_settings
from app.services.llm_service import LLMParsingService
from app.services.parser.extract_text import extract_text
from tests.utils.accuracy_scoring import print_dataset_score, score_dataset


_FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures" / "resumes"


def _iter_cases(fixtures_dir: Path):
    for case_dir in sorted(fixtures_dir.iterdir()):
        if not case_dir.is_dir():
            continue
        if not case_dir.name.startswith("sample_"):
            continue
        originals = list(case_dir.glob("original.*"))
        if len(originals) != 1:
            continue
        truth_path = case_dir / "truth.json"
        if not truth_path.exists():
            continue
        yield case_dir, originals[0], truth_path


def _run_3_pass_llm(text: str) -> dict:
    settings = get_settings()
    if settings.LLM_PROVIDER == "none":
        raise RuntimeError("LLM_PROVIDER is 'none'; cannot run LLM evaluation")
    service = LLMParsingService()
    extracted = service.extract_structured_resume(text)
    normalized = service.normalize_structured_resume(extracted)
    verified = service.verify_structured_resume(text, normalized)
    return verified


def evaluate_fixtures(fixtures_dir: Path = _FIXTURES_DIR):
    pairs = []
    for _, original_path, truth_path in _iter_cases(fixtures_dir):
        truth_payload = json.loads(truth_path.read_text(encoding="utf-8"))

        extracted = extract_text(original_path)
        pred_payload = _run_3_pass_llm(extracted.text)

        pairs.append((truth_payload, pred_payload))

    score = score_dataset(pairs)
    print_dataset_score(score)
    return score


def main() -> None:
    evaluate_fixtures(_FIXTURES_DIR)


@pytest.mark.evaluation
def test_eval_llm_accuracy_runner():
    if os.getenv("RUN_LLM_EVAL") != "1":
        pytest.skip("Set RUN_LLM_EVAL=1 to run LLM evaluation")
    evaluate_fixtures(_FIXTURES_DIR)


if __name__ == "__main__":
    main()
