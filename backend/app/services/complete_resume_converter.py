# Complete Resume JSON Format Converter

from typing import Dict, List, Any, Optional
from datetime import date, datetime
from app.schemas.enhanced_schemas import CompleteResumeJSON, BasicsBase, ProjectBase, PublicationBase, VolunteerBase, AwardBase, ReferenceBase, AdditionalTextBase

class CompleteResumeConverter:
    """
    Converts parsed resume data to target JSON format
    """
    
    def __init__(self):
        self.target_format = CompleteResumeJSON()
    
    def convert_to_target_format(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert parsed data to target JSON format
        """
        target_json = {
            "basics": self._convert_basics(parsed_data.get('basics', {})),
            "profile": self._convert_profile(parsed_data.get('profile')),
            "work": self._convert_work(parsed_data.get('work', [])),
            "education": self._convert_education(parsed_data.get('education', [])),
            "projects": self._convert_projects(parsed_data.get('projects', [])),
            "volunteer": self._convert_volunteer(parsed_data.get('volunteer', [])),
            "skills": self._convert_skills(parsed_data.get('skills', [])),
            "certifications": self._convert_certifications(parsed_data.get('certifications', [])),
            "publications": self._convert_publications(parsed_data.get('publications', [])),
            "awards": self._convert_awards(parsed_data.get('awards', [])),
            "achievements": self._convert_achievements(parsed_data.get('achievements', [])),
            "hobbies": self._convert_hobbies(parsed_data.get('hobbies', [])),
            "references": self._convert_references(parsed_data.get('references', [])),
            "texts": self._convert_texts(parsed_data.get('texts', []))
        }
        
        return target_json
    
    def _convert_basics(self, basics_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert basics data to target format"""
        basics = {
            "firstName": None,
            "lastName": None,
            "titleBeforeName": None,
            "titleAfterName": None,
            "dateOfBirth": None,
            "phone": [],
            "email": [],
            "web": [],
            "street": None,
            "city": None,
            "country": None,
            "postal": None
        }
        
        # Handle name parsing
        full_name = basics_data.get('full_name', '')
        if full_name:
            name_parts = full_name.split()
            if len(name_parts) >= 2:
                basics['firstName'] = name_parts[0]
                basics['lastName'] = ' '.join(name_parts[1:])
            else:
                basics['firstName'] = full_name
        
        # Extract individual name fields if available
        basics['firstName'] = basics_data.get('first_name') or basics['firstName']
        basics['lastName'] = basics_data.get('last_name') or basics['lastName']
        basics['titleBeforeName'] = basics_data.get('title_before_name')
        basics['titleAfterName'] = basics_data.get('title_after_name')
        basics['dateOfBirth'] = self._format_date(basics_data.get('date_of_birth'))
        
        # Contact information
        phone = basics_data.get('phone', '')
        if phone:
            basics['phone'] = [phone] if isinstance(phone, str) else phone
        
        email = basics_data.get('email', '')
        if email:
            basics['email'] = [email] if isinstance(email, str) else email
        
        # Web/LinkedIn
        web = []
        linkedin = basics_data.get('linkedin_url', '')
        if linkedin:
            web.append(linkedin)
        
        github = basics_data.get('github_url', '')
        if github:
            web.append(github)
        
        if basics_data.get('web'):
            if isinstance(basics_data['web'], list):
                web.extend(basics_data['web'])
            else:
                web.append(basics_data['web'])
        
        basics['web'] = list(set(web)) if web else []
        
        # Location
        location = basics_data.get('location', '')
        if location:
            # Try to parse city, country from location
            if ',' in location:
                parts = location.split(',')
                basics['city'] = parts[0].strip()
                if len(parts) > 1:
                    basics['country'] = parts[1].strip()
            else:
                basics['city'] = location
        
        basics['street'] = basics_data.get('street')
        basics['country'] = basics_data.get('country') or basics['country']
        basics['postal'] = basics_data.get('postal')
        
        return {k: v for k, v in basics.items() if v is not None and v != [] and v != ''}
    
    def _convert_profile(self, profile_data: Any) -> Optional[str]:
        """Convert profile/summary to target format"""
        if not profile_data:
            return None
        
        if isinstance(profile_data, str):
            return profile_data.strip()
        
        if isinstance(profile_data, dict):
            return profile_data.get('summary') or profile_data.get('description')
        
        return str(profile_data).strip() if profile_data else None
    
    def _convert_work(self, work_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert work experience to target format"""
        work_list = []
        
        for work in work_data:
            work_entry = {
                "jobTitle": work.get('job_title') or work.get('title') or '',
                "company": work.get('company_name') or work.get('company') or '',
                "city": work.get('location') or work.get('city') or '',
                "country": work.get('country') or None,
                "description": work.get('description') or '',
                "startDate": self._format_date(work.get('start_date')),
                "endDate": self._format_date(work.get('end_date'))
            }
            
            # Only add non-empty entries
            if work_entry['jobTitle'] or work_entry['company']:
                work_list.append(work_entry)
        
        return work_list
    
    def _convert_education(self, education_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert education to target format"""
        education_list = []
        
        for edu in education_data:
            edu_entry = {
                "degree": edu.get('degree') or '',
                "fieldOfStudy": edu.get('field_of_study') or '',
                "institution": edu.get('institution') or '',
                "city": edu.get('city') or '',
                "country": edu.get('country') or '',
                "description": edu.get('description') or '',
                "startDate": self._format_date(edu.get('start_date')),
                "endDate": self._format_date(edu.get('end_date'))
            }
            
            education_list.append(edu_entry)
        
        return education_list
    
    def _convert_projects(self, projects_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert projects to target format"""
        projects_list = []
        
        for project in projects_data:
            project_entry = {
                "name": project.get('name') or '',
                "description": project.get('description') or '',
                "startDate": self._format_date(project.get('start_date')),
                "endDate": self._format_date(project.get('end_date'))
            }
            
            projects_list.append(project_entry)
        
        return projects_list
    
    def _convert_volunteer(self, volunteer_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert volunteer experience to target format"""
        volunteer_list = []
        
        for volunteer in volunteer_data:
            volunteer_entry = {
                "organization": volunteer.get('organization') or '',
                "role": volunteer.get('role') or '',
                "description": volunteer.get('description') or '',
                "startDate": self._format_date(volunteer.get('start_date')),
                "endDate": self._format_date(volunteer.get('end_date')),
                "location": volunteer.get('location') or ''
            }
            
            volunteer_list.append(volunteer_entry)
        
        return volunteer_list
    
    def _convert_skills(self, skills_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert skills to target format"""
        skills_list = []
        
        # Group skills by category
        skills_by_category = {}
        for skill in skills_data:
            category = skill.get('category', 'Technical Skills')
            if category not in skills_by_category:
                skills_by_category[category] = []
            skills_by_category[category].append(skill.get('name', ''))
        
        # Convert to target format
        for category, skill_names in skills_by_category.items():
            skills_list.append({
                "name": category,
                "skills": skill_names
            })
        
        return skills_list
    
    def _convert_certifications(self, certifications_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert certifications to target format"""
        cert_list = []
        
        for cert in certifications_data:
            cert_entry = {
                "name": cert.get('name') or '',
                "issuer": cert.get('issuing_organization') or cert.get('issuer') or None,
                "description": cert.get('description') or None,
                "awardDate": self._format_date(cert.get('issue_date') or cert.get('award_date'))
            }
            
            cert_list.append(cert_entry)
        
        return cert_list
    
    def _convert_publications(self, publications_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert publications to target format"""
        pubs_list = []
        
        for pub in publications_data:
            pub_entry = {
                "name": pub.get('name') or '',
                "publisher": pub.get('publisher') or None,
                "description": pub.get('description') or '',
                "publicationDate": self._format_date(pub.get('publication_date'))
            }
            
            pubs_list.append(pub_entry)
        
        return pubs_list
    
    def _convert_awards(self, awards_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert awards to target format"""
        awards_list = []
        
        for award in awards_data:
            award_entry = {
                "name": award.get('name') or '',
                "issuer": award.get('issuer') or None,
                "description": award.get('description') or None,
                "awardDate": self._format_date(award.get('award_date'))
            }
            
            awards_list.append(award_entry)
        
        return awards_list
    
    def _convert_achievements(self, achievements_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert achievements to target format"""
        # This maps to your existing achievements structure
        return achievements_data
    
    def _convert_hobbies(self, hobbies_data: List[str]) -> List[str]:
        """Convert hobbies to target format"""
        if isinstance(hobbies_data, list):
            return hobbies_data
        elif isinstance(hobbies_data, str):
            return [hobbies_data]
        elif isinstance(hobbies_data, dict):
            # Extract from hobbies JSON field
            return hobbies_data.get('hobbies', [])
        else:
            return []
    
    def _convert_references(self, references_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert references to target format"""
        refs_list = []
        
        for ref in references_data:
            ref_entry = {
                "name": ref.get('name') or '',
                "company": ref.get('company') or None,
                "position": ref.get('position') or None,
                "email": ref.get('email') or None,
                "phone": ref.get('phone') or None
            }
            
            refs_list.append(ref_entry)
        
        return refs_list
    
    def _convert_texts(self, texts_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert additional texts to target format"""
        texts_list = []
        
        for text in texts_data:
            text_entry = {
                "content": text.get('content') or '',
            }
            
            texts_list.append(text_entry)
        
        return texts_list
    
    def _format_date(self, date_value: Any) -> Optional[str]:
        """Format date to target JSON format"""
        if not date_value:
            return None
        
        if isinstance(date_value, str):
            # Try to parse and format
            try:
                if len(date_value) == 4:  # Year only
                    return date_value
                # Add more date parsing logic as needed
                return date_value
            except:
                return date_value
        
        if isinstance(date_value, date):
            return date_value.strftime('%Y-%m-%d')
        
        if isinstance(date_value, datetime):
            return date_value.strftime('%Y-%m-%d')
        
        return str(date_value)

# Usage Example
def convert_resume_to_target_format(parsed_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main function to convert any parsed resume data to target JSON format
    """
    converter = CompleteResumeConverter()
    return converter.convert_to_target_format(parsed_data)
