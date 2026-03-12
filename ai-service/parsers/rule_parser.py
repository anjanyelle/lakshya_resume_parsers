"""
Rule-based personal information extractor for resume parsing.
Uses regex patterns and specialized libraries for accurate data extraction.
"""

import re
import logging
from typing import List, Dict, Optional, Union
from datetime import datetime
import phonenumbers
from phonenumbers import NumberParseException
import dateparser
from dateparser import DateDataParser

# Configure logging
logger = logging.getLogger(__name__)


class RuleBasedParser:
    """
    Comprehensive rule-based parser for extracting personal information from resume text.
    Supports emails, phone numbers, social profiles, websites, dates, and skills extraction.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Initialize date parser with common configurations
        self.date_parser = DateDataParser(
            languages=['en'],
            settings={
                'PREFER_DATES_FROM': 'past',
                'DATE_ORDER': 'MDY',
                'RELATIVE_BASE': datetime.now()
            }
        )
        
        # Pre-compiled regex patterns for better performance
        self._compile_patterns()
    
    def _compile_patterns(self):
        """Pre-compile regex patterns for better performance."""
        
        # Email pattern with internationalized domain support
        self.email_pattern = re.compile(
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b',
            re.IGNORECASE
        )
        
        # LinkedIn URL pattern
        self.linkedin_pattern = re.compile(
            r'(?:https?://)?(?:www\.)?linkedin\.com/in/([a-zA-Z0-9-]+)',
            re.IGNORECASE
        )
        
        # GitHub URL pattern
        self.github_pattern = re.compile(
            r'(?:https?://)?(?:www\.)?github\.com/([a-zA-Z0-9-]+)',
            re.IGNORECASE
        )
        
        # General website URL pattern
        self.website_pattern = re.compile(
            r'(?:https?://)?(?:www\.)?[a-zA-Z0-9-]+\.[a-zA-Z]{2,}(?:/[^\s]*)?',
            re.IGNORECASE
        )
        
        # Years of experience pattern
        self.experience_pattern = re.compile(
            r'(\d+(?:\.\d+)?)(?:\+|\s*-\s*\d+)?\s*(?:years?|yrs?)\s*(?:of\s*)?(?:experience|exp)?',
            re.IGNORECASE
        )
    
    def extract_email(self, text: str) -> Optional[str]:
        """
        Extract email address from text using regex pattern.
        
        Args:
            text: Input text to search for email
            
        Returns:
            First email found or None
        """
        try:
            matches = self.email_pattern.findall(text)
            if matches:
                email = matches[0].lower().strip()
                self.logger.debug(f"Found email: {email}")
                return email
            return None
        except Exception as e:
            self.logger.error(f"Error extracting email: {e}")
            return None
    
    def extract_phone(self, text: str) -> Optional[str]:
        """
        Extract phone number using phonenumbers library for international detection.
        Supports US, UK, India, Australia formats.
        
        Args:
            text: Input text to search for phone numbers
            
        Returns:
            E.164 formatted phone number or None
        """
        try:
            # Common countries to try
            country_codes = ['US', 'GB', 'IN', 'AU']
            
            for country_code in country_codes:
                try:
                    # Find all phone numbers in the text
                    for match in phonenumbers.PhoneNumberMatcher(text, country_code):
                        phone_number = match.number
                        
                        # Format to E.164 format
                        formatted_number = phonenumbers.format_number(
                            phone_number, 
                            phonenumbers.PhoneNumberFormat.E164
                        )
                        
                        self.logger.debug(f"Found phone number: {formatted_number}")
                        return formatted_number
                        
                except Exception:
                    continue
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error extracting phone number: {e}")
            return None
    
    def extract_linkedin(self, text: str) -> Optional[str]:
        """
        Extract LinkedIn profile URL from text.
        
        Args:
            text: Input text to search for LinkedIn URL
            
        Returns:
            LinkedIn URL or None
        """
        try:
            match = self.linkedin_pattern.search(text)
            if match:
                linkedin_url = f"https://linkedin.com/in/{match.group(1)}"
                self.logger.debug(f"Found LinkedIn: {linkedin_url}")
                return linkedin_url
            return None
        except Exception as e:
            self.logger.error(f"Error extracting LinkedIn URL: {e}")
            return None
    
    def extract_github(self, text: str) -> Optional[str]:
        """
        Extract GitHub profile URL from text.
        
        Args:
            text: Input text to search for GitHub URL
            
        Returns:
            GitHub URL or None
        """
        try:
            match = self.github_pattern.search(text)
            if match:
                github_url = f"https://github.com/{match.group(1)}"
                self.logger.debug(f"Found GitHub: {github_url}")
                return github_url
            return None
        except Exception as e:
            self.logger.error(f"Error extracting GitHub URL: {e}")
            return None
    
    def extract_websites(self, text: str) -> List[str]:
        """
        Extract website URLs that are not LinkedIn or GitHub.
        
        Args:
            text: Input text to search for website URLs
            
        Returns:
            List of website URLs
        """
        try:
            websites = []
            
            # Find all URLs
            matches = self.website_pattern.findall(text)
            
            for match in matches:
                url = match.lower().strip()
                
                # Skip LinkedIn and GitHub URLs
                if 'linkedin.com' in url or 'github.com' in url:
                    continue
                
                # Add protocol if missing
                if not url.startswith('http'):
                    url = f"https://{url}"
                
                # Avoid duplicates
                if url not in websites:
                    websites.append(url)
            
            self.logger.debug(f"Found {len(websites)} websites")
            return websites
            
        except Exception as e:
            self.logger.error(f"Error extracting websites: {e}")
            return []
    
    def extract_dates(self, text: str) -> List[Dict[str, Union[str, datetime, None]]]:
        """
        Extract all date mentions using dateparser library.
        
        Args:
            text: Input text to search for dates
            
        Returns:
            List of dictionaries with raw text, parsed datetime, and type
        """
        try:
            dates = []
            
            # Common date patterns to search for
            date_patterns = [
                r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s*\d{4}\b',
                r'\b\d{1,2}/\d{1,2}/\d{4}\b',
                r'\b\d{4}-\d{2}-\d{2}\b',
                r'\b(?:Spring|Summer|Fall|Winter)\s+\d{4}\b',
                r'\b\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}\b'
            ]
            
            # Combine all patterns
            combined_pattern = '|'.join(f'({pattern})' for pattern in date_patterns)
            
            for match in re.finditer(combined_pattern, text, re.IGNORECASE):
                raw_date = match.group(0).strip()
                
                # Check for present/current indicators
                date_type = 'unknown'
                if any(word in raw_date.lower() for word in ['present', 'current', 'now']):
                    dates.append({
                        'raw': raw_date,
                        'parsed': None,
                        'type': 'end'
                    })
                    continue
                
                # Parse the date
                try:
                    parsed_date = dateparser.parse(raw_date)
                    if parsed_date:
                        dates.append({
                            'raw': raw_date,
                            'parsed': parsed_date,
                            'type': 'unknown'
                        })
                except Exception:
                    # If parsing fails, still include the raw date
                    dates.append({
                        'raw': raw_date,
                        'parsed': None,
                        'type': 'unknown'
                    })
            
            self.logger.debug(f"Found {len(dates)} dates")
            return dates
            
        except Exception as e:
            self.logger.error(f"Error extracting dates: {e}")
            return []
    
    def extract_years_of_experience(self, text: str) -> Optional[int]:
        """
        Extract years of experience from text.
        Looks for patterns like '5 years of experience', '3+ years', '2-4 years'.
        
        Args:
            text: Input text to search for experience mentions
            
        Returns:
            Maximum years mentioned or None
        """
        try:
            matches = self.experience_pattern.findall(text)
            
            max_years = None
            
            for match in matches:
                try:
                    years_str = match[0]  # Get the first group (the number)
                    years = float(years_str)
                    
                    # Handle ranges like "2-4 years" by taking the higher number
                    if '-' in match:
                        # This is a range, extract the higher number
                        range_match = re.search(r'(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)', match)
                        if range_match:
                            years = max(float(range_match.group(1)), float(range_match.group(2)))
                    
                    # Update maximum years found
                    if max_years is None or years > max_years:
                        max_years = years
                        
                except ValueError:
                    continue
            
            result = int(max_years) if max_years is not None else None
            if result:
                self.logger.debug(f"Found years of experience: {result}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error extracting years of experience: {e}")
            return None
    
    def extract_skills_from_list(self, text: str, skill_taxonomy: List[str]) -> List[str]:
        """
        Extract skills from text using case-insensitive matching with known skills taxonomy.
        Handles compound skills like 'Node.js', 'React.js', 'C++', '.NET'.
        
        Args:
            text: Input text to search for skills
            skill_taxonomy: List of known skills to match against
            
        Returns:
            Sorted list of matched skills
        """
        try:
            found_skills = set()
            text_lower = text.lower()
            
            for skill in skill_taxonomy:
                if not skill or not skill.strip():
                    continue
                
                skill_lower = skill.lower().strip()
                
                # Handle compound skills with special characters
                # Escape special regex characters in skill names
                escaped_skill = re.escape(skill_lower)
                
                # Create pattern that matches whole words or compound skills
                pattern = r'\b' + escaped_skill + r'\b'
                
                # For compound skills with dots, also match without dots
                if '.' in skill_lower:
                    pattern += r'|\b' + escaped_skill.replace('.', '') + r'\b'
                
                if re.search(pattern, text_lower):
                    found_skills.add(skill.strip())
            
            # Convert to sorted list
            result = sorted(list(found_skills))
            
            self.logger.debug(f"Found {len(result)} skills: {result}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error extracting skills: {e}")
            return []
    
    def extract_all_contact_info(self, text: str) -> Dict[str, Union[str, List[str], None]]:
        """
        Extract all contact information in one call.
        
        Args:
            text: Input text to analyze
            
        Returns:
            Dictionary with all contact information
        """
        return {
            'email': self.extract_email(text),
            'phone': self.extract_phone(text),
            'linkedin': self.extract_linkedin(text),
            'github': self.extract_github(text),
            'websites': self.extract_websites(text)
        }
    
    def extract_all_temporal_info(self, text: str) -> Dict[str, Union[List, int, None]]:
        """
        Extract all temporal information in one call.
        
        Args:
            text: Input text to analyze
            
        Returns:
            Dictionary with dates and experience information
        """
        return {
            'dates': self.extract_dates(text),
            'years_of_experience': self.extract_years_of_experience(text)
        }


# Example usage and testing
if __name__ == "__main__":
    # Sample text for testing
    sample_text = """
    John Doe
    Email: john.doe@example.com
    Phone: +1-555-555-5555
    LinkedIn: https://www.linkedin.com/in/johndoe
    GitHub: https://github.com/johndoe
    Website: https://johndoe.com
    
    Experience:
    - Senior Software Engineer at Tech Corp (Jan 2020 - Present)
    - 5+ years of experience in software development
    - 2-3 years of experience with Python
    
    Skills: Python, JavaScript, Node.js, React.js, C++, .NET, SQL
    """
    
    parser = RuleBasedParser()
    
    # Test contact extraction
    contact_info = parser.extract_all_contact_info(sample_text)
    print("Contact Info:", contact_info)
    
    # Test temporal extraction
    temporal_info = parser.extract_all_temporal_info(sample_text)
    print("Temporal Info:", temporal_info)
    
    # Test skills extraction
    skills = ['Python', 'JavaScript', 'Node.js', 'React.js', 'C++', '.NET', 'SQL', 'Java']
    found_skills = parser.extract_skills_from_list(sample_text, skills)
    print("Found Skills:", found_skills)
