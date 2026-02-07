from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.candidate import Candidate
from app.schemas.candidate import CandidateCreate, CandidateUpdate


class CRUDCandidate(CRUDBase[Candidate, CandidateCreate, CandidateUpdate]):
    def get_by_email(self, db: Session, email: str) -> Candidate | None:
        return db.query(Candidate).filter(Candidate.email == email).first()


candidate = CRUDCandidate(Candidate)
