"""
Prompt Engineering Improvements for Resume Parser
Optimized prompts for Experience and Education extraction with strict JSON output
"""

import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import re

logger = logging.getLogger(__name__)


class PromptTemplates:
    """
    Optimized prompt templates for resume parsing with strict JSON output enforcement.
    """
    
    # EXPERIENCE EXTRACTION PROMPTS
    EXPERIENCE_EXTRACTION_V1 = """
You are an expert resume parser specializing in work experience extraction. Your task is to extract structured work experience information from the provided resume section.

STRICT RULES:
1. Extract ALL work experiences in the order they appear
2. For each experience, extract ONLY these fields: company, job_title, start_date, end_date, description, location
3. Dates MUST be in MM/YYYY format (e.g., "01/2020", "06/2019")
4. If end_date is "present", "current", or ongoing, use "12/2024" (current date)
5. Return ONLY valid JSON - no explanations, no markdown, no extra text
6. If a field cannot be found, use empty string "" instead of null
7. Description should be a single string with newlines as \\n
8. Company and job_title are REQUIRED - never use empty string for these

INPUT TEXT:
{experience_section}

OUTPUT FORMAT (copy this structure exactly):
{{
    "work_experience": [
        {{
            "company": "Exact company name from resume",
            "job_title": "Exact job title from resume", 
            "start_date": "MM/YYYY",
            "end_date": "MM/YYYY",
            "description": "Full description with \\n for line breaks",
            "location": "City, State or Country if available"
        }}
    ]
}}

Extract the work experience now:
"""

    EXPERIENCE_EXTRACTION_V2 = """
You are a precision resume parser. Extract structured work experience data from the resume text below.

EXTRACTION REQUIREMENTS:
- Extract each distinct work experience entry
- Parse company names exactly as written
- Parse job titles exactly as written  
- Convert dates to standard MM/YYYY format
- Include location information if present
- Preserve description text with proper formatting

DATE NORMALIZATION:
- "Jan 2020" → "01/2020"
- "January 2020" → "01/2020"
- "2020" → "01/2020" (assume start of year)
- "present" → "12/2024"
- "current" → "12/2024"
- "till date" → "12/2024"

JSON SCHEMA:
{{
    "work_experience": [
        {{
            "company": "string (required)",
            "job_title": "string (required)", 
            "start_date": "MM/YYYY (required)",
            "end_date": "MM/YYYY (required)",
            "description": "string (use \\n for line breaks)",
            "location": "string (optional)"
        }}
    ]
}}

RESUME TEXT:
{experience_section}

JSON OUTPUT:
"""

    # EDUCATION EXTRACTION PROMPTS
    EDUCATION_EXTRACTION_V1 = """
You are an expert resume parser specializing in education extraction. Extract structured education information from the provided resume section.

STRICT RULES:
1. Extract ALL education entries in the order they appear
2. For each entry, extract: institution, degree, field_of_study, start_date, end_date, gpa, location
3. Dates MUST be in MM/YYYY format
4. Identify degree type: Bachelor's, Master's, PhD, Associate, Diploma, Certificate
5. Return ONLY valid JSON - no explanations, no markdown
6. Use empty string "" for missing optional fields
7. Institution and degree are REQUIRED fields

INPUT TEXT:
{education_section}

OUTPUT FORMAT:
{{
    "education": [
        {{
            "institution": "University/School name",
            "degree": "Degree type (Bachelor's, Master's, etc.)",
            "field_of_study": "Major/concentration",
            "start_date": "MM/YYYY",
            "end_date": "MM/YYYY",
            "gpa": "GPA if available",
            "location": "City, State or Country"
        }}
    ]
}}

Extract the education information now:
"""

    EDUCATION_EXTRACTION_V2 = """
You are a precision education parser. Extract structured academic information from the resume text below.

EXTRACTION REQUIREMENTS:
- Extract each distinct education entry
- Identify institution names accurately
- Parse degree types (Bachelor's, Master's, PhD, etc.)
- Extract field of study/major
- Normalize dates to MM/YYYY format
- Include GPA if available
- Include location if present

DEGREE TYPE DETECTION:
- "B.S.", "BS", "Bachelor" → "Bachelor's"
- "M.S.", "MS", "Master" → "Master's" 
- "PhD", "Ph.D", "Doctorate" → "PhD"
- "Associate", "A.A.", "A.S." → "Associate"

JSON SCHEMA:
{{
    "education": [
        {{
            "institution": "string (required)",
            "degree": "string (required)",
            "field_of_study": "string (optional)",
            "start_date": "MM/YYYY (optional)",
            "end_date": "MM/YYYY (optional)",
            "gpa": "string (optional)",
            "location": "string (optional)"
        }}
    ]
}}

RESUME TEXT:
{education_section}

JSON OUTPUT:
"""

    # SKILLS EXTRACTION PROMPTS
    SKILLS_EXTRACTION_V1 = """
You are an expert skills parser. Extract technical and professional skills from the resume text below.

STRICT RULES:
1. Extract individual skills as a flat list
2. Separate technical skills from soft skills if possible
3. Remove duplicates
4. Return ONLY valid JSON array
5. Each skill should be a concise, recognizable skill name

INPUT TEXT:
{skills_section}

OUTPUT FORMAT:
{{
    "skills": ["Skill 1", "Skill 2", "Skill 3"]
}}

Extract the skills now:
"""

    # CONTACT INFORMATION EXTRACTION
    CONTACT_EXTRACTION_V1 = """
You are a contact information parser. Extract contact details from the resume text below.

STRICT RULES:
1. Extract: name, email, phone, linkedin_url, github_url, location
2. Validate email format
3. Normalize phone numbers to standard format
4. Return ONLY valid JSON
5. Use empty string "" for missing fields

INPUT TEXT:
{contact_section}

OUTPUT FORMAT:
{{
    "name": "Full Name",
    "email": "email@example.com",
    "phone": "+1-555-123-4567",
    "linkedin_url": "https://linkedin.com/in/username",
    "github_url": "https://github.com/username",
    "location": "City, State"
}}

Extract contact information now:
"""


class PromptEngineer:
    """
    Advanced prompt engineering system with validation, retry mechanisms,
    and fallback strategies for resume parsing.
    """
    
    def __init__(self):
        """Initialize prompt engineer."""
        self.prompt_versions = {
            'experience': ['v1', 'v2'],
            'education': ['v1', 'v2'],
            'skills': ['v1'],
            'contact': ['v1']
        }
        self.current_versions = {
            'experience': 'v2',  # Start with best version
            'education': 'v2',
            'skills': 'v1',
            'contact': 'v1'
        }
        self.success_rates = {}  # Track success rates by prompt version
        
    def get_prompt(self, extraction_type: str, text: str, version: str = None) -> str:
        """
        Get optimized prompt for specific extraction type.
        
        Args:
            extraction_type: Type of extraction ('experience', 'education', 'skills', 'contact')
            text: Input text to process
            version: Specific prompt version (uses default if not specified)
            
        Returns:
            Formatted prompt string
        """
        version = version or self.current_versions.get(extraction_type, 'v1')
        
        prompt_key = f"{extraction_type.upper()}_EXTRACTION_{version.upper()}"
        template = getattr(PromptTemplates, prompt_key, None)
        
        if not template:
            logger.warning(f"Prompt template not found: {prompt_key}, using v1 fallback")
            prompt_key = f"{extraction_type.upper()}_EXTRACTION_V1"
            template = getattr(PromptTemplates, prompt_key, PromptTemplates.EXPERIENCE_EXTRACTION_V1)
        
        # Format the prompt with input text
        try:
            formatted_prompt = template.format(**{f"{extraction_type}_section": text})
            return formatted_prompt
        except KeyError as e:
            logger.error(f"Prompt formatting error: {e}")
            return template.format(experience_section=text)  # Fallback
            
    def validate_json_response(self, response: str, expected_structure: Dict[str, Any]) -> tuple[bool, Any]:
        """
        Validate JSON response against expected structure.
        
        Args:
            response: Raw response string
            expected_structure: Expected JSON structure
            
        Returns:
            Tuple of (is_valid, parsed_json or error_message)
        """
        try:
            # Try to parse JSON
            parsed_json = json.loads(response)
            
            # Validate structure
            validation_result = self._validate_structure(parsed_json, expected_structure)
            
            if validation_result['is_valid']:
                return True, parsed_json
            else:
                return False, validation_result['error']
                
        except json.JSONDecodeError as e:
            return False, f"JSON parsing error: {str(e)}"
        except Exception as e:
            return False, f"Validation error: {str(e)}"
            
    def _validate_structure(self, data: Any, expected_structure: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate data structure against expected format.
        
        Args:
            data: Parsed JSON data
            expected_structure: Expected structure
            
        Returns:
            Validation result
        """
        if not isinstance(data, dict):
            return {
                'is_valid': False,
                'error': f"Expected dict, got {type(data).__name__}"
            }
            
        for key, expected_type in expected_structure.items():
            if key not in data:
                return {
                    'is_valid': False,
                    'error': f"Missing required key: {key}"
                }
                
            if expected_type == 'array' and not isinstance(data[key], list):
                return {
                    'is_valid': False,
                    'error': f"Key '{key}' should be array, got {type(data[key]).__name__}"
                }
                
            elif expected_type == 'string' and not isinstance(data[key], str):
                return {
                    'is_valid': False,
                    'error': f"Key '{key}' should be string, got {type(data[key]).__name__}"
                }
                
        return {'is_valid': True, 'error': None}
        
    def retry_with_fallback(
        self, 
        extraction_type: str, 
        text: str, 
        llm_function,
        max_retries: int = 3,
        expected_structure: Dict[str, Any] = None
    ) -> tuple[bool, Any, str]:
        """
        Retry extraction with fallback prompt versions.
        
        Args:
            extraction_type: Type of extraction
            text: Input text
            llm_function: Function to call LLM
            max_retries: Maximum retry attempts
            expected_structure: Expected JSON structure
            
        Returns:
            Tuple of (success, result, prompt_version_used)
        """
        expected_structure = expected_structure or {'work_experience': 'array'}
        
        versions = self.prompt_versions.get(extraction_type, ['v1'])
        
        for attempt in range(max_retries):
            for version in versions:
                try:
                    prompt = self.get_prompt(extraction_type, text, version)
                    response = llm_function(prompt)
                    
                    is_valid, result = self.validate_json_response(response, expected_structure)
                    
                    if is_valid:
                        # Update success rates
                        self._update_success_rate(extraction_type, version, True)
                        return True, result, version
                        
                except Exception as e:
                    logger.warning(f"Attempt {attempt + 1} with version {version} failed: {e}")
                    self._update_success_rate(extraction_type, version, False)
                    
        return False, None, "all_failed"
        
    def _update_success_rate(self, extraction_type: str, version: str, success: bool):
        """Update success rate tracking for prompt versions."""
        key = f"{extraction_type}_{version}"
        if key not in self.success_rates:
            self.success_rates[key] = {'success': 0, 'total': 0}
            
        self.success_rates[key]['total'] += 1
        if success:
            self.success_rates[key]['success'] += 1
            
    def get_best_version(self, extraction_type: str) -> str:
        """
        Get the best performing prompt version for an extraction type.
        
        Args:
            extraction_type: Type of extraction
            
        Returns:
            Best version name
        """
        versions = self.prompt_versions.get(extraction_type, ['v1'])
        best_version = versions[0]
        best_rate = 0.0
        
        for version in versions:
            key = f"{extraction_type}_{version}"
            if key in self.success_rates:
                stats = self.success_rates[key]
                rate = stats['success'] / stats['total'] if stats['total'] > 0 else 0.0
                if rate > best_rate:
                    best_rate = rate
                    best_version = version
                    
        return best_version
        
    def optimize_prompt(self, extraction_type: str, training_data: List[Dict[str, Any]]):
        """
        Analyze training data to suggest prompt improvements.
        
        Args:
            extraction_type: Type of extraction
            training_data: Training examples with inputs and expected outputs
        """
        logger.info(f"🔍 Analyzing training data for {extraction_type} prompt optimization...")
        
        # Analyze common patterns
        common_errors = self._analyze_common_errors(training_data)
        missing_fields = self._analyze_missing_fields(training_data)
        format_issues = self._analyze_format_issues(training_data)
        
        optimization_suggestions = {
            'common_errors': common_errors,
            'missing_fields': missing_fields,
            'format_issues': format_issues,
            'suggestions': self._generate_suggestions(common_errors, missing_fields, format_issues)
        }
        
        logger.info(f"📊 Optimization analysis complete: {optimization_suggestions}")
        return optimization_suggestions
        
    def _analyze_common_errors(self, training_data: List[Dict[str, Any]]) -> List[str]:
        """Analyze common errors in training data."""
        errors = []
        
        for example in training_data:
            if 'error' in example:
                errors.append(example['error'])
                
        # Return most common errors
        from collections import Counter
        error_counts = Counter(errors)
        return [error for error, count in error_counts.most_common(5)]
        
    def _analyze_missing_fields(self, training_data: List[Dict[str, Any]]) -> Dict[str, int]:
        """Analyze which fields are commonly missing."""
        field_counts = {}
        
        for example in training_data:
            if 'output' in example and isinstance(example['output'], dict):
                for field in example['output'].keys():
                    if field not in field_counts:
                        field_counts[field] = 0
                    if not example['output'][field]:  # Empty or None
                        field_counts[field] += 1
                        
        return field_counts
        
    def _analyze_format_issues(self, training_data: List[Dict[str, Any]]) -> List[str]:
        """Analyze common format issues."""
        issues = []
        
        for example in training_data:
            if 'output' in example:
                output = example['output']
                
                # Check date formats
                if 'work_experience' in output:
                    for exp in output['work_experience']:
                        if 'start_date' in exp:
                            if not re.match(r'^(0[1-9]|1[0-2])/\d{4}$', exp['start_date']):
                                issues.append(f"Invalid date format: {exp['start_date']}")
                                
        return list(set(issues))[:10]  # Return unique issues
        
    def _generate_suggestions(
        self, 
        common_errors: List[str], 
        missing_fields: Dict[str, int], 
        format_issues: List[str]
    ) -> List[str]:
        """Generate optimization suggestions."""
        suggestions = []
        
        if common_errors:
            suggestions.append("Address common errors: " + ", ".join(common_errors[:3]))
            
        if missing_fields:
            most_missing = max(missing_fields.items(), key=lambda x: x[1])
            suggestions.append(f"Improve extraction for field: {most_missing[0]}")
            
        if format_issues:
            suggestions.append("Fix format issues: " + ", ".join(format_issues[:3]))
            
        return suggestions


class JSONPostProcessor:
    """
    Post-processes JSON output to fix common issues and ensure data quality.
    """
    
    @staticmethod
    def fix_dates(date_str: str) -> str:
        """
        Fix and normalize date strings.
        
        Args:
            date_str: Input date string
            
        Returns:
            Normalized date in MM/YYYY format
        """
        if not date_str:
            return ""
            
        date_str = date_str.strip().lower()
        
        # Handle "present", "current", etc.
        if date_str in ['present', 'current', 'ongoing', 'till date', 'to date']:
            current_year = datetime.now().year
            return f"12/{current_year}"
            
        # Try various date formats
        date_patterns = [
            (r'(\d{1,2})/(\d{4})', r'\1/\2'),  # MM/YYYY
            (r'(\d{4})', r'01/\1'),            # YYYY → MM/YYYY
            (r'([a-z]+)\s+(\d{4})', ''),       # Month YYYY
        ]
        
        for pattern, replacement in date_patterns:
            match = re.match(pattern, date_str)
            if match:
                if pattern == r'([a-z]+)\s+(\d{4})':
                    # Convert month name to number
                    month_map = {
                        'january': '01', 'february': '02', 'march': '03', 'april': '04',
                        'may': '05', 'june': '06', 'july': '07', 'august': '08',
                        'september': '09', 'october': '10', 'november': '11', 'december': '12'
                    }
                    month_name = match.group(1)
                    year = match.group(2)
                    month_num = month_map.get(month_name, '01')
                    return f"{month_num}/{year}"
                else:
                    return re.sub(pattern, replacement, date_str)
                    
        return date_str  # Return original if no pattern matched
        
    @staticmethod
    def clean_text(text: str) -> str:
        """
        Clean and normalize text fields.
        
        Args:
            text: Input text
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
            
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters that might be errors
        text = re.sub(r'[<>{}|\\^~[\]]', '', text)
        
        # Trim whitespace
        text = text.strip()
        
        return text
        
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format."""
        if not email:
            return False
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
        
    @staticmethod
    def validate_phone(phone: str) -> str:
        """Normalize phone number format."""
        if not phone:
            return ""
            
        # Remove all non-numeric characters except + and -
        phone = re.sub(r'[^\d\+\-]', '', phone)
        
        return phone
        
    @staticmethod
    def post_process_json(json_data: Dict[str, Any], extraction_type: str) -> Dict[str, Any]:
        """
        Apply post-processing to JSON data based on extraction type.
        
        Args:
            json_data: Raw JSON data
            extraction_type: Type of extraction performed
            
        Returns:
            Post-processed JSON data
        """
        if extraction_type == 'experience':
            if 'work_experience' in json_data:
                for exp in json_data['work_experience']:
                    if 'start_date' in exp:
                        exp['start_date'] = JSONPostProcessor.fix_dates(exp['start_date'])
                    if 'end_date' in exp:
                        exp['end_date'] = JSONPostProcessor.fix_dates(exp['end_date'])
                    if 'description' in exp:
                        exp['description'] = JSONPostProcessor.clean_text(exp['description'])
                        
        elif extraction_type == 'education':
            if 'education' in json_data:
                for edu in json_data['education']:
                    if 'start_date' in edu:
                        edu['start_date'] = JSONPostProcessor.fix_dates(edu['start_date'])
                    if 'end_date' in edu:
                        edu['end_date'] = JSONPostProcessor.fix_dates(edu['end_date'])
                        
        elif extraction_type == 'contact':
            if 'email' in json_data:
                if not JSONPostProcessor.validate_email(json_data['email']):
                    json_data['email'] = ""  # Clear invalid email
            if 'phone' in json_data:
                json_data['phone'] = JSONPostProcessor.validate_phone(json_data['phone'])
                
        return json_data