"""
API Response Handler for New JSON Format
Provides backward compatibility and dual mode support
"""

from typing import Dict, Any, Optional
from fastapi import HTTPException
from app.services.legacy_format_adapter import get_legacy_format_for_ml
import logging

logger = logging.getLogger(__name__)


class APIResponseHandler:
    """
    Handles API responses for both new and legacy JSON formats
    Ensures backward compatibility while supporting new format
    """
    
    def __init__(self):
        self.dual_mode = True  # Support both formats during transition
        self.default_format = "new"  # Default to new format
    
    def format_response(self, data: Dict[str, Any], format_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Format API response based on requested format type
        """
        try:
            requested_format = format_type or self.default_format
            
            if requested_format == "legacy":
                # Return legacy format for ML models
                return get_legacy_format_for_ml(data)
            
            elif requested_format == "new":
                # Return new format as-is
                return data
            
            elif self.dual_mode:
                # Dual mode: return both formats
                return {
                    "new_format": data,
                    "legacy_format": get_legacy_format_for_ml(data),
                    "format_info": {
                        "default": self.default_format,
                        "supported": ["new", "legacy", "dual"],
                        "recommended": "new"
                    }
                }
            
            else:
                # Default to new format
                return data
                
        except Exception as e:
            logger.error(f"Error formatting API response: {e}")
            raise HTTPException(status_code=500, detail="Internal server error during response formatting")
    
    def extract_parsed_data_for_api(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract and format parsed data for API responses
        """
        try:
            parsed_data = job_data.get("parsed_data", {})
            
            if not parsed_data:
                return {"error": "No parsed data found"}
            
            # Check if data is in new format
            if "basics" in parsed_data or "experience" in parsed_data:
                # New format detected
                return self.format_response(parsed_data, "new")
            
            # Check if data is in legacy format
            elif "contact" in parsed_data or "work_experience" in parsed_data:
                # Legacy format detected - convert to new
                new_format_data = self._convert_legacy_to_new_format(parsed_data)
                return self.format_response(new_format_data, "new")
            
            else:
                # Unknown format - return as-is
                return self.format_response(parsed_data, "new")
                
        except Exception as e:
            logger.error(f"Error extracting parsed data for API: {e}")
            return {"error": "Failed to extract parsed data"}
    
    def _convert_legacy_to_new_format(self, legacy_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert legacy format to new format for API responses
        This is a lightweight conversion for API layer only
        """
        try:
            new_format = {}
            
            # Convert contact to basics
            if "contact" in legacy_data:
                contact = legacy_data.get("contact", {})
                new_format["basics"] = {
                    "firstName": contact.get("name", {}).get("name", "").split()[0] if contact.get("name") else "",
                    "lastName": " ".join(contact.get("name", {}).get("name", "").split()[1:]) if len(contact.get("name", {}).get("name", "").split()) > 1 else "",
                    "email": [email.get("email", "") for email in contact.get("emails", []) if email.get("email")],
                    "phone": [phone.get("phone", "") for phone in contact.get("phones", []) if phone.get("phone")],
                    "city": contact.get("location", {}).get("city", ""),
                    "country": contact.get("location", {}).get("country", "")
                }
            
            # Convert work_experience to experience
            if "work_experience" in legacy_data:
                work_experience = legacy_data.get("work_experience", [])
                new_format["experience"] = []
                for job in work_experience:
                    exp_entry = {
                        "jobTitle": job.get("title", ""),
                        "company": job.get("company", ""),
                        "location": job.get("location", ""),
                        "startDate": job.get("start_date"),
                        "endDate": job.get("end_date"),
                        "description": job.get("description", "")
                    }
                    new_format["experience"].append(exp_entry)
            
            # Copy other fields as-is
            for key in ["skills", "education", "certifications", "projects", "debug"]:
                if key in legacy_data:
                    new_format[key] = legacy_data[key]
            
            # Add metadata
            new_format["metadata"] = {
                "format_version": "2.0",
                "converted_from": "legacy",
                "generated_at": "api_response_time"
            }
            
            return new_format
            
        except Exception as e:
            logger.error(f"Error converting legacy to new format: {e}")
            return legacy_data  # Fallback to original
    
    def get_format_info(self) -> Dict[str, Any]:
        """
        Get format information for API documentation
        """
        return {
            "supported_formats": ["new", "legacy", "dual"],
            "default_format": self.default_format,
            "dual_mode": self.dual_mode,
            "field_mappings": {
                "new": {
                    "contact": "basics",
                    "work_experience": "experience",
                    "skills": "skills",
                    "education": "education",
                    "certifications": "certifications"
                },
                "legacy": {
                    "basics": "contact",
                    "experience": "work_experience",
                    "skills": "skills",
                    "education": "education",
                    "certifications": "certifications"
                }
            },
            "migration_status": {
                "phase": "active",
                "breaking_changes": False,
                "backward_compatible": True
            }
        }


# Global response handler instance
api_response_handler = APIResponseHandler()


def format_candidate_response(data: Dict[str, Any], format_type: Optional[str] = None) -> Dict[str, Any]:
    """
    Format candidate data for API responses
    """
    return api_response_handler.format_response(data, format_type)


def extract_candidate_parsed_data(job_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract and format candidate parsed data for API responses
    """
    return api_response_handler.extract_parsed_data_for_api(job_data)
