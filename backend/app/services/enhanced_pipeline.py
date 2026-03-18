# Enhanced Pipeline Integration for Complete Resume JSON

from typing import Dict, Any, Optional
from app.services.ml_complete_parser import MLResumeParser
from app.services.complete_resume_converter import convert_resume_to_target_format
from app.services.parser.quality_classifier import quality_classifier
from app.services.parser.tfidf_vectorizer import tfidf_vectorizer

class EnhancedResumePipeline:
    """
    Enhanced Pipeline that produces complete target JSON format
    """
    
    def __init__(self):
        self.ml_parser = MLResumeParser()
        # Initialize quality classifier and TF-IDF vectorizer
        print("✅ Quality classifier loaded")
        print("✅ TF-IDF vectorizer loaded")
    
    def parse_resume_complete(self, resume_text: str, use_ml: bool = True) -> Dict[str, Any]:
        """
        Parse resume into complete target JSON format
        
        Args:
            resume_text: Raw resume text
            use_ml: Whether to use ML models (LayoutLM, BERT, spaCy)
        
        Returns:
            Complete resume JSON in target format
        """
        
        if use_ml:
            # Step 1: ML-Powered Parsing
            parsed_data = self.ml_parser.parse_complete_resume(resume_text)
        else:
            # Step 2: Fallback to existing parsers
            parsed_data = self._parse_with_existing_methods(resume_text)
        
        # Step 3: Convert to target JSON format
        target_json = convert_resume_to_target_format(parsed_data)
        
        # Step 4: Validate and clean
        validated_json = self._validate_and_clean(target_json)
        
        return validated_json
    
    def _parse_with_existing_methods(self, resume_text: str) -> Dict[str, Any]:
        """
        Fallback parsing using existing methods
        """
        from app.services.llm_service import LLMParsingService
        
        # Use existing parsers for sections that are already implemented
        llm_service = LLMParsingService()
        
        parsed_data = {
            "work": llm_service.extract_work_experience_details(resume_text),
            "education": [],  # Use existing education parser
            "skills": [],     # Use existing skills parser
            "certifications": [],  # Use existing certifications parser
            "achievements": [],    # Use existing achievements parser
            "basics": self._extract_basic_info(resume_text),
            "profile": self._extract_profile(resume_text),
            "projects": [],
            "volunteer": [],
            "publications": [],
            "awards": [],
            "hobbies": [],
            "references": [],
            "texts": []
        }
        
        return parsed_data
    
    def _extract_basic_info(self, text: str) -> Dict[str, Any]:
        """Extract basic info using simple patterns"""
        import re
        
        basics = {}
        
        # Email
        emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
        if emails:
            basics['email'] = list(set(emails))
        
        # Phone
        phones = re.findall(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', text)
        if phones:
            basics['phone'] = list(set(phones))
        
        # LinkedIn
        linkedin = re.findall(r'linkedin\.com/in/[\w-]+', text)
        if linkedin:
            basics['web'] = linkedin
        
        # Name (simple extraction)
        lines = text.split('\n')[:5]  # Check first few lines
        for line in lines:
            if re.match(r'^[A-Z][a-z]+\s+[A-Z][a-z]+$', line.strip()):
                name_parts = line.strip().split()
                if len(name_parts) >= 2:
                    basics['firstName'] = name_parts[0]
                    basics['lastName'] = ' '.join(name_parts[1:])
                break
        
        return basics
    
    def _extract_profile(self, text: str) -> Optional[str]:
        """Extract professional summary"""
        lines = text.split('\n')
        profile_lines = []
        
        profile_keywords = ['summary', 'objective', 'profile', 'about']
        
        for i, line in enumerate(lines):
            line_lower = line.strip().lower()
            if any(keyword in line_lower for keyword in profile_keywords):
                # Collect next few lines as profile
                j = i + 1
                while j < len(lines) and j < i + 6:  # Max 5 lines
                    next_line = lines[j].strip()
                    if next_line and not any(keyword in next_line.lower() for keyword in ['experience', 'education', 'skills']):
                        profile_lines.append(next_line)
                    j += 1
                break
        
        return '\n'.join(profile_lines) if profile_lines else None
    
    def _validate_and_clean(self, json_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and clean the JSON data
        """
        cleaned = json_data.copy()
        
        # Remove empty sections
        for key, value in cleaned.items():
            if value in [None, [], {}, ''] or (isinstance(value, list) and all(not item for item in value)):
                cleaned[key] = None
        
        # Validate required fields
        if cleaned.get('basics'):
            basics = cleaned['basics']
            if not basics.get('firstName') and not basics.get('lastName'):
                # Try to extract from full_name
                if basics.get('full_name'):
                    name_parts = basics['full_name'].split()
                    if len(name_parts) >= 2:
                        basics['firstName'] = name_parts[0]
                        basics['lastName'] = ' '.join(name_parts[1:])
        
        # Clean up work experience
        if cleaned.get('work'):
            cleaned['work'] = [
                job for job in cleaned['work'] 
                if job.get('jobTitle') or job.get('company')
            ]
        
        # Ensure proper date formatting
        cleaned = self._format_all_dates(cleaned)
        
        return cleaned
    
    def _format_all_dates(self, json_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format all dates consistently
        """
        def format_date_section(section_data):
            if isinstance(section_data, list):
                for item in section_data:
                    if isinstance(item, dict):
                        for key, value in item.items():
                            if 'date' in key.lower() and value:
                                item[key] = self._format_single_date(value)
            return section_data
        
        # Apply to all date-containing sections
        date_sections = ['work', 'education', 'projects', 'volunteer', 'certifications', 'publications', 'awards']
        
        for section in date_sections:
            if json_data.get(section):
                json_data[section] = format_date_section(json_data[section])
        
        return json_data
    
    def _format_single_date(self, date_value: Any) -> str:
        """
        Format a single date value
        """
        if not date_value:
            return None
        
        if isinstance(date_value, str):
            # Try to standardize
            if len(date_value) == 4:  # Year only
                return date_value
            # Add more date formatting logic as needed
            return date_value
        
        return str(date_value)

# Integration with existing pipeline
def integrate_complete_parser():
    """
    Integration function to add complete parser to existing pipeline
    """
    # This would be called from your main pipeline
    enhanced_pipeline = EnhancedResumePipeline()
    return enhanced_pipeline
