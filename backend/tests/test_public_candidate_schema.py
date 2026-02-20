from __future__ import annotations

from datetime import datetime

from app.schemas.public import ParsingJobPublic


def test_parsing_job_public_does_not_expose_raw_text_or_parsed_data():
    job = {
        "id": "00000000-0000-0000-0000-000000000000",
        "candidate_id": "00000000-0000-0000-0000-000000000001",
        "filename": "resume.pdf",
        "file_path": "s3://bucket/resume.pdf",
        "original_file_copy_path": None,
        "extracted_text_path": None,
        "parsed_json_path": None,
        "status": "success",
        "task_id": None,
        "last_stage": None,
        "confidence_score": 0.7,
        "ocr_confidence": None,
        "error_message": None,
        "started_at": datetime.utcnow().isoformat(),
        "completed_at": None,
        # These should be ignored / not representable
        "raw_text": "SECRET",
        "parsed_data": {"secret": True},
    }

    parsed = ParsingJobPublic.model_validate(job)
    dumped = parsed.model_dump()
    assert "raw_text" not in dumped
    assert "parsed_data" not in dumped
