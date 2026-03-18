"""
Backward Compatibility Adapter for ML Models
Converts new JSON format to legacy format expected by existing ML models
"""

from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)


class LegacyFormatAdapter:
    """
    Adapter that converts new JSON format back to legacy format
    Ensures ML models continue working without modifications
    """
    
    def __init__(self):
        self.reverse_mapping = {
            # Contact reverse mappings
            "basics": "contact",
            "firstName": "firstName",
            "lastName": "lastName",
            "email": "emails",
            "phone": "phones",
            
            # Experience reverse mappings
            "experience": "work_experience",
            "jobTitle": "title",
            "startDate": "start_date",
            "endDate": "end_date",
            
            # Other reverse mappings
            "skills": "skills",
            "education": "education",
            "certifications": "certifications"
        }
    
    def convert_to_legacy_format(self, new_format_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert new JSON format back to legacy format for ML models
        """
        try:
            legacy_data = {}
            
            # Convert contact back to legacy format
            if "basics" in new_format_data:
                legacy_data["contact"] = self._convert_contact_to_legacy(new_format_data["basics"])
            
            # Convert experience back to legacy format
            if "experience" in new_format_data:
                legacy_data["work_experience"] = self._convert_experience_to_legacy(new_format_data["experience"])
            
            # Keep skills as-is (structure is compatible)
            if "skills" in new_format_data:
                legacy_data["skills"] = new_format_data["skills"]
            
            # Keep education as-is (structure is compatible)
            if "education" in new_format_data:
                legacy_data["education"] = new_format_data["education"]
            
            # Keep certifications as-is (structure is compatible)
            if "certifications" in new_format_data:
                legacy_data["certifications"] = new_format_data["certifications"]
            
            # Preserve debug info
            if "debug" in new_format_data:
                legacy_data["debug"] = new_format_data["debug"]
            
            logger.info("Successfully converted to legacy format for ML models")
            return legacy_data
            
        except Exception as e:
            logger.error(f"Error converting to legacy format: {e}")
            # Fallback to original data
            return new_format_data
    
    def _convert_contact_to_legacy(self, basics: Dict[str, Any]) -> Dict[str, Any]:
        """Convert new basics format back to legacy contact format"""
        if not basics:
            return {}
        
        legacy_contact = {}
        
        # Convert name back to legacy format
        first_name = basics.get("firstName", "")
        last_name = basics.get("lastName", "")
        full_name = f"{first_name} {last_name}".strip()
        
        legacy_contact["name"] = {
            "name": full_name,
            "confidence": 1.0
        }
        
        # Convert emails back to legacy format
        emails = basics.get("email", [])
        legacy_contact["emails"] = [{"email": email, "confidence": 1.0} for email in emails]
        
        # Convert phones back to legacy format
        phones = basics.get("phone", [])
        legacy_contact["phones"] = [{"phone": phone, "confidence": 1.0} for phone in phones]
        
        # Convert location back to legacy format
        city = basics.get("city", "")
        country = basics.get("country", "")
        legacy_contact["location"] = {
            "city": city,
            "country": country
        }
        
        # Convert URLs back to legacy format
        web = basics.get("web", [])
        if web:
            legacy_contact["urls"] = {}
            for url in web:
                if "linkedin.com" in url:
                    legacy_contact["urls"]["linkedin"] = url
                elif "github.com" in url:
                    legacy_contact["urls"]["github"] = url
        
        return legacy_contact
    
    def _convert_experience_to_legacy(self, experience: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert new experience format back to legacy format"""
        if not experience:
            return []
        
        legacy_experience = []
        for exp in experience:
            legacy_exp = {
                "title": exp.get("jobTitle", ""),
                "company": exp.get("company", ""),
                "description": exp.get("description", ""),
                "start_date": exp.get("startDate"),
                "end_date": exp.get("endDate"),
                "location": exp.get("location", "")
            }
            
            # Add client if available
            if exp.get("client"):
                legacy_exp["client"] = exp.get("client")
            
            legacy_experience.append(legacy_exp)
        
        return legacy_experience


# Global adapter instance
legacy_adapter = LegacyFormatAdapter()


def get_legacy_format_for_ml(new_format_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get legacy format data for ML models
    Use this function wherever ML models expect the old format
    """
    return legacy_adapter.convert_to_legacy_format(new_format_data)
