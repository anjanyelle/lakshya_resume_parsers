"""
Unified JSON Adapter - Uses ALL Datasets Simultaneously
Converts unified parsing results to existing JSON format
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from app.services.parser.enhanced_normalizer import unified_normalizer
from app.services.parser.hybrid_work_experience_parser import unified_parser, UnifiedJobEntry

logger = logging.getLogger(__name__)

class UnifiedJSONAdapter:
    """
    Unified JSON adapter that ensures enhanced parsing results
    conform exactly to the existing JSON structure while using ALL datasets.
    
    This maintains 100% backward compatibility while leveraging all unified datasets.
    """
    
    def __init__(self):
        self.normalizer = unified_normalizer
        self.unified_parser = unified_parser
        
        logger.info("Unified JSON Adapter initialized")
        logger.info("Using ALL unified datasets for JSON adaptation")
    
    def adapt_work_experience(self, unified_entries: List[UnifiedJobEntry]) -> List[Dict[str, Any]]:
        """
        Convert UnifiedJobEntry objects to standard work experience format
        using ALL unified datasets without priority.
        """
        adapted_entries = []
        
        for entry in unified_entries:
            # Create standard work experience entry
            adapted_entry = {
                "jobTitle": entry.title or "",
                "company": entry.company or "",
                "location": entry.location or "",
                "startDate": entry.start_date or "",
                "endDate": entry.end_date or "",
                "description": entry.description or ""
            }
            
            # Only include non-empty fields to match existing behavior
            filtered_entry = {k: v for k, v in adapted_entry.items() if v is not None and v != ""}
            
            if filtered_entry:  # Only add if there's actual data
                adapted_entries.append(filtered_entry)
                
                # Log all sources used for debugging
                sources_used = entry.sources_used or ['unknown']
                logger.debug(f"Adapted entry using sources: {sources_used} - {entry.company} - {entry.title}")
                
                # Log additional metadata
                if entry.pattern_matched:
                    logger.debug(f"Pattern used: {entry.pattern_matched}")
                if entry.ner_entities_found:
                    logger.debug(f"NER entities: {entry.ner_entities_found}")
        
        return adapted_entries
    
    def adapt_education(self, education_data: List[Dict]) -> List[Dict[str, Any]]:
        """
        Adapt education data to standard format using ALL unified datasets
        """
        adapted_education = []
        
        for edu in education_data:
            if not isinstance(edu, dict):
                continue
            
            # Apply unified normalization using ALL datasets
            institution = edu.get("institution", "")
            degree = edu.get("degree", "")
            
            if institution:
                normalized_institution, normalized_degree = self.normalizer.normalize_education(institution, degree)
                
                adapted_entry = {
                    "institution": normalized_institution,
                    "degree": normalized_degree or degree,
                    "graduationYear": edu.get("graduationYear", ""),
                    "fieldOfStudy": edu.get("fieldOfStudy", "") or edu.get("field_of_study", ""),
                    "startDate": edu.get("startDate", "") or edu.get("start_date", ""),
                    "endDate": edu.get("endDate", "") or edu.get("end_date", ""),
                    "gpa": edu.get("gpa", "")
                }
                
                # Only include non-empty fields
                filtered_entry = {k: v for k, v in adapted_entry.items() if v is not None and v != ""}
                
                if filtered_entry:
                    adapted_education.append(filtered_entry)
        
        return adapted_education
    
    def adapt_skills(self, skills_data: List[Dict]) -> List[Dict[str, Any]]:
        """
        Adapt skills data using ALL unified datasets
        """
        adapted_skills = []
        
        for skill in skills_data:
            if not isinstance(skill, dict):
                continue
            
            skill_name = skill.get("name", "") or skill.get("skill", "")
            if not skill_name:
                continue
            
            # Apply unified normalization using ALL datasets
            normalized_name = self.normalizer.normalize_skill(skill_name)
            
            adapted_entry = {
                "name": normalized_name,
                "category": skill.get("category", ""),
                "confidence": skill.get("confidence", 0.0),
                "proficiency": skill.get("proficiency"),
                "yearsExperience": skill.get("yearsExperience") or skill.get("years_experience"),
                "version": skill.get("version")
            }
            
            # Only include non-empty fields
            filtered_entry = {k: v for k, v in adapted_entry.items() if v is not None and v != ""}
            
            if filtered_entry:
                adapted_skills.append(filtered_entry)
        
        return adapted_skills
    
    def adapt_certifications(self, cert_data: List[Dict]) -> List[Dict[str, Any]]:
        """
        Adapt certifications data using ALL unified datasets
        """
        adapted_certs = []
        
        for cert in cert_data:
            if not isinstance(cert, dict):
                continue
            
            cert_name = cert.get("name", "")
            if not cert_name:
                continue
            
            # Apply unified normalization using ALL datasets
            normalized_name = self.normalizer.normalize_certification(cert_name)
            
            adapted_entry = {
                "name": normalized_name,
                "issuing_organization": cert.get("issuing_organization", "") or cert.get("issuer", ""),
                "issue_date": cert.get("issue_date", "") or cert.get("issueDate", ""),
                "expiry_date": cert.get("expiry_date", "") or cert.get("expiryDate", ""),
                "credential_id": cert.get("credential_id", "") or cert.get("credentialId", ""),
                "is_active": cert.get("is_active", "") or cert.get("isActive", ""),
                "confidence": cert.get("confidence", 0.0)
            }
            
            # Only include non-empty fields
            filtered_entry = {k: v for k, v in adapted_entry.items() if v is not None and v != ""}
            
            if filtered_entry:
                adapted_certs.append(filtered_entry)
        
        return adapted_certs
    
    def adapt_contact(self, contact_data: Dict) -> Dict[str, Any]:
        """
        Adapt contact data to standard format using ALL unified datasets
        """
        if not isinstance(contact_data, dict):
            return {}
        
        adapted_contact = {}
        
        # Handle name
        name_obj = contact_data.get("name", {})
        if isinstance(name_obj, dict):
            name_text = name_obj.get("name", "")
        else:
            name_text = str(name_obj) if name_obj else ""
        
        if name_text:
            # Parse name into first and last
            name_parts = name_text.strip().split()
            if len(name_parts) >= 2:
                adapted_contact["firstName"] = name_parts[0].strip()
                adapted_contact["lastName"] = " ".join(name_parts[1:]).strip()
            elif len(name_parts) == 1:
                adapted_contact["firstName"] = name_parts[0].strip()
                adapted_contact["lastName"] = ""
        
        # Handle emails
        emails = contact_data.get("emails", [])
        if isinstance(emails, list):
            adapted_contact["emails"] = [
                email.get("email", "") if isinstance(email, dict) else str(email)
                for email in emails if email
            ]
        elif isinstance(emails, str):
            adapted_contact["emails"] = [emails]
        
        # Handle phones
        phones = contact_data.get("phones", [])
        if isinstance(phones, list):
            adapted_contact["phones"] = [
                phone.get("phone", "") if isinstance(phone, dict) else str(phone)
                for phone in phones if phone
            ]
        elif isinstance(phones, str):
            adapted_contact["phones"] = [phones]
        
        # Handle location with unified normalization
        location = contact_data.get("location", {})
        if isinstance(location, dict):
            city = location.get("city", "")
            state = location.get("state", "") or location.get("region", "")
            country = location.get("country", "")
            
            # Apply unified location normalization
            if city:
                normalized_city = self.normalizer.normalize_location(city)
                adapted_contact["location"] = {
                    "city": normalized_city,
                    "state": state,
                    "country": country
                }
            else:
                adapted_contact["location"] = {
                    "city": "",
                    "state": state,
                    "country": country
                }
        elif isinstance(location, str):
            # Parse and normalize string location
            normalized_location = self.normalizer.normalize_location(location)
            if "," in normalized_location:
                parts = normalized_location.split(",", 1)
                adapted_contact["location"] = {
                    "city": parts[0].strip(),
                    "state": parts[1].strip() if len(parts) > 1 else "",
                    "country": ""
                }
            else:
                adapted_contact["location"] = {
                    "city": normalized_location,
                    "state": "",
                    "country": ""
                }
        
        # Handle URLs
        urls = contact_data.get("urls", {})
        if isinstance(urls, dict):
            adapted_contact["urls"] = {
                "linkedin": urls.get("linkedin", ""),
                "github": urls.get("github", ""),
                "websites": urls.get("websites", [])
            }
        
        # Only include non-empty fields
        return {k: v for k, v in adapted_contact.items() if v is not None and v != "" and v != []}
    
    def enhance_parsing_with_all_datasets(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main adapter method that enhances parsing using ALL unified datasets
        while maintaining exact JSON structure compatibility.
        """
        logger.info("Applying enhanced parsing with ALL unified datasets")
        
        enhanced_data = parsed_data.copy()
        
        # Enhance work experience using unified parser (ALL datasets)
        experience_text = ""
        sections = parsed_data.get("sections", {})
        if isinstance(sections, dict) and "experience" in sections:
            experience_text = sections["experience"].get("content", "")
        
        if experience_text:
            try:
                # Use unified parser with ALL datasets
                unified_entries = self.unified_parser.parse_experience_section(experience_text)
                adapted_work = self.adapt_work_experience(unified_entries)
                
                if adapted_work:
                    enhanced_data["work_experience"] = adapted_work
                    logger.info(f"Enhanced work experience: {len(adapted_work)} entries")
                    
                    # Log all source usage
                    source_counts = {}
                    for entry in unified_entries:
                        for source in entry.sources_used or []:
                            source_counts[source] = source_counts.get(source, 0) + 1
                    logger.info(f"All sources used: {source_counts}")
                
            except Exception as e:
                logger.warning(f"Unified work experience parsing failed: {e}")
                # Fall back to existing data
                pass
        
        # Enhance education with ALL unified datasets
        if "education" in parsed_data:
            enhanced_education = self.adapt_education(parsed_data["education"])
            if enhanced_education:
                enhanced_data["education"] = enhanced_education
                logger.info(f"Enhanced education: {len(enhanced_education)} entries")
        
        # Enhance skills with ALL unified datasets
        if "skills" in parsed_data:
            enhanced_skills = self.adapt_skills(parsed_data["skills"])
            if enhanced_skills:
                enhanced_data["skills"] = enhanced_skills
                logger.info(f"Enhanced skills: {len(enhanced_skills)} entries")
        
        # Enhance certifications with ALL unified datasets
        if "certifications" in parsed_data:
            enhanced_certs = self.adapt_certifications(parsed_data["certifications"])
            if enhanced_certs:
                enhanced_data["certifications"] = enhanced_certs
                logger.info(f"Enhanced certifications: {len(enhanced_certs)} entries")
        
        # Adapt contact to basics format with unified datasets
        if "contact" in parsed_data:
            adapted_contact = self.adapt_contact(parsed_data["contact"])
            if adapted_contact:
                enhanced_data["basics"] = adapted_contact
                logger.info("Enhanced contact information with unified datasets")
        
        # Add unified enhancement metadata (for debugging)
        enhancement_stats = {
            "enhanced_at": datetime.utcnow().isoformat(),
            "enhancement_type": "unified_all_datasets",
            "datasets_used": "ALL",
            "unified_parsing_stats": self.unified_parser.get_unified_parsing_stats(),
            "unified_normalization_stats": self.normalizer.get_unified_normalization_stats()
        }
        
        # Add to metadata without breaking existing structure
        if "metadata" not in enhanced_data:
            enhanced_data["metadata"] = {}
        
        enhanced_data["metadata"]["unified_enhancement_info"] = enhancement_stats
        
        logger.info("Enhanced parsing with ALL datasets completed successfully")
        return enhanced_data
    
    def validate_json_structure(self, data: Dict[str, Any]) -> bool:
        """
        Validate that the enhanced data maintains the expected JSON structure
        """
        required_top_level_keys = {
            "basics", "work_experience", "education", "skills", 
            "certifications", "sections", "metadata"
        }
        
        present_keys = set(data.keys())
        missing_keys = required_top_level_keys - present_keys
        
        if missing_keys:
            logger.warning(f"Missing required keys in JSON structure: {missing_keys}")
            return False
        
        # Validate basics structure
        if "basics" in data and data["basics"]:
            basics_fields = {"firstName", "lastName", "emails", "phones", "location"}
            basics_keys = set(data["basics"].keys())
            if not basics_fields & basics_keys:  # At least some basics fields should be present
                logger.warning("Invalid basics structure")
                return False
        
        # Validate work experience structure
        if "work_experience" in data and data["work_experience"]:
            for i, job in enumerate(data["work_experience"][:3]):  # Check first 3 entries
                if not isinstance(job, dict):
                    logger.warning(f"Invalid work experience entry at index {i}")
                    return False
        
        logger.info("JSON structure validation passed")
        return True

# Global instance
unified_json_adapter = UnifiedJSONAdapter()
