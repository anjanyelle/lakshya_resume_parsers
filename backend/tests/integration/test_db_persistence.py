import pytest

from app.models import Candidate
from app.models.candidate import CandidateStatus


@pytest.mark.integration
def test_db_persistence(db_session, cleanup_db):
    candidate = Candidate(
        full_name="DB Test",
        status=CandidateStatus.PENDING,
        tenant_id="default",
    )
    db_session.add(candidate)
    db_session.commit()
    db_session.refresh(candidate)

    loaded = db_session.get(Candidate, candidate.id)
    assert loaded is not None
    assert loaded.full_name == "DB Test"
