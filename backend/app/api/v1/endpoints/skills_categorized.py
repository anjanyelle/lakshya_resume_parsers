"""
Categorized Skills API Endpoint
Returns skills grouped by category for better ATS search and candidate matching

Uses comprehensive 18,300+ IT skills taxonomy with domain-wise categorization
"""

import json
from pathlib import Path
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, List, Any

from app.api.deps import get_current_user, get_db
from app.models.candidate import Candidate
from app.models.candidate_skill import CandidateSkill

router = APIRouter()

# Load comprehensive skills taxonomy (18,300+ skills across 18 domains)
TAXONOMY_PATH = Path(__file__).parent / "worldwide_clean_18300_it_skills_domain_wise.json"
SKILLS_TAXONOMY = {}
SKILL_TO_DOMAIN = {}

def _load_taxonomy():
    """Load the comprehensive skills taxonomy on startup."""
    global SKILLS_TAXONOMY, SKILL_TO_DOMAIN
    try:
        with open(TAXONOMY_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
            SKILLS_TAXONOMY = data.get('domains', {})
            
            # Create reverse mapping: skill -> domain
            for domain, skills in SKILLS_TAXONOMY.items():
                for skill in skills:
                    # Normalize skill name for matching
                    normalized = skill.lower().strip()
                    SKILL_TO_DOMAIN[normalized] = domain
    except Exception as e:
        print(f"Warning: Could not load skills taxonomy: {e}")

# Load taxonomy on module import
_load_taxonomy()


@router.get("/candidates/{candidate_id}/skills/categorized")
def get_categorized_skills(
    candidate_id: UUID,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Return candidate skills grouped by domain using 18,300+ skills taxonomy.
    
    Domains (18 total):
    - Programming Languages and Language Internals
    - Frontend Web Development
    - Backend Web Development
    - Databases Storage Search and Vector DB
    - Cloud Computing Platforms
    - DevOps SRE Platform Engineering
    - Software Testing QA and Automation
    - AI ML NLP and LLM Engineering
    - Data Engineering Big Data and Streaming
    - Data Science Analytics and BI
    - Mobile Application Development
    - Java Ecosystem
    - Cybersecurity and Compliance
    - Blockchain Web3 IoT AR VR and Game Development
    - Enterprise Platforms ERP CRM ITSM and Low Code
    - Networking Infrastructure and Operating Systems
    - System Design Architecture and Distributed Systems
    - UI UX Product and Project Management
    - Resume Parser HR Tech ATS and Document AI
    - Other (uncategorized)
    """
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    skills = db.query(CandidateSkill).filter(CandidateSkill.candidate_id == candidate_id).all()
    
    # Initialize categorized dict with all domains
    categorized = {domain: [] for domain in SKILLS_TAXONOMY.keys()}
    categorized["Other"] = []
    categorized["all_skills"] = []
    
    for skill in skills:
        skill_data = {
            "name": skill.name,
            "normalized_name": skill.normalized_name,
            "confidence": skill.confidence,
            "years_experience": skill.years_experience,
            "proficiency": skill.proficiency,
            "source": getattr(skill, 'source', None)
        }
        
        # Find domain for this skill using taxonomy
        normalized_skill = (skill.normalized_name or skill.name or "").lower().strip()
        domain = SKILL_TO_DOMAIN.get(normalized_skill)
        
        if domain:
            skill_data["domain"] = domain
            categorized[domain].append(skill_data)
        else:
            # Try partial matching for skills not in taxonomy
            skill_data["domain"] = "Other"
            categorized["Other"].append(skill_data)
        
        categorized["all_skills"].append(skill_data)
    
    # Sort each domain by confidence (highest first)
    for domain in categorized:
        categorized[domain] = sorted(
            categorized[domain],
            key=lambda x: x["confidence"] or 0.0,
            reverse=True
        )
    
    # Remove empty domains for cleaner response
    categorized = {k: v for k, v in categorized.items() if v}
    
    return categorized


@router.get("/candidates/{candidate_id}/skills/summary")
def get_skills_summary(
    candidate_id: UUID,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    Return a summary of candidate skills with counts by domain using 18,300+ skills taxonomy.
    """
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    skills = db.query(CandidateSkill).filter(CandidateSkill.candidate_id == candidate_id).all()
    
    # Count by domain using taxonomy
    domain_counts = {}
    top_skills = []
    skills_by_source = {"technical_skills_section": 0, "experience": 0, "raw_text": 0}
    
    for skill in skills:
        # Find domain using taxonomy
        normalized_skill = (skill.normalized_name or skill.name or "").lower().strip()
        domain = SKILL_TO_DOMAIN.get(normalized_skill, "Other")
        domain_counts[domain] = domain_counts.get(domain, 0) + 1
        
        # Track source
        source = getattr(skill, 'source', None)
        if source in skills_by_source:
            skills_by_source[source] += 1
        
        # Collect high-confidence skills
        if skill.confidence and skill.confidence >= 0.7:
            top_skills.append({
                "name": skill.name,
                "domain": domain,
                "confidence": skill.confidence,
                "years_experience": skill.years_experience,
                "source": source
            })
    
    # Sort top skills by confidence
    top_skills = sorted(top_skills, key=lambda x: x["confidence"], reverse=True)[:20]
    
    return {
        "total_skills": len(skills),
        "domain_counts": domain_counts,
        "top_skills": top_skills,
        "skills_by_source": skills_by_source,
        "high_confidence_count": len([s for s in skills if s.confidence and s.confidence >= 0.7]),
        "medium_confidence_count": len([s for s in skills if s.confidence and 0.5 <= s.confidence < 0.7]),
        "low_confidence_count": len([s for s in skills if s.confidence and s.confidence < 0.5]),
        "taxonomy_coverage": f"{len([s for s in skills if SKILL_TO_DOMAIN.get((s.normalized_name or s.name or '').lower().strip())])}/{len(skills)} skills in taxonomy"
    }
