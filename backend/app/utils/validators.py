"""
Custom validators for the Resume Parser API.

This module contains reusable validation functions and Pydantic validators
for common validation scenarios including phone numbers, years of experience,
education levels, file uploads, and more.
"""

import re
import logging
from datetime import date
from typing import Optional
from uuid import UUID
from pydantic import (
    BaseModel,
    field_validator,
    model_validator,
    ValidationInfo,
    ConfigDict,
)
from pydantic_core import PydanticCustomError

logger = logging.getLogger(__name__)


# ==================== Phone Number Validation ====================

class PhoneNumberValidator:
    """Validator for phone numbers with international format support."""
    
    # Regex for international phone numbers (simplified but practical)
    PHONE_REGEX = re.compile(
        r'^\+?(\d{1,3})?[-. ]?(\(?\d{3}\)?[-. ]?)?\d{3}[-. ]?\d{4}$'
    )
    
    @classmethod
    def validate(cls, phone: Optional[str]) -> Optional[str]:
        """
        Validate phone number format.
        
        Args:
            phone: Phone number string to validate
            
        Returns:
            Validated phone number or None if empty
            
        Raises:
            ValueError: If phone number format is invalid
        """
        if phone is None or phone.strip() == "":
            return None
            
        phone = phone.strip()
        
        if not cls.PHONE_REGEX.match(phone):
            logger.warning(f"Invalid phone number format: {phone}")
            raise ValueError(
                "Invalid phone number format. "
                "Expected format: +1-XXX-XXX-XXXX or (XXX) XXX-XXXX"
            )
        
        return phone


# ==================== Years of Experience Validation ====================

class ExperienceValidator:
    """Validator for years of experience fields."""
    
    @classmethod
    def validate_years(cls, years: Optional[float]) -> Optional[float]:
        """
        Validate years of experience.
        
        Args:
            years: Years of experience to validate
            
        Returns:
            Validated years or None if empty
            
        Raises:
            ValueError: If years is negative or exceeds reasonable limit
        """
        if years is None:
            return None
            
        if years < 0:
            logger.warning(f"Negative years of experience: {years}")
            raise ValueError("Years of experience cannot be negative")
            
        if years > 50:
            logger.warning(f"Unreasonably high years of experience: {years}")
            raise ValueError("Years of experience cannot exceed 50 years")
            
        return round(years, 1)


# ==================== Education Level Validation ====================

class EducationValidator:
    """Validator for education-related fields."""
    
    VALID_DEGREES = [
        "High School", "GED", "Associate", "Bachelor", "Master", 
        "PhD", "Doctorate", "MBA", "JD", "MD", "Other"
    ]
    
    @classmethod
    def validate_gpa(cls, gpa: Optional[float]) -> Optional[float]:
        """
        Validate GPA field.
        
        Args:
            gpa: GPA to validate
            
        Returns:
            Validated GPA or None if empty
            
        Raises:
            ValueError: If GPA is out of valid range
        """
        if gpa is None:
            return None
            
        if gpa < 0 or gpa > 4.0:
            logger.warning(f"Invalid GPA: {gpa}")
            raise ValueError("GPA must be between 0.0 and 4.0")
            
        return round(gpa, 2)
    
    @classmethod
    def validate_degree(cls, degree: Optional[str]) -> Optional[str]:
        """
        Validate degree field against known degree types.
        
        Args:
            degree: Degree to validate
            
        Returns:
            Validated degree or None if empty
            
        Raises:
            ValueError: If degree is not recognized
        """
        if degree is None or degree.strip() == "":
            return None
            
        degree = degree.strip()
        
        # Check if degree contains any valid degree name
        degree_lower = degree.lower()
        for valid_degree in cls.VALID_DEGREES:
            if valid_degree.lower() in degree_lower:
                return degree
        
        # Allow custom degrees but log warning
        logger.warning(f"Unrecognized degree type: {degree}")
        return degree


# ==================== Date Range Validation ====================

class DateRangeValidator:
    """Validator for date ranges (start_date < end_date)."""
    
    @classmethod
    def validate_date_range(
        cls, 
        start_date: Optional[date], 
        end_date: Optional[date],
        field_name: str = "date range"
    ) -> tuple[Optional[date], Optional[date]]:
        """
        Validate that start_date is before end_date.
        
        Args:
            start_date: Start date
            end_date: End date
            field_name: Name of the field for error messages
            
        Returns:
            Tuple of (start_date, end_date)
            
        Raises:
            ValueError: If start_date is after end_date
        """
        if start_date and end_date:
            if start_date > end_date:
                logger.warning(
                    f"Invalid {field_name}: start_date {start_date} > end_date {end_date}"
                )
                raise ValueError(
                    f"{field_name}: start_date must be before or equal to end_date"
                )
        
        return start_date, end_date


# ==================== URL Validation ====================

class URLValidator:
    """Validator for URL fields (LinkedIn, GitHub, etc.)."""
    
    URL_REGEX = re.compile(
        r'^https?://'  # http or https
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain
        r'localhost|'  # localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # IP
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE
    )
    
    @classmethod
    def validate_url(cls, url: Optional[str]) -> Optional[str]:
        """
        Validate URL format.
        
        Args:
            url: URL to validate
            
        Returns:
            Validated URL or None if empty
            
        Raises:
            ValueError: If URL format is invalid
        """
        if url is None or url.strip() == "":
            return None
            
        url = url.strip()
        
        if not cls.URL_REGEX.match(url):
            logger.warning(f"Invalid URL format: {url}")
            raise ValueError("Invalid URL format. Must start with http:// or https://")
        
        return url


# ==================== Skills Validation ====================

class SkillsValidator:
    """Validator for skills-related fields."""
    
    @classmethod
    def validate_skills_not_empty(cls, skills: list) -> list:
        """
        Validate that skills list is not empty when required.
        
        Args:
            skills: List of skills to validate
            
        Returns:
            Validated skills list
            
        Raises:
            ValueError: If skills list is empty
        """
        if not skills:
            logger.warning("Empty skills list provided")
            raise ValueError("Skills list cannot be empty")
        
        return skills
    
    @classmethod
    def validate_skill_name(cls, name: str) -> str:
        """
        Validate skill name format.
        
        Args:
            name: Skill name to validate
            
        Returns:
            Validated skill name
            
        Raises:
            ValueError: If skill name is invalid
        """
        if not name or not name.strip():
            raise ValueError("Skill name cannot be empty")
        
        name = name.strip()
        
        if len(name) < 2:
            raise ValueError("Skill name must be at least 2 characters long")
        
        if len(name) > 150:
            raise ValueError("Skill name cannot exceed 150 characters")
        
        return name


# ==================== Confidence Score Validation ====================

class ConfidenceValidator:
    """Validator for confidence score fields."""
    
    @classmethod
    def validate_confidence(cls, score: Optional[float]) -> Optional[float]:
        """
        Validate confidence score (0.0 to 1.0).
        
        Args:
            score: Confidence score to validate
            
        Returns:
            Validated confidence score or None if empty
            
        Raises:
            ValueError: If score is out of valid range
        """
        if score is None:
            return None
        
        if score < 0.0 or score > 1.0:
            logger.warning(f"Invalid confidence score: {score}")
            raise ValueError("Confidence score must be between 0.0 and 1.0")
        
        return round(score, 4)


# ==================== Pydantic Base Classes with Validators ====================

class ValidatedCandidateBase(BaseModel):
    """Base model for candidate-related schemas with built-in validators."""
    
    @field_validator('phone', check_fields=False)
    @classmethod
    def validate_phone_number(cls, v: Optional[str]) -> Optional[str]:
        """Validate phone number format."""
        return PhoneNumberValidator.validate(v)
    
    @field_validator('years_experience', check_fields=False)
    @classmethod
    def validate_years_of_experience(cls, v: Optional[float]) -> Optional[float]:
        """Validate years of experience."""
        return ExperienceValidator.validate_years(v)
    
    @field_validator('linkedin_url', 'github_url', check_fields=False)
    @classmethod
    def validate_urls(cls, v: Optional[str]) -> Optional[str]:
        """Validate URL formats."""
        return URLValidator.validate_url(v)


class ValidatedEducationBase(BaseModel):
    """Base model for education-related schemas with built-in validators."""
    
    @field_validator('gpa', check_fields=False)
    @classmethod
    def validate_gpa_score(cls, v: Optional[float]) -> Optional[float]:
        """Validate GPA score."""
        return EducationValidator.validate_gpa(v)
    
    @field_validator('degree', check_fields=False)
    @classmethod
    def validate_degree_type(cls, v: Optional[str]) -> Optional[str]:
        """Validate degree type."""
        return EducationValidator.validate_degree(v)
    
    @model_validator(mode='after')
    def validate_date_range(self) -> 'ValidatedEducationBase':
        """Validate that start_date is before end_date."""
        DateRangeValidator.validate_date_range(
            self.start_date, 
            self.end_date,
            "education period"
        )
        return self


class ValidatedWorkHistoryBase(BaseModel):
    """Base model for work history schemas with built-in validators."""
    
    @model_validator(mode='after')
    def validate_date_range(self) -> 'ValidatedWorkHistoryBase':
        """Validate that start_date is before end_date."""
        DateRangeValidator.validate_date_range(
            self.start_date,
            self.end_date,
            "employment period"
        )
        return self


class ValidatedSkillBase(BaseModel):
    """Base model for skill-related schemas with built-in validators."""
    
    @field_validator('name', check_fields=False)
    @classmethod
    def validate_skill_name(cls, v: str) -> str:
        """Validate skill name."""
        return SkillsValidator.validate_skill_name(v)


class ValidatedParsingJobBase(BaseModel):
    """Base model for parsing job schemas with built-in validators."""
    
    @field_validator('confidence_score', 'ocr_confidence', check_fields=False)
    @classmethod
    def validate_confidence_scores(cls, v: Optional[float]) -> Optional[float]:
        """Validate confidence scores."""
        return ConfidenceValidator.validate_confidence(v)
