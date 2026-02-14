import time

import pytest

from app.services.llm_service import LLMParsingService, LLMResponse


def test_parse_json_handles_invalid_payload():
    service = LLMParsingService()
    result = service._parse_json("not-json", expect_array=True)
    assert result == []


def test_extract_work_experience_uses_llm(monkeypatch):
    service = LLMParsingService()

    def _fake_call(prompt: str, task: str) -> LLMResponse:
        return LLMResponse(
            content='[{"company_name":"Acme","job_title":"Engineer"}]'
        )

    monkeypatch.setattr(service, "_call_llm", _fake_call)
    results = service.extract_work_experience("Acme work")
    assert results[0]["company_name"] == "Acme"


def test_rate_limit_raises_when_exceeded():
    service = LLMParsingService()
    service.settings.LLM_RATE_LIMIT_PER_MINUTE = 1
    service._rate_timestamps = [time.time()]
    with pytest.raises(RuntimeError):
        service._enforce_rate_limit()
