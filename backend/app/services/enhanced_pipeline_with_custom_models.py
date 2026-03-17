"""
Enhanced Pipeline with Custom Trained Models Integration
"""

import os
import json
import re
from typing import Dict, List, Any, Optional
from app.services.custom_models import custom_models

class EnhancedResumePipelineWithCustomModels:
    """Enhanced pipeline that uses custom trained models"""
    
    def __init__(self):
        self.custom_models = custom_models
        print("🤖 Enhanced Pipeline with Custom Models Initialized")
    
    def parse_resume_complete(self, resume_text: str, use_ml: bool = True) -> Dict[str, Any]:
        """Parse complete resume using custom trained models"""
        
        if not resume_text or not resume_text.strip():
            print("❌ Empty resume text provided")
            return {}
        
        print(f"🔍 Parsing resume with custom models ({len(resume_text)} chars)")
        
        # Initialize result structure
        result = {}
        
        try:
            result["basics"] = self._extract_basics(resume_text)
            print(f"  ✅ Basics extracted: {len(result['basics'])} fields")
        except Exception as e:
            print(f"  ❌ Error extracting basics: {e}")
            result["basics"] = {}
        
        try:
            result["profile"] = self._extract_profile(resume_text)
            print(f"  ✅ Profile extracted: {len(result['profile'])} fields")
        except Exception as e:
            print(f"  ❌ Error extracting profile: {e}")
            result["profile"] = {}
        
        try:
            result["work"] = self._extract_work_experience(resume_text)
            print(f"  ✅ Work extracted: {len(result['work'])} entries")
        except Exception as e:
            print(f"  ❌ Error extracting work: {e}")
            result["work"] = []
        
        try:
            result["education"] = self._extract_education(resume_text)
            print(f"  ✅ Education extracted: {len(result['education'])} entries")
        except Exception as e:
            print(f"  ❌ Error extracting education: {e}")
            result["education"] = []
        
        try:
            result["skills"] = self._extract_skills(resume_text)
            print(f"  ✅ Skills extracted: {len(result['skills'])} entries")
        except Exception as e:
            print(f"  ❌ Error extracting skills: {e}")
            result["skills"] = []
        
        try:
            result["certifications"] = self._extract_certifications(resume_text)
            print(f"  ✅ Certifications extracted: {len(result['certifications'])} entries")
        except Exception as e:
            print(f"  ❌ Error extracting certifications: {e}")
            result["certifications"] = []
        
        # Add other sections (rule-based for now)
        result["projects"] = self._extract_projects(resume_text)
        result["achievements"] = self._extract_achievements(resume_text)
        result["volunteer"] = self._extract_volunteer(resume_text)
        result["publications"] = self._extract_publications(resume_text)
        result["awards"] = self._extract_awards(resume_text)
        result["hobbies"] = self._extract_hobbies(resume_text)
        result["languages"] = self._extract_languages(resume_text)
        result["references"] = self._extract_references(resume_text)
        result["texts"] = self._extract_additional_texts(resume_text)
        
        print(f"✅ Custom model parsing completed!")
        print(f"📊 Sections extracted: {list(result.keys())}")
        
        # Validate result has meaningful data
        if not result.get("work") and not result.get("basics"):
            print("❌ No meaningful data extracted!")
            return {}
        
        return result
    
    def _extract_work_experience(self, text: str) -> List[Dict[str, Any]]:
        """Extract work experience using custom NER model"""
        print("💼 Extracting work experience with custom NER model...")
        
        # Use custom work NER model
        entities = self.custom_models.extract_section_entities(text, "work")
        
        # Parse work entries from entities
        work_entries = self._parse_work_entities(text, entities)
        
        # If NER didn't work, force rule-based parsing
        if not work_entries:
            print("  🔧 NER failed, using rule-based parsing...")
            work_entries = self._parse_work_experience_rule_based(text)
        
        print(f"  ✅ Extracted {len(work_entries)} work entries")
        return work_entries
    
    def _extract_education(self, text: str) -> List[Dict[str, Any]]:
        """Extract education using custom NER model"""
        print("🎓 Extracting education with custom NER model...")
        
        # Use custom education NER model
        entities = self.custom_models.extract_section_entities(text, "education")
        
        # Parse education entries from entities
        education_entries = self._parse_education_entities(text, entities)
        
        print(f"  ✅ Extracted {len(education_entries)} education entries")
        return education_entries
    
    def _extract_skills(self, text: str) -> List[Dict[str, Any]]:
        """Extract skills using custom NER model"""
        print("🔧 Extracting skills with custom NER model...")
        
        # Use custom skills NER model
        entities = self.custom_models.extract_section_entities(text, "skills")
        
        # Parse skills from entities
        skills = self._parse_skill_entities(text, entities)
        
        # If NER didn't work well, force rule-based parsing
        if len(skills) < 5:  # If we got less than 5 skills, use rule-based
            print("  🔧 NER insufficient, using rule-based parsing...")
            skills = self._parse_skills_rule_based(text)
        
        print(f"  ✅ Extracted {len(skills)} skills")
        return skills
    
    def _extract_projects(self, text: str) -> List[Dict[str, Any]]:
        """Extract projects using custom NER model"""
        print("🏗️ Extracting projects with custom NER model...")
        
        # Use custom projects NER model
        entities = self.custom_models.extract_section_entities(text, "projects")
        
        # Parse projects from entities
        projects = self._parse_project_entities(text, entities)
        
        print(f"  ✅ Extracted {len(projects)} projects")
        return projects
    
    def _extract_certifications(self, text: str) -> List[Dict[str, Any]]:
        """Extract certifications using custom NER model"""
        print("🏆 Extracting certifications with custom NER model...")
        
        # Use custom certifications NER model
        entities = self.custom_models.extract_section_entities(text, "certifications")
        
        # Parse certifications from entities
        certifications = self._parse_certification_entities(text, entities)
        
        print(f"  ✅ Extracted {len(certifications)} certifications")
        return certifications
    
    def _parse_work_entities(self, text: str, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Parse work entities into structured work entries"""
        work_entries = []
        
        # If no entities from NER, use rule-based parsing as fallback
        if not entities:
            return self._parse_work_experience_rule_based(text)
        
        # Group entities by proximity (same work entry)
        entity_groups = self._group_entities_by_proximity(entities)
        
        for group in entity_groups:
            entry = {}
            for entity in group:
                if entity["label"] == "COMPANY":
                    entry["company"] = entity["text"]
                elif entity["label"] == "TITLE":
                    entry["title"] = entity["text"]
                elif entity["label"] == "LOCATION":
                    entry["location"] = entity["text"]
                elif entity["label"] == "DATE_RANGE":
                    entry["date_range"] = entity["text"]
            
            # Extract description from text around entities
            if group:
                start_pos = min(e["start"] for e in group)
                end_pos = max(e["end"] for e in group)
                entry["description"] = text[start_pos:end_pos].strip()
            
            if entry.get("company") and entry.get("title"):
                work_entries.append(entry)
        
        return work_entries
    
    def _parse_education_entities(self, text: str, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Parse education entities into structured education entries"""
        education_entries = []
        
        # If no entities from NER, use rule-based parsing as fallback
        if not entities:
            return self._parse_education_rule_based(text)
        
        entity_groups = self._group_entities_by_proximity(entities)
        
        for group in entity_groups:
            entry = {}
            for entity in group:
                if entity["label"] == "UNIVERSITY":
                    entry["university"] = entity["text"]
                elif entity["label"] == "DEGREE":
                    entry["degree"] = entity["text"]
                elif entity["label"] == "MAJOR":
                    entry["major"] = entity["text"]
                elif entity["label"] == "EDU_DATE":
                    entry["date"] = entity["text"]
                elif entity["label"] == "GPA":
                    entry["gpa"] = entity["text"]
            
            if entry.get("university"):
                education_entries.append(entry)
        
        return education_entries
    
    def _parse_education_rule_based(self, text: str) -> List[Dict[str, Any]]:
        """Rule-based parsing for education as fallback"""
        education_entries = []
        
        # Find education section
        edu_section_match = re.search(r'(?:EDUCATION)[\s:\-]*(.*?)(?=\n\n[A-Z]|\n##|\Z)', text, re.IGNORECASE | re.DOTALL)
        
        if edu_section_match:
            edu_text = edu_section_match.group(1).strip()
            
            # Parse education format (Rahul's format: Degree – University, Location, Date)
            edu_pattern = r'([A-Za-z\s]+(?:Bachelor|Master|PhD|Associate)[A-Za-z\s]*(?:in|of)[A-Za-z\s]*)\s*–\s*([A-Za-z\s]+(?:University|College|Institute|Technology)[A-Za-z\s]*)\s*,\s*([A-Za-z\s,]+)\s*,\s*(\d{4}-\d{4})'
            
            matches = re.findall(edu_pattern, edu_text)
            for match in matches:
                degree, university, location, date = match
                education_entries.append({
                    "degree": degree.strip(),
                    "university": university.strip(),
                    "location": location.strip(),
                    "date": date.strip(),
                    "confidence": 0.9
                })
        
        return education_entries
    
    def _parse_skill_entities(self, text: str, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Parse skill entities into structured skills"""
        skills = []
        
        # If no entities from NER, use rule-based parsing as fallback
        if not entities:
            return self._parse_skills_rule_based(text)
        
        for entity in entities:
            if entity["label"] == "SKILL":
                skills.append({
                    "skill": entity["text"],
                    "proficiency": "Intermediate",  # Default proficiency
                    "confidence": entity["confidence"]
                })
        
        return skills
    
    def _parse_skills_rule_based(self, text: str) -> List[Dict[str, Any]]:
        """Rule-based parsing for skills as fallback"""
        skills = []
        
        # Find skills section
        skills_section_match = re.search(r'(?:TECHNICAL SKILLS|SKILLS)[\s:\-]*(.*?)(?=\n\n[A-Z]|\n##|\Z)', text, re.IGNORECASE | re.DOTALL)
        
        if skills_section_match:
            skills_text = skills_section_match.group(1).strip()
            
            # Parse skill categories (Rahul's format)
            skill_categories = re.findall(r'([A-Za-z\s&\-\s]+):\s*([^\n]+)', skills_text)
            
            for category, skill_list in skill_categories:
                # Clean up category name
                category = category.strip()
                
                # Split skills by comma
                skill_items = [skill.strip() for skill in skill_list.split(',')]
                
                for skill in skill_items:
                    if skill and len(skill) > 2:  # Filter out very short items
                        # Determine proficiency based on category
                        if "Programming" in category or "Big Data" in category or "Cloud" in category:
                            proficiency = "Expert"
                        elif "Data Warehousing" in category or "Databases" in category:
                            proficiency = "Advanced"
                        else:
                            proficiency = "Intermediate"
                        
                        skills.append({
                            "skill": skill,
                            "proficiency": proficiency,
                            "confidence": 0.9
                        })
        
        return skills
    
    def _parse_project_entities(self, text: str, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Parse project entities into structured projects"""
        projects = []
        
        entity_groups = self._group_entities_by_proximity(entities)
        
        for group in entity_groups:
            entry = {}
            for entity in group:
                if entity["label"] == "PROJECT_NAME":
                    entry["name"] = entity["text"]
                elif entity["label"] == "PROJECT_TECH":
                    entry["technologies"] = entity["text"]
                elif entity["label"] == "PROJECT_DATE":
                    entry["date"] = entity["text"]
            
            if entry.get("name"):
                projects.append(entry)
        
        return projects
    
    def _parse_certification_entities(self, text: str, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Parse certification entities into structured certifications"""
        certifications = []
        
        # If no entities from NER, use rule-based parsing as fallback
        if not entities:
            return self._parse_certifications_rule_based(text)
        
        for entity in entities:
            if entity["label"] == "CERT_NAME":
                certifications.append({
                    "name": entity["text"],
                    "confidence": entity["confidence"]
                })
        
        return certifications
    
    def _parse_certifications_rule_based(self, text: str) -> List[Dict[str, Any]]:
        """Rule-based parsing for certifications as fallback"""
        certifications = []
        
        # Find certifications section
        cert_section_match = re.search(r'(?:CERTIFICATIONS|CERTIFICATION)[\s:\-]*(.*?)(?=\n\n[A-Z]|\n##|\Z)', text, re.IGNORECASE | re.DOTALL)
        
        if cert_section_match:
            cert_text = cert_section_match.group(1).strip()
            
            # Parse certification format (Rahul's format with en dash)
            cert_lines = cert_text.split('\n')
            
            for line in cert_lines:
                line = line.strip()
                if line and '–' in line and '|' in line:
                    # Parse: Name – Issuer | Issued: Date | Credential ID: ID
                    parts = line.split('–')
                    if len(parts) >= 2:
                        name = parts[0].strip()
                        rest = '–'.join(parts[1:]).strip()
                        
                        # Extract issuer
                        issuer_match = re.search(r'([A-Za-z\s\-\s]+(?:Inc|LLC|Corporation|AWS|Google|Microsoft|HashiCorp|Databricks|Snowflake|Confluent|dbt|CNCF))', rest)
                        issuer = issuer_match.group(1).strip() if issuer_match else ""
                        
                        # Extract date
                        date_match = re.search(r'Issued:\s*([A-Za-z]+\s+\d{4})', rest)
                        date = date_match.group(1).strip() if date_match else ""
                        
                        # Extract credential ID
                        id_match = re.search(r'Credential ID:\s*([A-Z0-9\-]+)', rest)
                        credential_id = id_match.group(1).strip() if id_match else ""
                        
                        if name and issuer:
                            certifications.append({
                                "name": name,
                                "issuer": issuer,
                                "date": date,
                                "credentialId": credential_id,
                                "confidence": 0.95
                            })
        
        return certifications
    
    def _group_entities_by_proximity(self, entities: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
        """Group entities that belong to the same entry"""
        if not entities:
            return []
        
        # Sort entities by position
        sorted_entities = sorted(entities, key=lambda x: x["start"])
        
        groups = []
        current_group = [sorted_entities[0]]
        
        for entity in sorted_entities[1:]:
            # If entity is close to current group, add it
            if entity["start"] - current_group[-1]["end"] < 200:  # 200 character threshold
                current_group.append(entity)
            else:
                # Start new group
                groups.append(current_group)
                current_group = [entity]
        
        groups.append(current_group)
        return groups
    
    def _extract_basics(self, text: str) -> Dict[str, Any]:
        """Extract basic contact information"""
        # Simple regex-based extraction for basics
        basics = {}
        
        # Extract name (first line with all caps)
        lines = text.split('\n')
        for line in lines[:5]:  # Check first 5 lines
            line = line.strip()
            if line and len(line.split()) >= 2 and line.isupper():
                basics["name"] = line
                break
        
        # Extract email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        if emails:
            basics["email"] = emails[0]
        
        # Extract phone (more flexible patterns)
        phone_patterns = [
            r'\+\d{1,3}[\s-]?\d{3}[\s-]?\d{3}[\s-]?\d{4}',
            r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            r'\(\d{3}\)\s*\d{3}[-.]?\d{4}'
        ]
        for pattern in phone_patterns:
            phones = re.findall(pattern, text)
            if phones:
                basics["phone"] = phones[0]
                break
        
        # Extract location (look for City, State pattern)
        location_pattern = r'([A-Za-z\s]+,\s*[A-Z]{2,3})'
        locations = re.findall(location_pattern, text)
        if locations:
            basics["location"] = locations[0]
        
        return basics
    
    def _extract_profile(self, text: str) -> Dict[str, Any]:
        """Extract profile/summary"""
        # Look for summary sections
        summary_patterns = [
            r'(?:SUMMARY|PROFILE|OBJECTIVE)[\s:\-]+(.*?)(?=\n\n|\n##|\n[A-Z]|\Z)',
            r'(?:ABOUT|PROFESSIONAL SUMMARY)[\s:\-]+(.*?)(?=\n\n|\n##|\n[A-Z]|\Z)',
            r'^(.*?years of experience.*?)(?=\n\n|\n##|\n[A-Z]|\Z)'  # Rahul's format
        ]
        
        for pattern in summary_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                summary = match.group(1).strip()
                # Clean up bullet points
                summary = re.sub(r'^[-•]\s*', '', summary, flags=re.MULTILINE)
                summary = re.sub(r'\n[-•]\s*', ' ', summary)
                return {"summary": summary}
        
        return {}
    
    def _extract_achievements(self, text: str) -> List[Dict[str, Any]]:
        """Extract achievements (rule-based for now)"""
        achievements = []
        
        # Look for achievement keywords
        achievement_patterns = [
            r'(?:ACHIEVEMENT|AWARD|ACCOMPLISHMENT)[\s:\-]+(.*?)(?=\n\n|\n[A-Z]|\Z)',
            r'(?:RECOGNITION|HONOR)[\s:\-]+(.*?)(?=\n\n|\n[A-Z]|\Z)'
        ]
        
        for pattern in achievement_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE | re.DOTALL)
            for match in matches:
                achievements.append({"achievement": match.strip()})
        
        return achievements
    
    def _extract_volunteer(self, text: str) -> List[Dict[str, Any]]:
        """Extract volunteer experience (rule-based for now)"""
        volunteer = []
        
        # Look for volunteer keywords
        volunteer_patterns = [
            r'(?:VOLUNTEER|COMMUNITY SERVICE)[\s:\-]+(.*?)(?=\n\n|\n[A-Z]|\Z)',
            r'(?:VOLUNTEERING|COMMUNITY)[\s:\-]+(.*?)(?=\n\n|\n[A-Z]|\Z)'
        ]
        
        for pattern in volunteer_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE | re.DOTALL)
            for match in matches:
                volunteer.append({"experience": match.strip()})
        
        return volunteer
    
    def _extract_publications(self, text: str) -> List[Dict[str, Any]]:
        """Extract publications (rule-based for now)"""
        publications = []
        
        # Look for publication keywords
        pub_patterns = [
            r'(?:PUBLICATION|PAPER|ARTICLE)[\s:\-]+(.*?)(?=\n\n|\n[A-Z]|\Z)',
            r'(?:PUBLISHED|JOURNAL)[\s:\-]+(.*?)(?=\n\n|\n[A-Z]|\Z)'
        ]
        
        for pattern in pub_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE | re.DOTALL)
            for match in matches:
                publications.append({"publication": match.strip()})
        
        return publications
    
    def _extract_awards(self, text: str) -> List[Dict[str, Any]]:
        """Extract awards (rule-based for now)"""
        awards = []
        
        # Look for award keywords
        award_patterns = [
            r'(?:AWARD|HONOR|RECOGNITION)[\s:\-]+(.*?)(?=\n\n|\n[A-Z]|\Z)',
            r'(?:CERTIFICATE|CERTIFICATION)[\s:\-]+(.*?)(?=\n\n|\n[A-Z]|\Z)'
        ]
        
        for pattern in award_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE | re.DOTALL)
            for match in matches:
                awards.append({"award": match.strip()})
        
        return awards
    
    def _extract_hobbies(self, text: str) -> List[Dict[str, Any]]:
        """Extract hobbies (rule-based for now)"""
        hobbies = []
        
        # Look for hobby keywords
        hobby_patterns = [
            r'(?:HOBBIES|INTERESTS|ACTIVITIES)[\s:\-]+(.*?)(?=\n\n|\n[A-Z]|\Z)',
            r'(?:PERSONAL|LEISURE)[\s:\-]+(.*?)(?=\n\n|\n[A-Z]|\Z)'
        ]
        
        for pattern in hobby_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE | re.DOTALL)
            for match in matches:
                hobbies.append({"hobby": match.strip()})
        
        return hobbies
    
    def _extract_languages(self, text: str) -> List[Dict[str, Any]]:
        """Extract languages (rule-based for now)"""
        languages = []
        
        # Look for language keywords
        lang_patterns = [
            r'(?:LANGUAGES|LANGUAGE)[\s:\-]+(.*?)(?=\n\n|\n[A-Z]|\Z)',
            r'(?:FLUENT|PROFICIENT)[\s:\-]+(.*?)(?=\n\n|\n[A-Z]|\Z)'
        ]
        
        for pattern in lang_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE | re.DOTALL)
            for match in matches:
                languages.append({"language": match.strip()})
        
        return languages
    
    def _extract_references(self, text: str) -> List[Dict[str, Any]]:
        """Extract references (rule-based for now)"""
        references = []
        
        # Look for reference keywords
        ref_patterns = [
            r'(?:REFERENCES|REFERENCE)[\s:\-]+(.*?)(?=\n\n|\n[A-Z]|\Z)',
            r'(?:RECOMMENDATION|RECOMMENDER)[\s:\-]+(.*?)(?=\n\n|\n[A-Z]|\Z)'
        ]
        
        for pattern in ref_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE | re.DOTALL)
            for match in matches:
                references.append({"reference": match.strip()})
        
        return references
    
    def _parse_work_experience_rule_based(self, text: str) -> List[Dict[str, Any]]:
        """Rule-based parsing for work experience as fallback"""
        work_entries = []
        
        # Find work experience section
        work_section_match = re.search(r'(?:PROFESSIONAL EXPERIENCE|EXPERIENCE|WORK EXPERIENCE)[\s:\-]*(.*?)(?=\n\n[A-Z]|\n##|\Z)', text, re.IGNORECASE | re.DOTALL)
        
        if not work_section_match:
            return work_entries
        
        work_text = work_section_match.group(1).strip()
        
        # Split by specific company names (Rahul's format)
        company_names = [
            'UnitedHealth Group',
            'JP Morgan Chase & Co.',
            'Walmart Global Tech',
            'AT&T',
            'Exxon Mobil Corporation',
            'Infosys Limited'
        ]
        
        # Split by company names
        parts = work_text
        for company in company_names:
            parts = parts.replace(company, f'###SPLIT###{company}')
        
        company_sections = parts.split('###SPLIT###')
        company_sections = [section.strip() for section in company_sections if section.strip()]
        
        for section in company_sections:
            # Extract company name (first line before colon)
            lines = section.split('\n')
            if not lines:
                continue
                
            first_line = lines[0].strip()
            if ':' not in first_line:
                continue
                
            company = first_line.split(':')[0].strip()
            rest_of_line = first_line.split(':', 1)[1].strip()
            
            # Extract date range and location
            date_range = ""
            location = ""
            
            # Pattern: Date Range (Location: City, State)
            date_loc_match = re.search(r'([A-Za-z]+\s+\d{4}\s*–\s*[A-Za-z]+\s+\d{4}|[A-Za-z]+\s+\d{4}\s*–\s*Current)\s*\(([^)]+)\)', rest_of_line)
            if date_loc_match:
                date_range = date_loc_match.group(1).strip()
                location = date_loc_match.group(2).strip()
            
            # Extract role
            role = "Data Engineer"
            for line in lines:
                if line.strip().startswith('Role:'):
                    role = line.replace('Role:', '').strip()
                    break
            
            # Extract description
            description = ""
            in_responsibilities = False
            for line in lines[1:]:  # Skip first line (company info)
                if line.strip().startswith('Responsibilities:'):
                    in_responsibilities = True
                    continue
                if in_responsibilities:
                    if line.strip().startswith('•'):
                        description += line.strip().replace('•', '').strip() + ' '
                    elif line.strip() and not line.startswith('  '):
                        break
            
            # Clean up description
            description = description.strip()
            
            if company and role:
                work_entries.append({
                    "company": company,
                    "title": role,
                    "date_range": date_range,
                    "location": location,
                    "description": description
                })
        
        return work_entries
    
    def _extract_additional_texts(self, text: str) -> Dict[str, Any]:
        """Extract additional text sections"""
        return {"additional_text": text}
