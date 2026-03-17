# Enhanced Database Integration for Complete Resume JSON

"""
Functions to save complete resume JSON data to new database tables
"""

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.additional_models import Project, Publication, Volunteer, Award, Reference, AdditionalText
from app.models.candidate import Candidate
from app.models.work_history import WorkHistory
from app.models.education import Education
from app.models.skill import Skill
from app.models.certification import Certification
from app.models.candidate_achievement import CandidateAchievement
from app.models.candidate_skill import CandidateSkill
import uuid

def save_complete_resume_to_db(job_id: str, complete_json: dict):
    """
    Save complete resume JSON data to all database tables
    """
    session = SessionLocal()
    
    try:
        # Get candidate ID
        job = session.query(Candidate).filter_by(id=job_id).first()
        if not job:
            print(f"❌ Job {job_id} not found")
            return
        
        candidate_id = job.candidate_id
        
        print(f"🔍 Saving complete resume data for candidate {candidate_id}")
        print("=" * 60)
        
        # 1. Save Basics (Update candidates table)
        if complete_json.get('basics'):
            save_basics_data(session, candidate_id, complete_json['basics'])
        
        # 2. Save Projects
        if complete_json.get('projects'):
            save_projects_data(session, candidate_id, complete_json['projects'])
        
        # 3. Save Publications
        if complete_json.get('publications'):
            save_publications_data(session, candidate_id, complete_json['publications'])
        
        # 4. Save Volunteer Experience
        if complete_json.get('volunteer'):
            save_volunteer_data(session, candidate_id, complete_json['volunteer'])
        
        # 5. Save Awards
        if complete_json.get('awards'):
            save_awards_data(session, candidate_id, complete_json['awards'])
        
        # 6. Save Additional Texts
        if complete_json.get('texts'):
            save_additional_texts_data(session, candidate_id, complete_json['texts'])
        
        # 7. Update Profile (already handled by existing logic)
        if complete_json.get('profile'):
            # Profile is already saved in candidates.summary field
            pass
        
        session.commit()
        print("✅ Complete resume data saved successfully!")
        print("📊 Summary:")
        print(f"   - Projects: {len(complete_json.get('projects', []))}")
        print(f"   - Publications: {len(complete_json.get('publications', []))}")
        print(f"   - Volunteer: {len(complete_json.get('volunteer', []))}")
        print(f"   - Awards: {len(complete_json.get('awards', []))}")
        print(f"   - Additional Texts: {len(complete_json.get('texts', []))}")
        
    except Exception as e:
        session.rollback()
        print(f"❌ Error saving complete resume data: {e}")
    finally:
        session.close()

def save_basics_data(session, candidate_id: str, basics_data: dict):
    """Save basics data to candidates table"""
    candidate = session.query(Candidate).filter_by(id=candidate_id).first()
    if not candidate:
        return
    
    # Update candidate fields
    if basics_data.get('firstName'):
        candidate.first_name = basics_data['firstName']
    if basics_data.get('lastName'):
        candidate.last_name = basics_data['lastName']
    if basics_data.get('titleBeforeName'):
        candidate.title_before_name = basics_data['titleBeforeName']
    if basics_data.get('titleAfterName'):
        candidate.title_after_name = basics_data['titleAfterName']
    if basics_data.get('dateOfBirth'):
        candidate.date_of_birth = basics_data['dateOfBirth']
    if basics_data.get('street'):
        candidate.street = basics_data['street']
    if basics_data.get('city'):
        candidate.city = basics_data['city']
    if basics_data.get('country'):
        candidate.country = basics_data['country']
    if basics_data.get('postal'):
        candidate.postal = basics_data['postal']
    if basics_data.get('web'):
        candidate.web = basics_data['web']
    if basics_data.get('profile'):
        candidate.profile = basics_data['profile']
    if basics_data.get('hobbies'):
        candidate.hobbies = basics_data['hobbies']
    
    print("   ✅ Basics data updated")

def save_projects_data(session, candidate_id: str, projects_data: list):
    """Save projects data to projects table"""
    # Delete existing projects for this candidate
    session.query(Project).filter_by(candidate_id=candidate_id).delete()
    
    for i, project_data in enumerate(projects_data):
        project = Project(
            id=str(uuid.uuid4()),
            candidate_id=candidate_id,
            name=project_data.get('name', ''),
            description=project_data.get('description', ''),
            start_date=_parse_date(project_data.get('startDate')),
            end_date=_parse_date(project_data.get('endDate')),
            display_order=i
        )
        session.add(project)
    
    print(f"   ✅ Projects saved: {len(projects_data)} entries")

def save_publications_data(session, candidate_id: str, publications_data: list):
    """Save publications data to publications table"""
    # Delete existing publications for this candidate
    session.query(Publication).filter_by(candidate_id=candidate_id).delete()
    
    for i, pub_data in enumerate(publications_data):
        publication = Publication(
            id=str(uuid.uuid4()),
            candidate_id=candidate_id,
            name=pub_data.get('name', ''),
            publisher=pub_data.get('publisher'),
            description=pub_data.get('description', ''),
            publication_date=_parse_date(pub_data.get('publicationDate')),
            display_order=i
        )
        session.add(publication)
    
    print(f"   ✅ Publications saved: {len(publications_data)} entries")

def save_volunteer_data(session, candidate_id: str, volunteer_data: list):
    """Save volunteer data to volunteer_experience table"""
    # Delete existing volunteer experience for this candidate
    session.query(Volunteer).filter_by(candidate_id=candidate_id).delete()
    
    for i, vol_data in enumerate(volunteer_data):
        volunteer = Volunteer(
            id=str(uuid.uuid4()),
            candidate_id=candidate_id,
            organization=vol_data.get('organization', ''),
            role=vol_data.get('role', ''),
            description=vol_data.get('description', ''),
            start_date=_parse_date(vol_data.get('startDate')),
            end_date=_parse_date(vol_data.get('endDate')),
            location=vol_data.get('location', ''),
            display_order=i
        )
        session.add(volunteer)
    
    print(f"   ✅ Volunteer experience saved: {len(volunteer_data)} entries")

def save_awards_data(session, candidate_id: str, awards_data: list):
    """Save awards data to awards table"""
    # Delete existing awards for this candidate
    session.query(Award).filter_by(candidate_id=candidate_id).delete()
    
    for i, award_data in enumerate(awards_data):
        award = Award(
            id=str(uuid.uuid4()),
            candidate_id=candidate_id,
            name=award_data.get('name', ''),
            issuer=award_data.get('issuer'),
            description=award_data.get('description', ''),
            award_date=_parse_date(award_data.get('awardDate')),
            display_order=i
        )
        session.add(award)
    
    print(f"   ✅ Awards saved: {len(awards_data)} entries")

def save_additional_texts_data(session, candidate_id: str, texts_data: list):
    """Save additional texts data to additional_texts table"""
    # Delete existing additional texts for this candidate
    session.query(AdditionalText).filter_by(candidate_id=candidate_id).delete()
    
    for i, text_data in enumerate(texts_data):
        additional_text = AdditionalText(
            id=str(uuid.uuid4()),
            candidate_id=candidate_id,
            content=text_data.get('content', ''),
            section_type=text_data.get('section_type', ''),
            display_order=i
        )
        session.add(additional_text)
    
    print(f"   ✅ Additional texts saved: {len(texts_data)} entries")

def _parse_date(date_value):
    """Parse date string to date object"""
    if not date_value:
        return None
    # Add more date parsing logic as needed
    return date_value

# Integration function to call from pipeline
def integrate_complete_resume_parsing(job_id: str, complete_json: dict):
    """
    Main integration function - call this from pipeline
    """
    save_complete_resume_to_db(job_id, complete_json)
