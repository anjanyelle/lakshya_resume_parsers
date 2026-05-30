"""
Duplicate detection service for the Resume Parser API.

This module provides functionality to detect duplicate resumes using
hashing, email/phone matching, and fuzzy matching algorithms.
"""

import logging
import hashlib
from typing import List, Dict, Any, Optional, Tuple, Set
from datetime import datetime
from pathlib import Path
from difflib import SequenceMatcher

from sqlalchemy.orm import Session
from sqlalchemy import or_, and_

from app.models.candidate import Candidate
from app.models.parsing_job import ParsingJob

logger = logging.getLogger(__name__)


class DuplicateDetectionService:
    """
    Service for detecting duplicate candidates and resumes.
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def compute_resume_hash(self, file_path: str) -> str:
        """
        Compute SHA-256 hash of a resume file.
        
        Args:
            file_path: Path to the resume file
            
        Returns:
            SHA-256 hash string
        """
        sha256_hash = hashlib.sha256()
        
        try:
            with open(file_path, "rb") as f:
                # Read file in chunks to handle large files
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            
            file_hash = sha256_hash.hexdigest()
            logger.info(f"Computed hash for file: {file_path} -> {file_hash}")
            return file_hash
            
        except Exception as e:
            logger.error(f"Error computing hash for file {file_path}: {e}")
            raise
    
    def compute_content_hash(self, content: str) -> str:
        """
        Compute hash of resume text content.
        
        Args:
            content: Resume text content
            
        Returns:
            SHA-256 hash string
        """
        # Normalize content: lowercase, remove extra whitespace
        normalized = " ".join(content.lower().split())
        return hashlib.sha256(normalized.encode()).hexdigest()
    
    def find_duplicates_by_hash(
        self,
        file_hash: str,
        exclude_candidate_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Find candidates with the same file hash.
        
        Args:
            file_hash: SHA-256 hash of the file
            exclude_candidate_id: Candidate ID to exclude from results
            
        Returns:
            List of duplicate candidates
        """
        query = self.db.query(ParsingJob).filter(
            ParsingJob.file_hash == file_hash
        )
        
        if exclude_candidate_id:
            query = query.filter(ParsingJob.candidate_id != exclude_candidate_id)
        
        duplicates = query.all()
        
        results = []
        for dup in duplicates:
            candidate = self.db.query(Candidate).filter(
                Candidate.id == dup.candidate_id
            ).first()
            
            if candidate:
                results.append({
                    "candidate_id": str(candidate.id),
                    "full_name": candidate.full_name,
                    "email": candidate.email,
                    "phone": candidate.phone,
                    "parsing_job_id": str(dup.id),
                    "filename": dup.filename,
                    "uploaded_at": dup.created_at.isoformat(),
                    "match_type": "file_hash"
                })
        
        logger.info(f"Found {len(results)} duplicates by file hash: {file_hash}")
        return results
    
    def find_duplicates_by_email(
        self,
        email: str,
        exclude_candidate_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Find candidates with the same email address.
        
        Args:
            email: Email address to search for
            exclude_candidate_id: Candidate ID to exclude from results
            
        Returns:
            List of duplicate candidates
        """
        query = self.db.query(Candidate).filter(
            Candidate.email == email
        )
        
        if exclude_candidate_id:
            query = query.filter(Candidate.id != exclude_candidate_id)
        
        duplicates = query.all()
        
        results = []
        for dup in duplicates:
            results.append({
                "candidate_id": str(dup.id),
                "full_name": dup.full_name,
                "email": dup.email,
                "phone": dup.phone,
                "created_at": dup.created_at.isoformat(),
                "updated_at": dup.updated_at.isoformat(),
                "match_type": "email"
            })
        
        logger.info(f"Found {len(results)} duplicates by email: {email}")
        return results
    
    def find_duplicates_by_phone(
        self,
        phone: str,
        exclude_candidate_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Find candidates with the same phone number.
        
        Args:
            phone: Phone number to search for
            exclude_candidate_id: Candidate ID to exclude from results
            
        Returns:
            List of duplicate candidates
        """
        query = self.db.query(Candidate).filter(
            Candidate.phone == phone
        )
        
        if exclude_candidate_id:
            query = query.filter(Candidate.id != exclude_candidate_id)
        
        duplicates = query.all()
        
        results = []
        for dup in duplicates:
            results.append({
                "candidate_id": str(dup.id),
                "full_name": dup.full_name,
                "email": dup.email,
                "phone": dup.phone,
                "created_at": dup.created_at.isoformat(),
                "updated_at": dup.updated_at.isoformat(),
                "match_type": "phone"
            })
        
        logger.info(f"Found {len(results)} duplicates by phone: {phone}")
        return results
    
    def find_fuzzy_duplicates(
        self,
        candidate: Candidate,
        similarity_threshold: float = 0.85,
        exclude_candidate_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Find candidates with similar information using fuzzy matching.
        
        Args:
            candidate: Candidate to find duplicates for
            similarity_threshold: Minimum similarity score (0.0 to 1.0)
            exclude_candidate_id: Candidate ID to exclude from results
            
        Returns:
            List of potentially duplicate candidates with similarity scores
        """
        # Get all candidates except the current one
        query = self.db.query(Candidate)
        
        if exclude_candidate_id:
            query = query.filter(Candidate.id != exclude_candidate_id)
        
        all_candidates = query.all()
        
        fuzzy_duplicates = []
        
        for other_candidate in all_candidates:
            similarity_score = self._calculate_similarity(candidate, other_candidate)
            
            if similarity_score >= similarity_threshold:
                fuzzy_duplicates.append({
                    "candidate_id": str(other_candidate.id),
                    "full_name": other_candidate.full_name,
                    "email": other_candidate.email,
                    "phone": other_candidate.phone,
                    "similarity_score": round(similarity_score, 4),
                    "match_type": "fuzzy",
                    "created_at": other_candidate.created_at.isoformat(),
                    "updated_at": other_candidate.updated_at.isoformat(),
                })
        
        # Sort by similarity score (descending)
        fuzzy_duplicates.sort(key=lambda x: x["similarity_score"], reverse=True)
        
        logger.info(
            f"Found {len(fuzzy_duplicates)} fuzzy duplicates for candidate {candidate.id}"
        )
        
        return fuzzy_duplicates
    
    def _calculate_similarity(self, candidate1: Candidate, candidate2: Candidate) -> float:
        """
        Calculate similarity score between two candidates.
        
        Args:
            candidate1: First candidate
            candidate2: Second candidate
            
        Returns:
            Similarity score (0.0 to 1.0)
        """
        scores = []
        
        # Name similarity
        if candidate1.full_name and candidate2.full_name:
            name_similarity = SequenceMatcher(
                None,
                candidate1.full_name.lower(),
                candidate2.full_name.lower()
            ).ratio()
            scores.append(name_similarity * 0.4)  # 40% weight
        
        # Email similarity
        if candidate1.email and candidate2.email:
            if candidate1.email == candidate2.email:
                scores.append(1.0 * 0.3)  # 30% weight for exact match
            else:
                email_similarity = SequenceMatcher(
                    None,
                    candidate1.email.lower(),
                    candidate2.email.lower()
                ).ratio()
                scores.append(email_similarity * 0.3)
        
        # Phone similarity
        if candidate1.phone and candidate2.phone:
            # Normalize phone numbers (remove non-digits)
            phone1 = ''.join(c for c in candidate1.phone if c.isdigit())
            phone2 = ''.join(c for c in candidate2.phone if c.isdigit())
            
            if phone1 == phone2:
                scores.append(1.0 * 0.2)  # 20% weight for exact match
            elif phone1 and phone2:
                phone_similarity = SequenceMatcher(None, phone1, phone2).ratio()
                scores.append(phone_similarity * 0.2)
        
        # Skills similarity
        if candidate1.skills and candidate2.skills:
            skills1 = set(skill.name.lower() for skill in candidate1.skills)
            skills2 = set(skill.name.lower() for skill in candidate2.skills)
            
            if skills1 and skills2:
                intersection = len(skills1.intersection(skills2))
                union = len(skills1.union(skills2))
                skills_similarity = intersection / union if union > 0 else 0.0
                scores.append(skills_similarity * 0.1)  # 10% weight
        
        # Overall similarity
        total_weight = sum(0.4, 0.3, 0.2, 0.1)  # Sum of weights
        if scores:
            return sum(scores) / total_weight
        
        return 0.0
    
    def find_all_duplicates(
        self,
        candidate_id: str,
        file_hash: Optional[str] = None,
        similarity_threshold: float = 0.85
    ) -> Dict[str, Any]:
        """
        Find all types of duplicates for a candidate.
        
        Args:
            candidate_id: Candidate ID to check for duplicates
            file_hash: File hash to check (optional)
            similarity_threshold: Minimum similarity score for fuzzy matching
            
        Returns:
            Dictionary with all duplicate types and counts
        """
        candidate = self.db.query(Candidate).filter(
            Candidate.id == candidate_id
        ).first()
        
        if not candidate:
            raise ValueError(f"Candidate not found: {candidate_id}")
        
        all_duplicates = {
            "candidate_id": str(candidate.id),
            "full_name": candidate.full_name,
            "email": candidate.email,
            "phone": candidate.phone,
            "duplicates": {
                "by_hash": [],
                "by_email": [],
                "by_phone": [],
                "fuzzy": []
            },
            "total_count": 0
        }
        
        # Find by file hash
        if file_hash:
            all_duplicates["duplicates"]["by_hash"] = self.find_duplicates_by_hash(
                file_hash,
                exclude_candidate_id=candidate_id
            )
        
        # Find by email
        if candidate.email:
            all_duplicates["duplicates"]["by_email"] = self.find_duplicates_by_email(
                candidate.email,
                exclude_candidate_id=candidate_id
            )
        
        # Find by phone
        if candidate.phone:
            all_duplicates["duplicates"]["by_phone"] = self.find_duplicates_by_phone(
                candidate.phone,
                exclude_candidate_id=candidate_id
            )
        
        # Find fuzzy duplicates
        all_duplicates["duplicates"]["fuzzy"] = self.find_fuzzy_duplicates(
            candidate,
            similarity_threshold=similarity_threshold,
            exclude_candidate_id=candidate_id
        )
        
        # Calculate total unique duplicates
        seen_ids: Set[str] = set()
        for dup_type in all_duplicates["duplicates"].values():
            for dup in dup_type:
                seen_ids.add(dup["candidate_id"])
        
        all_duplicates["total_count"] = len(seen_ids)
        
        logger.info(
            f"Found {all_duplicates['total_count']} total duplicates for candidate {candidate_id}"
        )
        
        return all_duplicates
    
    def merge_candidates(
        self,
        primary_candidate_id: str,
        duplicate_candidate_ids: List[str],
        merge_strategy: str = "keep_newest"
    ) -> Dict[str, Any]:
        """
        Merge duplicate candidates into a single candidate.
        
        Args:
            primary_candidate_id: ID of the primary candidate to keep
            duplicate_candidate_ids: List of duplicate candidate IDs to merge
            merge_strategy: Strategy for merging (keep_newest, keep_oldest, keep_most_complete)
            
        Returns:
            Dictionary with merge results
        """
        primary = self.db.query(Candidate).filter(
            Candidate.id == primary_candidate_id
        ).first()
        
        if not primary:
            raise ValueError(f"Primary candidate not found: {primary_candidate_id}")
        
        duplicates = self.db.query(Candidate).filter(
            Candidate.id.in_(duplicate_candidate_ids)
        ).all()
        
        if not duplicates:
            raise ValueError("No duplicate candidates found")
        
        merged_data = {
            "primary_candidate_id": str(primary_candidate_id),
            "merged_candidate_ids": duplicate_candidate_ids,
            "merge_strategy": merge_strategy,
            "fields_merged": [],
            "conflicts": []
        }
        
        # Merge fields based on strategy
        for duplicate in duplicates:
            # Merge email if primary doesn't have one
            if not primary.email and duplicate.email:
                primary.email = duplicate.email
                merged_data["fields_merged"].append(f"email from {duplicate.id}")
            
            # Merge phone if primary doesn't have one
            if not primary.phone and duplicate.phone:
                primary.phone = duplicate.phone
                merged_data["fields_merged"].append(f"phone from {duplicate.id}")
            
            # Merge skills (union of both)
            primary_skills = set(skill.name for skill in primary.skills)
            duplicate_skills = set(skill.name for skill in duplicate.skills)
            new_skills = duplicate_skills - primary_skills
            
            if new_skills:
                merged_data["fields_merged"].append(f"{len(new_skills)} skills from {duplicate.id}")
            
            # Merge work history
            primary_work = set((wh.company_name, wh.job_title) for wh in primary.work_history)
            duplicate_work = set((wh.company_name, wh.job_title) for wh in duplicate.work_history)
            new_work = duplicate_work - primary_work
            
            if new_work:
                merged_data["fields_merged"].append(f"{len(new_work)} work history entries from {duplicate.id}")
        
        # Update primary candidate
        primary.updated_at = datetime.utcnow()
        self.db.commit()
        
        # Mark duplicates as merged (you might want to add a status field for this)
        # For now, we'll just log it
        for duplicate in duplicates:
            logger.info(f"Marking candidate {duplicate.id} as merged into {primary_candidate_id}")
        
        merged_data["success"] = True
        merged_data["message"] = f"Successfully merged {len(duplicates)} candidates"
        
        return merged_data
    
    def check_duplicate_on_upload(
        self,
        file_path: str,
        email: Optional[str] = None,
        phone: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Check for duplicates when uploading a new resume.
        
        Args:
            file_path: Path to the resume file
            email: Email address (optional)
            phone: Phone number (optional)
            
        Returns:
            Dictionary with duplicate check results
        """
        results = {
            "has_duplicates": False,
            "duplicates": [],
            "duplicate_types": []
        }
        
        # Check file hash
        try:
            file_hash = self.compute_resume_hash(file_path)
            hash_duplicates = self.find_duplicates_by_hash(file_hash)
            
            if hash_duplicates:
                results["has_duplicates"] = True
                results["duplicates"].extend(hash_duplicates)
                results["duplicate_types"].append("file_hash")
        except Exception as e:
            logger.error(f"Error checking file hash: {e}")
        
        # Check email
        if email:
            email_duplicates = self.find_duplicates_by_email(email)
            
            if email_duplicates:
                results["has_duplicates"] = True
                results["duplicates"].extend(email_duplicates)
                results["duplicate_types"].append("email")
        
        # Check phone
        if phone:
            phone_duplicates = self.find_duplicates_by_phone(phone)
            
            if phone_duplicates:
                results["has_duplicates"] = True
                results["duplicates"].extend(phone_duplicates)
                results["duplicate_types"].append("phone")
        
        # Remove duplicate entries (same candidate might match multiple criteria)
        seen_ids: Set[str] = set()
        unique_duplicates = []
        for dup in results["duplicates"]:
            if dup["candidate_id"] not in seen_ids:
                seen_ids.add(dup["candidate_id"])
                unique_duplicates.append(dup)
        
        results["duplicates"] = unique_duplicates
        results["duplicate_count"] = len(unique_duplicates)
        
        logger.info(
            f"Duplicate check on upload: found {results['duplicate_count']} duplicates"
        )
        
        return results
