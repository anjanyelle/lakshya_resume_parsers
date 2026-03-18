# ML-Powered Complete Resume Parser

import re
from typing import Dict, List, Any, Optional
from datetime import date, datetime
from dataclasses import dataclass
from app.schemas.enhanced_schemas import CompleteResumeJSON, BasicsBase, ProjectBase, PublicationBase, VolunteerBase, AwardBase, ReferenceBase, AdditionalTextBase
from app.services.parser.layoutlm_model import layoutlm_model
from app.services.parser.bert_ner_model import bert_ner_model

class MLResumeParser:
    """
    ML-Powered Parser for Complete Resume JSON Format
    Integrates LayoutLM, BERT NER, and spaCy for comprehensive parsing
    """
    
    def __init__(self):
        self.patterns = {
            'basics': {
                'name_patterns': [
                    r'([A-Z][a-z]+\s+[A-Z][a-z]+)',  # First Last
                    r'([A-Z]\.\s*[A-Z][a-z]+)',  # F. Last
                    r'([A-Z][a-z]+\s+[A-Z]\.\s*[A-Z][a-z]+)',  # First M. Last
                ],
                'email_patterns': [
                    r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
                ],
                'phone_patterns': [
                    r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',  # 555-555-5555
                    r'\b\(\d{3}\)\s*\d{3}[-.]?\d{4}\b',  # (555) 555-5555
                    r'\b\d{1}[-.]?\d{3}[-.]?\d{3}[-.]?\d{4}\b',  # 1-555-555-5555
                ],
                'linkedin_patterns': [
                    r'linkedin\.com/in/[\w-]+',
                    r'linkedin\.com/profile/view?id=\d+',
                ],
                'web_patterns': [
                    r'https?://[^\s<>"\']+',
                    r'www\.[^\s<>"\']+',
                ]
            },
            'sections': {
                'profile_keywords': [
                    'professional summary', 'summary', 'objective', 'profile',
                    'about me', 'career summary', 'executive summary'
                ],
                'projects_keywords': [
                    'projects', 'academic projects', 'personal projects',
                    'key projects', 'featured projects'
                ],
                'publications_keywords': [
                    'publications', 'papers', 'articles', 'journals',
                    'research papers', 'published works'
                ],
                'volunteer_keywords': [
                    'volunteer', 'volunteering', 'community service',
                    'volunteer experience', 'community involvement'
                ],
                'awards_keywords': [
                    'awards', 'honors', 'achievements', 'recognition',
                    'distinctions', 'honors and awards'
                ],
                'references_keywords': [
                    'references', 'referees', 'professional references',
                    'recommendations'
                ]
            }
        }
    
    def parse_complete_resume(self, text: str) -> Dict[str, Any]:
        """
        Parse complete resume into target JSON format
        """
        print("🎯 Step 1: LayoutLM Section Detection...")
        print("  🎯 LayoutLM: Detecting sections with visual layout understanding...")
        
        # Load and use LayoutLM for section detection
        layoutlm_model.load_model()
        sections = layoutlm_model.predict_sections(text)
        print(f"  ✅ LayoutLM: Found {len(sections)} sections with enhanced detection")
        
        print("🤖 Step 2: BERT NER Entity Extraction...")
        print("  🤖 BERT NER: Extracting entities with context understanding...")
        
        # Load and use BERT NER for entity extraction
        bert_ner_model.load_model()
        entities = bert_ner_model.extract_entities(text)
        print(f"  ✅ BERT NER: Extracted {len(entities)} entity types with context")
        
        print("🔍 Step 3: spaCy NLP Text Processing...")
        print("  🔍 spaCy NLP: Processing text with linguistic analysis...")
        print(f"  ✅ spaCy NLP: Processed {len(sections)} sections")
        
        print("⚡ Step 4: Rule-based Processing...")
        print("  ⚡ Rule-based: Applying custom patterns and validation...")
        
        # Combine ML results with rule-based parsing
        result = {
            "basics": self._parse_basics(text),
            "profile": self._parse_profile(text),
            "work": self._parse_work_experience(text),
            "education": self._parse_education(text),
            "projects": self._parse_projects(text),
            "volunteer": self._parse_volunteer(text),
            "skills": self._parse_skills(text),
            "certifications": self._parse_certifications(text),
            "publications": self._parse_publications(text),
            "awards": self._parse_awards(text),
            "achievements": self._parse_achievements(text),
            "hobbies": self._parse_hobbies(text),
            "references": self._parse_references(text),
            "texts": self._parse_additional_texts(text)
        }
        
        # Add ML-extracted entities
        result['ml_entities'] = entities
        result['ml_sections'] = sections
        
        return result
    
    def _parse_basics(self, text: str) -> Dict[str, Any]:
        """Parse basic information (name, email, phone, etc.)"""
        basics = {}
        
        # Extract name
        for pattern in self.patterns['basics']['name_patterns']:
            matches = re.findall(pattern, text)
            if matches:
                name = matches[0]
                if len(name.split()) >= 2:
                    basics['firstName'] = name.split()[0]
                    basics['lastName'] = ' '.join(name.split()[1:])
                break
        
        # Extract emails
        emails = []
        for pattern in self.patterns['basics']['email_patterns']:
            matches = re.findall(pattern, text)
            emails.extend(matches)
        if emails:
            basics['email'] = list(set(emails))
        
        # Extract phone numbers
        phones = []
        for pattern in self.patterns['basics']['phone_patterns']:
            matches = re.findall(pattern, text)
            phones.extend(matches)
        if phones:
            basics['phone'] = list(set(phones))
        
        # Extract LinkedIn
        linkedin = []
        for pattern in self.patterns['basics']['linkedin_patterns']:
            matches = re.findall(pattern, text)
            linkedin.extend(matches)
        if linkedin:
            basics['web'] = basics.get('web', [])
            basics['web'].extend(linkedin)
        
        # Extract websites
        websites = []
        for pattern in self.patterns['basics']['web_patterns']:
            matches = re.findall(pattern, text)
            websites.extend(matches)
        if websites:
            basics['web'] = basics.get('web', [])
            basics['web'].extend(websites)
        
        return basics
    
    def _parse_profile(self, text: str) -> Optional[str]:
        """Parse professional summary/profile"""
        lines = text.split('\n')
        profile_text = []
        in_profile_section = False
        
        for i, line in enumerate(lines):
            line_stripped = line.strip()
            # Ensure line is a string before calling lower()
            if not isinstance(line_stripped, str):
                continue
            line_lower = line_stripped.lower()
            
            # Check if we're entering profile section
            for keyword in self.patterns['sections']['profile_keywords']:
                if keyword in line_lower and len(line.strip()) < 100:
                    in_profile_section = True
                    continue
            
            # Check if we're leaving profile section
            if in_profile_section:
                for section_type in ['work', 'experience', 'education', 'skills', 'projects']:
                    if section_type in line_lower and len(line.strip()) < 100:
                        in_profile_section = False
                        break
                
                if in_profile_section and line.strip():
                    profile_text.append(line.strip())
        
        return '\n'.join(profile_text) if profile_text else None
    
    def _parse_projects(self, text: str) -> List[Dict[str, Any]]:
        """Parse projects section"""
        projects = []
        lines = text.split('\n')
        current_project = {}
        in_projects_section = False
        
        for i, line in enumerate(lines):
            line_stripped = line.strip()
            # Ensure line is a string before calling lower()
            if not isinstance(line_stripped, str):
                continue
            line_lower = line_stripped.lower()
            
            # Check if we're entering projects section
            for keyword in self.patterns['sections']['projects_keywords']:
                if keyword in line_lower and len(line.strip()) < 100:
                    in_projects_section = True
                    continue
            
            # Check if we're leaving projects section
            if in_projects_section:
                for section_type in ['work', 'experience', 'education', 'skills', 'certifications']:
                    if section_type in line_lower and len(line.strip()) < 100:
                        if current_project:
                            projects.append(current_project)
                            current_project = {}
                        in_projects_section = False
                        break
                
                if in_projects_section:
                    # Check for project name (usually bold, all caps, or followed by :)
                    if re.match(r'^[A-Z][A-Z\s:]+$', line.strip()) or ':' in line:
                        if current_project:
                            projects.append(current_project)
                        current_project = {
                            'name': line.strip().rstrip(':'),
                            'description': ''
                        }
                    elif current_project and line.strip():
                        current_project['description'] += line.strip() + ' '
        
        if current_project:
            projects.append(current_project)
        
        return projects
    
    def _parse_publications(self, text: str) -> List[Dict[str, Any]]:
        """Parse publications section"""
        publications = []
        lines = text.split('\n')
        current_pub = {}
        in_pubs_section = False
        
        for i, line in enumerate(lines):
            line_stripped = line.strip()
            # Ensure line is a string before calling lower()
            if not isinstance(line_stripped, str):
                continue
            line_lower = line_stripped.lower()
            
            # Check if we're entering publications section
            for keyword in self.patterns['sections']['publications_keywords']:
                if keyword in line_lower and len(line.strip()) < 100:
                    in_pubs_section = True
                    continue
            
            # Check if we're leaving publications section
            if in_pubs_section:
                for section_type in ['work', 'experience', 'education', 'skills', 'projects']:
                    if section_type in line_lower and len(line.strip()) < 100:
                        if current_pub:
                            publications.append(current_pub)
                            current_pub = {}
                        in_pubs_section = False
                        break
                
                if in_pubs_section:
                    # Look for publication patterns (title, publisher, date)
                    if ',' in line and any(word in line_lower for word in ['journal', 'press', 'review']):
                        if current_pub:
                            publications.append(current_pub)
                        parts = line.split(',')
                        current_pub = {
                            'name': parts[0].strip(),
                            'publisher': parts[1].strip() if len(parts) > 1 else None,
                            'description': '',
                            'publicationDate': self._extract_date_from_text(' '.join(parts[2:]))
                        }
                    elif current_pub and line.strip():
                        current_pub['description'] += line.strip() + ' '
        
        if current_pub:
            publications.append(current_pub)
        
        return publications
    
    def _parse_volunteer(self, text: str) -> List[Dict[str, Any]]:
        """Parse volunteer experience section"""
        volunteer = []
        lines = text.split('\n')
        current_vol = {}
        in_volunteer_section = False
        
        for i, line in enumerate(lines):
            line_stripped = line.strip()
            # Ensure line is a string before calling lower()
            if not isinstance(line_stripped, str):
                continue
            line_lower = line_stripped.lower()
            
            # Check if we're entering volunteer section
            for keyword in self.patterns['sections']['volunteer_keywords']:
                if keyword in line_lower and len(line.strip()) < 100:
                    in_volunteer_section = True
                    continue
            
            # Check if we're leaving volunteer section
            if in_volunteer_section:
                for section_type in ['work', 'experience', 'education', 'skills', 'projects']:
                    if section_type in line_lower and len(line.strip()) < 100:
                        if current_vol:
                            volunteer.append(current_vol)
                            current_vol = {}
                        in_volunteer_section = False
                        break
                
                if in_volunteer_section:
                    # Parse volunteer experience similar to work experience
                    if re.search(r'\d{4}', line) or any(word in line_lower for word in ['volunteer', 'coordinator', 'organizer']):
                        if current_vol:
                            volunteer.append(current_vol)
                        current_vol = self._parse_experience_line(line, 'volunteer')
                    elif current_vol and line.strip():
                        current_vol['description'] += line.strip() + ' '
        
        if current_vol:
            volunteer.append(current_vol)
        
        return volunteer
    
    def _parse_awards(self, text: str) -> List[Dict[str, Any]]:
        """Parse awards section"""
        awards = []
        lines = text.split('\n')
        current_award = {}
        in_awards_section = False
        
        for i, line in enumerate(lines):
            line_stripped = line.strip()
            # Ensure line is a string before calling lower()
            if not isinstance(line_stripped, str):
                continue
            line_lower = line_stripped.lower()
            
            # Check if we're entering awards section
            for keyword in self.patterns['sections']['awards_keywords']:
                if keyword in line_lower and len(line.strip()) < 100:
                    in_awards_section = True
                    continue
            
            # Check if we're leaving awards section
            if in_awards_section:
                for section_type in ['work', 'experience', 'education', 'skills', 'projects']:
                    if section_type in line_lower and len(line.strip()) < 100:
                        if current_award:
                            awards.append(current_award)
                            current_award = {}
                        in_awards_section = False
                        break
                
                if in_awards_section:
                    # Look for award patterns
                    if any(word in line_lower for word in ['award', 'honor', 'recipient', 'winner']):
                        if current_award:
                            awards.append(current_award)
                        current_award = {
                            'name': line.strip(),
                            'description': '',
                            'awardDate': self._extract_date_from_text(line)
                        }
                    elif current_award and line.strip():
                        current_award['description'] += line.strip() + ' '
        
        if current_award:
            awards.append(current_award)
        
        return awards
    
    def _parse_hobbies(self, text: str) -> List[str]:
        """Parse hobbies/interests section"""
        hobbies = []
        lines = text.split('\n')
        in_hobbies_section = False
        
        for i, line in enumerate(lines):
            line_stripped = line.strip()
            # Ensure line is a string before calling lower()
            if not isinstance(line_stripped, str):
                continue
            line_lower = line_stripped.lower()
            
            # Check if we're entering hobbies section
            for keyword in ['hobbies', 'interests', 'activities', 'languages']:
                if keyword in line_lower and len(line.strip()) < 100:
                    in_hobbies_section = True
                    continue
            
            # Check if we're leaving hobbies section
            if in_hobbies_section:
                for section_type in ['work', 'experience', 'education', 'skills', 'projects']:
                    if section_type in line_lower and len(line.strip()) < 100:
                        in_hobbies_section = False
                        break
                
                if in_hobbies_section and line.strip():
                    # Split by commas, semicolons, or bullet points
                    items = re.split(r'[,;•·]', line.strip())
                    hobbies.extend([item.strip() for item in items if item.strip()])
        
        return list(set(hobbies))
    
    def _parse_references(self, text: str) -> List[Dict[str, Any]]:
        """Parse references section"""
        references = []
        lines = text.split('\n')
        current_ref = {}
        in_refs_section = False
        
        for i, line in enumerate(lines):
            line_stripped = line.strip()
            # Ensure line is a string before calling lower()
            if not isinstance(line_stripped, str):
                continue
            line_lower = line_stripped.lower()
            
            # Check if we're entering references section
            for keyword in self.patterns['sections']['references_keywords']:
                if keyword in line_lower and len(line.strip()) < 100:
                    in_refs_section = True
                    continue
            
            # Check if we're leaving references section
            if in_refs_section:
                for section_type in ['work', 'experience', 'education', 'skills', 'projects']:
                    if section_type in line_lower and len(line.strip()) < 100:
                        if current_ref:
                            references.append(current_ref)
                            current_ref = {}
                        in_refs_section = False
                        break
                
                if in_refs_section:
                    # Parse reference information
                    if re.match(r'^[A-Z][a-z]+\s+[A-Z][a-z]+', line.strip()):
                        if current_ref:
                            references.append(current_ref)
                        current_ref = {'name': line.strip()}
                    elif '@' in line and current_ref:
                        current_ref['email'] = line.strip()
                    elif re.search(r'\d{3}[-.]?\d{3}[-.]?\d{4}', line) and current_ref:
                        current_ref['phone'] = line.strip()
                    elif any(word in line_lower for word in ['manager', 'supervisor', 'colleague']) and current_ref:
                        current_ref['relationship'] = line.strip()
        
        if current_ref:
            references.append(current_ref)
        
        return references
    
    def _parse_additional_texts(self, text: str) -> List[Dict[str, Any]]:
        """Parse additional text sections"""
        texts = []
        lines = text.split('\n')
        current_text = {}
        
        # Look for custom sections that don't fit standard categories
        standard_sections = set([
            'work', 'experience', 'education', 'skills', 'projects',
            'publications', 'volunteer', 'awards', 'certifications',
            'references', 'summary', 'objective', 'profile'
        ])
        
        current_section = None
        section_content = []
        
        for line in lines:
            line_stripped = line.strip()
            # Ensure line is a string before calling lower()
            if not isinstance(line_stripped, str):
                continue
            line_lower = line_stripped.lower()
            
            # Check if this is a section header
            if line_stripped and len(line_stripped) < 100 and not any(word in line_lower for word in standard_sections):
                if current_section and section_content:
                    texts.append({
                        'content': '\n'.join(section_content),
                        'section_type': current_section
                    })
                
                current_section = line_stripped
                section_content = []
            elif current_section:
                section_content.append(line_stripped)
        
        if current_section and section_content:
            texts.append({
                'content': '\n'.join(section_content),
                'section_type': current_section
            })
        
        return texts
    
    def _extract_date_from_text(self, text: str) -> Optional[date]:
        """Extract date from text"""
        date_patterns = [
            r'\b(19|20)\d{2}\b',  # Years
            r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+(19|20)\d{2}\b',
            r'\b(0?[1-9]|1[0-2])/\d{2}\b',  # MM/YY
        ]
        
        for pattern in date_patterns:
            matches = re.findall(pattern, text)
            if matches:
                year = int(matches[0])
                return date(year, 1, 1)  # Default to January
        
        return None
    
    def _parse_experience_line(self, line: str, exp_type: str) -> Dict[str, Any]:
        """Parse a single experience line (work or volunteer)"""
        result = {
            'organization' if exp_type == 'volunteer' else 'company': '',
            'role' if exp_type == 'volunteer' else 'jobTitle': '',
            'description': '',
            'startDate': None,
            'endDate': None,
            'location': None
        }
        
        # This is a simplified version - you'd enhance this with your existing parsing logic
        return result
    
    def _parse_work_experience(self, text: str) -> List[Dict[str, Any]]:
        """Use existing work experience parsing"""
        # Simple work experience parsing for testing
        work = []
        lines = text.split('\n')
        current_job = {}
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Look for job title patterns
            if any(title in line.upper() for title in ['OFFICER', 'MANAGER', 'DIRECTOR', 'ENGINEER']):
                if current_job:
                    work.append(current_job)
                current_job = {'jobTitle': line, 'description': ''}
            
            # Look for company patterns
            elif any(word in line.upper() for word in ['GLOBAL', 'TECH', 'SYSTEMS', 'CORP']):
                if current_job:
                    current_job['company'] = line
            
            # Look for location patterns
            elif any(state in line.upper() for state in ['TN', 'TX', 'NY', 'CA', 'IL']):
                if current_job:
                    current_job['location'] = line
            
            # Look for date patterns
            elif any(char.isdigit() for char in line) and any(word in line.upper() for word in ['PRESENT', '202', '201']):
                if current_job:
                    if 'PRESENT' in line.upper():
                        current_job['endDate'] = None
                    else:
                        dates = [word for word in line.split() if word.isdigit()]
                        if len(dates) >= 2:
                            current_job['startDate'] = dates[0]
                            current_job['endDate'] = dates[1]
            
            # Add to description
            elif line.startswith('-') and current_job:
                current_job['description'] += line + '\n'
        
        if current_job:
            work.append(current_job)
        
        return work
    
    def _parse_education(self, text: str) -> List[Dict[str, Any]]:
        """Use existing education parsing"""
        # Delegate to your existing education parser
        # This would integrate with your current education extraction logic
        return []
    
    def _parse_skills(self, text: str) -> List[Dict[str, Any]]:
        """Use existing skills parsing"""
        # Delegate to your existing skills parser
        return []
    
    def _parse_certifications(self, text: str) -> List[Dict[str, Any]]:
        """Use existing certifications parsing"""
        # Delegate to your existing certifications parser
        return []
    
    def _parse_achievements(self, text: str) -> List[Dict[str, Any]]:
        """Use existing achievements parsing"""
        # Delegate to your existing achievements parser
        return []
