from __future__ import annotations

import inspect

import app.workers.pipeline as pipeline


def test_detect_resume_sections_uses_excerpt_not_full_raw_text():
    src = inspect.getsource(pipeline.task_detect_resume_sections)
    assert "_llm_excerpt" in src
    assert "detect_resume_sections(excerpt" in src


def test_parse_work_experience_caps_llm_input():
    src = inspect.getsource(pipeline.task_parse_work_experience)
    assert "_cap_llm_text" in src
    assert "llm_source = _cap_llm_text" in src
