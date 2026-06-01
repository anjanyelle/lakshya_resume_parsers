"""
Candidate ranking service for the Resume Parser API.

This module provides ranking algorithms to sort and rank candidates
based on match scores, skills, experience, and other criteria.
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from enum import Enum

from sqlalchemy.orm import Session

from app.models.candidate import Candidate, CandidateStatus, ReviewStatus
from app.models.candidate_skill import CandidateSkill, ProficiencyLevel
from app.models.parsing_job import ParsingJob, ParsingJobStatus

logger = logging.getLogger(__name__)


class RankingCriteria(Enum):
    """Criteria for ranking candidates."""
    MATCH_SCORE = "match_score"
    SKILLS_MATCH = "skills_match"
    EXPERIENCE = "experience"
    CONFIDENCE = "confidence"
    RECENCY = "recency"
    REVIEW_STATUS = "review_status"


class RankingService:
    """
    Service for ranking and sorting candidates based on various criteria.
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def rank_candidates(
        self,
        job_id: Optional[str] = None,
        criteria: RankingCriteria = RankingCriteria.MATCH_SCORE,
        limit: int = 100,
        offset: int = 0,
        status_filter: Optional[CandidateStatus] = None
    ) -> List[Dict[str, Any]]:
        """
        Rank candidates based on specified criteria.
        
        Args:
            job_id: Job ID for job-specific matching (optional)
            criteria: Ranking criteria to use
            limit: Maximum number of candidates to return
            offset: Offset for pagination
            status_filter: Filter by candidate status (optional)
            
        Returns:
            List of ranked candidates with scores and metadata
        """
        # Build base query
        query = self.db.query(Candidate)
        
        # Apply status filter if specified
        if status_filter:
            query = query.filter(Candidate.status == status_filter)
        
        # Get candidates
        candidates = query.offset(offset).limit(limit).all()
        
        # Calculate ranking scores
        ranked_candidates = []
        for candidate in candidates:
            score_data = self._calculate_ranking_score(
                candidate, 
                criteria, 
                job_id
            )
            
            ranked_candidates.append({
                "candidate_id": str(candidate.id),
                "full_name": candidate.full_name,
                "email": candidate.email,
                "status": candidate.status.value,
                "review_status": candidate.review_status.value if candidate.review_status else None,
                "ranking_score": score_data["score"],
                "score_breakdown": score_data["breakdown"],
                "years_experience": candidate.years_experience,
                "skills_count": len(candidate.skills),
                "created_at": candidate.created_at.isoformat(),
                "updated_at": candidate.updated_at.isoformat(),
            })
        
        # Sort by ranking score (descending)
        ranked_candidates.sort(key=lambda x: x["ranking_score"], reverse=True)
        
        logger.info(
            f"Ranked {len(ranked_candidates)} candidates using criteria: {criteria.value}"
        )
        
        return ranked_candidates
    
    def _calculate_ranking_score(
        self,
        candidate: Candidate,
        criteria: RankingCriteria,
        job_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Calculate ranking score for a candidate.
        
        Args:
            candidate: Candidate object
            criteria: Ranking criteria to use
            job_id: Job ID for job-specific matching (optional)
            
        Returns:
            Dictionary with score and breakdown
        """
        breakdown = {}
        total_score = 0.0
        
        if criteria == RankingCriteria.MATCH_SCORE:
            # Use match score if available (from job matching)
            match_score = self._get_match_score(candidate.id, job_id)
            breakdown["match_score"] = match_score
            total_score = match_score
            
        elif criteria == RankingCriteria.SKILLS_MATCH:
            # Score based on skills count and proficiency
            skills_score = self._calculate_skills_score(candidate)
            breakdown["skills_score"] = skills_score
            total_score = skills_score
            
        elif criteria == RankingCriteria.EXPERIENCE:
            # Score based on years of experience
            experience_score = self._calculate_experience_score(candidate)
            breakdown["experience_score"] = experience_score
            total_score = experience_score
            
        elif criteria == RankingCriteria.CONFIDENCE:
            # Score based on parsing confidence
            confidence_score = self._calculate_confidence_score(candidate)
            breakdown["confidence_score"] = confidence_score
            total_score = confidence_score
            
        elif criteria == RankingCriteria.RECENCY:
            # Score based on recency (newer candidates score higher)
            recency_score = self._calculate_recency_score(candidate)
            breakdown["recency_score"] = recency_score
            total_score = recency_score
            
        elif criteria == RankingCriteria.REVIEW_STATUS:
            # Score based on review status
            review_score = self._calculate_review_status_score(candidate)
            breakdown["review_score"] = review_score
            total_score = review_score
        
        # Add bonus for completeness
        completeness_score = self._calculate_completeness_score(candidate)
        breakdown["completeness_bonus"] = completeness_score
        total_score += completeness_score * 0.1  # 10% bonus
        
        return {
            "score": round(total_score, 4),
            "breakdown": breakdown
        }
    
    def _get_match_score(
        self, 
        candidate_id: str, 
        job_id: Optional[str] = None
    ) -> float:
        """
        Get match score for candidate against a job.
        
        Args:
            candidate_id: Candidate ID
            job_id: Job ID (optional)
            
        Returns:
            Match score (0.0 to 1.0)
        """
        if not job_id:
            return 0.5  # Default score if no job specified
        
        # Try to get match score from matching results
        # This would typically come from a matching service
        # For now, return a default score
        try:
            from app.store.useJobStore import useJobStore
            job_store = useJobStore()
            match_results = job_store.match_results
            
            for match in match_results:
                if match.candidate_id == str(candidate_id) and match.job_id == job_id:
                    return match.overall_score / 100.0  # Convert to 0-1 range
        except Exception:
            pass
        
        return 0.5
    
    def _calculate_skills_score(self, candidate: Candidate) -> float:
        """
        Calculate score based on candidate's skills.
        
        Args:
            candidate: Candidate object
            
        Returns:
            Skills score (0.0 to 1.0)
        """
        if not candidate.skills:
            return 0.0
        
        # Base score from number of skills (normalized to 0-1)
        skills_count = len(candidate.skills)
        base_score = min(skills_count / 20.0, 1.0)  # Max score at 20 skills
        
        # Bonus for proficiency levels
        proficiency_bonus = 0.0
        for candidate_skill in candidate.candidate_skills:
            if candidate_skill.proficiency_level == ProficiencyLevel.EXPERT:
                proficiency_bonus += 0.05
            elif candidate_skill.proficiency_level == ProficiencyLevel.ADVANCED:
                proficiency_bonus += 0.03
            elif candidate_skill.proficiency_level == ProficiencyLevel.INTERMEDIATE:
                proficiency_bonus += 0.01
        
        proficiency_bonus = min(proficiency_bonus, 0.3)  # Max 30% bonus
        
        return round(base_score + proficiency_bonus, 4)
    
    def _calculate_experience_score(self, candidate: Candidate) -> float:
        """
        Calculate score based on years of experience.
        
        Args:
            candidate: Candidate object
            
        Returns:
            Experience score (0.0 to 1.0)
        """
        if candidate.years_experience is None:
            return 0.0
        
        # Normalize experience (0-30 years to 0-1 range)
        normalized_exp = min(candidate.years_experience / 30.0, 1.0)
        
        # Apply curve to give more weight to mid-range experience
        score = normalized_exp * (1 + 0.5 * (1 - abs(normalized_exp - 0.5)))
        
        return round(min(score, 1.0), 4)
    
    def _calculate_confidence_score(self, candidate: Candidate) -> float:
        """
        Calculate score based on parsing confidence.
        
        Args:
            candidate: Candidate object
            
        Returns:
            Confidence score (0.0 to 1.0)
        """
        # Get latest parsing job
        latest_job = self._get_latest_parsing_job(candidate.id)
        
        if not latest_job or latest_job.confidence_score is None:
            return 0.5  # Default score if no confidence data
        
        return round(latest_job.confidence_score, 4)
    
    def _calculate_recency_score(self, candidate: Candidate) -> float:
        """
        Calculate score based on recency (newer candidates score higher).
        
        Args:
            candidate: Candidate object
            
        Returns:
            Recency score (0.0 to 1.0)
        """
        days_since_creation = (datetime.utcnow() - candidate.created_at).days
        
        # Score decreases with age (newer = higher score)
        # Max score for candidates < 7 days old
        # Min score for candidates > 365 days old
        if days_since_creation < 7:
            return 1.0
        elif days_since_creation < 30:
            return 0.8
        elif days_since_creation < 90:
            return 0.6
        elif days_since_creation < 180:
            return 0.4
        elif days_since_creation < 365:
            return 0.2
        else:
            return 0.1
    
    def _calculate_review_status_score(self, candidate: Candidate) -> float:
        """
        Calculate score based on review status.
        
        Args:
            candidate: Candidate object
            
        Returns:
            Review status score (0.0 to 1.0)
        """
        if not candidate.review_status:
            return 0.5  # Default for unreviewed
        
        status_scores = {
            ReviewStatus.PENDING: 0.3,
            ReviewStatus.IN_PROGRESS: 0.5,
            ReviewStatus.APPROVED: 1.0,
            ReviewStatus.REJECTED: 0.0,
            ReviewStatus.NEEDS_REVIEW: 0.4,
        }
        
        return status_scores.get(candidate.review_status, 0.5)
    
    def _calculate_completeness_score(self, candidate: Candidate) -> float:
        """
        Calculate score based on profile completeness.
        
        Args:
            candidate: Candidate object
            
        Returns:
            Completeness score (0.0 to 1.0)
        """
        required_fields = [
            candidate.full_name,
            candidate.email,
            candidate.phone,
            candidate.location,
        ]
        
        optional_fields = [
            candidate.linkedin_url,
            candidate.github_url,
            candidate.summary,
            candidate.years_experience,
        ]
        
        # Required fields (40% weight)
        required_filled = sum(1 for field in required_fields if field)
        required_score = required_filled / len(required_fields) * 0.4
        
        # Optional fields (30% weight)
        optional_filled = sum(1 for field in optional_fields if field)
        optional_score = optional_filled / len(optional_fields) * 0.3
        
        # Work history (15% weight)
        work_history_score = 0.15 if candidate.work_history else 0.0
        
        # Education (15% weight)
        education_score = 0.15 if candidate.education else 0.0
        
        total_score = required_score + optional_score + work_history_score + education_score
        
        return round(total_score, 4)
    
    def _get_latest_parsing_job(self, candidate_id: str) -> Optional[ParsingJob]:
        """
        Get the latest parsing job for a candidate.
        
        Args:
            candidate_id: Candidate ID
            
        Returns:
            Latest parsing job or None
        """
        return self.db.query(ParsingJob).filter(
            ParsingJob.candidate_id == candidate_id
        ).order_by(ParsingJob.created_at.desc()).first()
    
    def get_top_candidates(
        self,
        job_id: Optional[str] = None,
        limit: int = 10,
        criteria: RankingCriteria = RankingCriteria.MATCH_SCORE
    ) -> List[Dict[str, Any]]:
        """
        Get top N candidates based on ranking criteria.
        
        Args:
            job_id: Job ID for job-specific matching (optional)
            limit: Number of top candidates to return
            criteria: Ranking criteria to use
            
        Returns:
            List of top candidates
        """
        return self.rank_candidates(
            job_id=job_id,
            criteria=criteria,
            limit=limit,
            offset=0
        )
    
    def get_ranking_summary(
        self,
        job_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get summary statistics for candidate rankings.
        
        Args:
            job_id: Job ID for job-specific matching (optional)
            
        Returns:
            Dictionary with ranking summary
        """
        candidates = self.db.query(Candidate).all()
        
        if not candidates:
            return {
                "total_candidates": 0,
                "average_score": 0.0,
                "score_distribution": {},
            }
        
        scores = []
        for candidate in candidates:
            score_data = self._calculate_ranking_score(
                candidate,
                RankingCriteria.MATCH_SCORE,
                job_id
            )
            scores.append(score_data["score"])
        
        avg_score = sum(scores) / len(scores) if scores else 0.0
        
        # Calculate distribution
        distribution = {
            "excellent": sum(1 for s in scores if s >= 0.8),
            "good": sum(1 for s in scores if 0.6 <= s < 0.8),
            "fair": sum(1 for s in scores if 0.4 <= s < 0.6),
            "poor": sum(1 for s in scores if s < 0.4),
        }
        
        return {
            "total_candidates": len(candidates),
            "average_score": round(avg_score, 4),
            "score_distribution": distribution,
            "top_score": round(max(scores), 4) if scores else 0.0,
            "bottom_score": round(min(scores), 4) if scores else 0.0,
        }
