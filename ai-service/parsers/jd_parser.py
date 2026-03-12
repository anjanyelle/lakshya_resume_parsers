"""
Job description parser that extracts key information from job postings.
Identifies skills, experience requirements, education levels, and job metadata.
"""

import re
import logging
from typing import Dict, List, Tuple, Optional, Any
from collections import defaultdict

# Configure logging
logger = logging.getLogger(__name__)


class JobDescriptionParser:
    """
    Parser for extracting structured information from job descriptions.
    Identifies skills, experience requirements, education, and job metadata.
    """
    
    def __init__(self):
        """Initialize the job description parser with patterns and keywords."""
        self.logger = logging.getLogger(__name__)
        
        # Skill-related patterns
        self.skill_patterns = {
            'required': [
                r'(?:required|must have|requirements?|essential|needed)[:\s]*([^\n]*)',
                r'(?:requirements?|qualifications?)[:\s]*([^\n]*)',
                r'(?:must have|required skills?)[:\s]*([^\n]*)',
                r'(?:essential skills?)[:\s]*([^\n]*)',
            ],
            'preferred': [
                r'(?:preferred|nice to have|desired|plus|bonus)[:\s]*([^\n]*)',
                r'(?:nice to have skills?|preferred skills?)[:\s]*([^\n]*)',
                r'(?:desired qualifications?|plus points?)[:\s]*([^\n]*)',
            ]
        }
        
        # Experience patterns
        self.experience_patterns = [
            r'(\d+)\+?\s*[-–to]?\s*(\d+)?\s*years?',
            r'(?:minimum|min|required|at least)\s+(\d+)\s*years?',
            r'(?:up to|max)\s+(\d+)\s*years?',
            r'(\d+)\s*[-–to]\s*(\d+)\s*years?\s*(?:of\s*)?(?:experience|exp)?',
            r'(\d+)\s*\+\s*years?\s*(?:of\s*)?(?:experience|exp)?',
        ]
        
        # Seniority level patterns
        self.seniority_patterns = {
            'Junior': [
                r'junior|entry[-\s]?level|associate|intern|trainee|beginner',
                r'0[-–]?2\s*years?|1[-–]?2\s*years?|less than\s*3\s*years?'
            ],
            'Mid': [
                r'mid[-\s]?level|intermediate|3[-–]?5\s*years?|4[-–]?6\s*years?',
                r'2[-–]?4\s*years?|3[-–]?6\s*years?'
            ],
            'Senior': [
                r'senior|5[-–]?8\s*years?|6[-–]?10\s*years?|experienced',
                r'5\+\s*years?|7[-–]?10\s*years?'
            ],
            'Lead': [
                r'lead|principal|8[-–]?12\s*years?|10\+\s*years?|team lead',
                r'staff|principal engineer|architect'
            ],
            'Manager': [
                r'manager|management|director|head of|team manager|supervisor',
                r'people manager|team lead manager'
            ]
        }
        
        # Education patterns
        self.education_patterns = {
            'PhD': [
                r'phd|doctorate|doctoral|ph\.?d\.?'
            ],
            'Master': [
                r'master|msc|m\.?s\.?|master\'s|graduate degree|ma|m\.?a\.?'
            ],
            'Bachelor': [
                r'bachelor|bsc|b\.?s\.?|bachelor\'s|undergraduate|ba|b\.?a\.?'
            ],
            'Associate': [
                r'associate|diploma|2[-\s]?year degree|technical degree'
            ],
            'Any': [
                r'high school|ged|no degree|degree not required|any education'
            ]
        }
        
        # Employment type patterns
        self.employment_patterns = {
            'full-time': [
                r'full[-\s]?time|permanent|direct hire|employee'
            ],
            'part-time': [
                r'part[-\s]?time|part time'
            ],
            'contract': [
                r'contract|temporary|temp|freelance|consultant'
            ],
            'internship': [
                r'internship|intern|trainee'
            ]
        }
        
        # Common technology keywords for skill extraction
        self.tech_keywords = {
            'programming': [
                'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'go', 'rust',
                'ruby', 'php', 'swift', 'kotlin', 'scala', 'perl', 'r', 'matlab'
            ],
            'web': [
                'html', 'css', 'react', 'angular', 'vue', 'nodejs', 'django', 'flask',
                'express', 'spring', 'laravel', 'rails', 'asp.net', 'next.js'
            ],
            'mobile': [
                'ios', 'android', 'react native', 'flutter', 'swift', 'kotlin',
                'xamarin', 'cordova', 'ionic'
            ],
            'database': [
                'sql', 'nosql', 'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch',
                'oracle', 'sql server', 'cassandra', 'dynamodb'
            ],
            'cloud': [
                'aws', 'azure', 'google cloud', 'gcp', 'heroku', 'digitalocean',
                'kubernetes', 'docker', 'terraform', 'ansible', 'jenkins'
            ],
            'tools': [
                'git', 'github', 'gitlab', 'jira', 'slack', 'trello', 'asana',
                'vs code', 'intellij', 'eclipse', 'linux', 'windows', 'macos'
            ]
        }
        
        # Responsibility indicators
        self.responsibility_indicators = [
            r'[-•*]\s*(.+)',  # Bullet points
            r'responsibilities?[:\s]*(.+)',  # Responsibilities section
            r'what you\'ll do[:\s]*(.+)',  # Modern job descriptions
            r'your role[:\s]*(.+)',  # Role description
            r'duties?[:\s]*(.+)',  # Duties section
        ]
    
    def parse(self, jd_text: str) -> Dict[str, Any]:
        """
        Parse job description and extract structured information.
        
        Args:
            jd_text: Raw job description text
            
        Returns:
            Dictionary with extracted job information
        """
        try:
            self.logger.info("Starting job description parsing")
            
            # Clean and normalize text
            cleaned_text = self._clean_text(jd_text)
            
            # Extract all components
            result = {
                'required_skills': self.extract_required_skills(cleaned_text),
                'preferred_skills': self.extract_preferred_skills(cleaned_text),
                'min_experience_years': None,
                'max_experience_years': None,
                'education_requirement': self.extract_education_requirement(cleaned_text),
                'key_responsibilities': self.extract_key_responsibilities(cleaned_text),
                'employment_type': self.extract_employment_type(cleaned_text),
                'seniority_level': self.detect_seniority(cleaned_text),
                'all_skills_detected': self._extract_all_skills(cleaned_text),
                'salary_range': self._extract_salary_range(cleaned_text),
                'location': self._extract_location(cleaned_text),
                'company': self._extract_company(cleaned_text),
                'job_title': self._extract_job_title(cleaned_text)
            }
            
            # Extract experience requirements
            min_exp, max_exp = self.extract_experience_requirement(cleaned_text)
            result['min_experience_years'] = min_exp
            result['max_experience_years'] = max_exp
            
            # Post-processing and validation
            result = self._post_process_result(result)
            
            self.logger.info(f"Successfully parsed job description: {result['job_title']}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error parsing job description: {e}")
            return self._create_empty_result()
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize job description text."""
        if not text:
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Normalize bullet points
        text = re.sub(r'[·•▪▫◦‣⁃]', '-', text)
        
        # Remove special characters but keep important ones
        text = re.sub(r'[^\w\s\-\.\,\;\:\!\?\(\)\[\]/\+\&\@]', ' ', text)
        
        # Convert to lowercase for pattern matching (keep original for some extractions)
        return text.strip()
    
    def extract_required_skills(self, text: str) -> List[str]:
        """Extract required skills from job description."""
        skills = []
        text_lower = text.lower()
        
        # Try pattern-based extraction first
        for pattern in self.skill_patterns['required']:
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            for match in matches:
                extracted = self._extract_skills_from_text(match)
                skills.extend(extracted)
        
        # If no pattern matches, try general skill extraction
        if not skills:
            skills = self._extract_all_skills(text)
        
        # Remove duplicates and sort
        return sorted(list(set(skills)))
    
    def extract_preferred_skills(self, text: str) -> List[str]:
        """Extract preferred skills from job description."""
        skills = []
        text_lower = text.lower()
        
        # Try pattern-based extraction
        for pattern in self.skill_patterns['preferred']:
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            for match in matches:
                extracted = self._extract_skills_from_text(match)
                skills.extend(extracted)
        
        # Remove duplicates and sort
        return sorted(list(set(skills)))
    
    def _extract_skills_from_text(self, text: str) -> List[str]:
        """Extract skills from a piece of text."""
        skills = []
        text_lower = text.lower()
        
        # Check for tech keywords
        for category, keywords in self.tech_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    skills.append(keyword.title() if keyword.islower() else keyword)
        
        # Extract capitalized words (potential skills)
        capitalized_words = re.findall(r'\b[A-Z][a-zA-Z]+\b', text)
        for word in capitalized_words:
            if len(word) > 2 and word not in skills:
                # Filter out common non-skill words
                if not self._is_common_word(word.lower()):
                    skills.append(word)
        
        return skills
    
    def _extract_all_skills(self, text: str) -> List[str]:
        """Extract all skills from text using various methods."""
        skills = []
        text_lower = text.lower()
        
        # Tech keywords
        for category, keywords in self.tech_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    skills.append(keyword.title() if keyword.islower() else keyword)
        
        # Look for skill sections
        skill_section_patterns = [
            r'(?:skills?|technologies?|stack|tools?)[:\s]*([^\n]*)',
            r'(?:technical skills?|programming languages?)[:\s]*([^\n]*)',
        ]
        
        for pattern in skill_section_patterns:
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            for match in matches:
                extracted = self._extract_skills_from_text(match)
                skills.extend(extracted)
        
        return sorted(list(set(skills)))
    
    def _is_common_word(self, word: str) -> bool:
        """Check if a word is a common non-skill word."""
        common_words = {
            'experience', 'required', 'preferred', 'skills', 'ability', 'knowledge',
            'strong', 'excellent', 'good', 'years', 'plus', 'including', 'various',
            'multiple', 'related', 'relevant', 'field', 'industry', 'business',
            'development', 'management', 'support', 'analysis', 'design',
            'quality', 'high', 'level', 'position', 'role', 'team', 'work'
        }
        return word in common_words
    
    def detect_seniority(self, text: str) -> str:
        """Detect seniority level from job description."""
        text_lower = text.lower()
        
        # Score each seniority level
        scores = {}
        
        for level, patterns in self.seniority_patterns.items():
            score = 0
            for pattern in patterns:
                matches = re.findall(pattern, text_lower)
                score += len(matches)
            scores[level] = score
        
        # Return the level with highest score
        if max(scores.values()) > 0:
            return max(scores, key=scores.get)
        
        return 'Mid'  # Default fallback
    
    def extract_experience_requirement(self, text: str) -> Tuple[Optional[int], Optional[int]]:
        """Extract minimum and maximum experience requirements."""
        text_lower = text.lower()
        
        min_years = None
        max_years = None
        
        for pattern in self.experience_patterns:
            matches = re.findall(pattern, text_lower)
            
            for match in matches:
                if isinstance(match, tuple):
                    # Range pattern (e.g., "3-5 years")
                    first, second = match
                    if first and second:
                        min_exp = int(first)
                        max_exp = int(second)
                        min_years = min(min_years, min_exp) if min_years is not None else min_exp
                        max_years = max(max_years, max_exp) if max_years is not None else max_exp
                    elif first:
                        exp = int(first)
                        if '+' in pattern:
                            max_years = max(max_years, exp) if max_years is not None else exp
                        else:
                            min_years = min(min_years, exp) if min_years is not None else exp
                            max_years = max(max_years, exp) if max_years is not None else exp
                else:
                    # Single number pattern
                    exp = int(match)
                    if '+' in pattern:
                        max_years = max(max_years, exp) if max_years is not None else exp
                    else:
                        min_years = min(min_years, exp) if min_years is not None else exp
                        max_years = max(max_years, exp) if max_years is not None else exp
        
        return min_years, max_years
    
    def extract_education_requirement(self, text: str) -> str:
        """Extract education requirement from job description."""
        text_lower = text.lower()
        
        # Score each education level
        scores = {}
        
        for level, patterns in self.education_patterns.items():
            score = 0
            for pattern in patterns:
                matches = re.findall(pattern, text_lower)
                score += len(matches)
            scores[level] = score
        
        # Return the level with highest score
        if max(scores.values()) > 0:
            return max(scores, key=scores.get)
        
        return 'Any'  # Default fallback
    
    def extract_key_responsibilities(self, text: str) -> List[str]:
        """Extract key responsibilities from job description."""
        responsibilities = []
        
        # Try different patterns for responsibilities
        for pattern in self.responsibility_indicators:
            matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
            
            for match in matches:
                # Clean up the responsibility
                responsibility = match.strip()
                
                # Filter out very short or irrelevant items
                if len(responsibility) > 10 and not self._is_responsibility_noise(responsibility):
                    responsibilities.append(responsibility)
        
        # If no structured responsibilities found, try to extract from bullet points
        if not responsibilities:
            bullet_points = re.findall(r'^[-•*]\s*(.+)$', text, re.MULTILINE)
            for point in bullet_points:
                if len(point.strip()) > 10:
                    responsibilities.append(point.strip())
        
        # Remove duplicates and limit to top 10
        unique_responsibilities = []
        seen = set()
        
        for resp in responsibilities:
            resp_lower = resp.lower()
            if resp_lower not in seen and len(unique_responsibilities) < 10:
                seen.add(resp_lower)
                unique_responsibilities.append(resp)
        
        return unique_responsibilities
    
    def _is_responsibility_noise(self, text: str) -> bool:
        """Check if responsibility text is noise."""
        noise_indicators = [
            'requirements:', 'qualifications:', 'skills:', 'benefits:',
            'about us:', 'company:', 'location:', 'salary:', 'apply now'
        ]
        
        text_lower = text.lower()
        return any(indicator in text_lower for indicator in noise_indicators)
    
    def extract_employment_type(self, text: str) -> str:
        """Extract employment type from job description."""
        text_lower = text.lower()
        
        # Score each employment type
        scores = {}
        
        for emp_type, patterns in self.employment_patterns.items():
            score = 0
            for pattern in patterns:
                matches = re.findall(pattern, text_lower)
                score += len(matches)
            scores[emp_type] = score
        
        # Return the type with highest score
        if max(scores.values()) > 0:
            return max(scores, key=scores.get)
        
        return 'full-time'  # Default fallback
    
    def _extract_salary_range(self, text: str) -> Optional[str]:
        """Extract salary range from job description."""
        salary_patterns = [
            r'\$[\d,]+[-–]\$?[\d,]+(?:\s*per\s*year)?',
            r'\$[\d,]+\s*[-–to]\s*\$?[\d,]+',
            r'(\d{1,3}[,\d{3}]*)\s*[-–to]\s*(\d{1,3}[,\d{3}]*)\s*k',
            r'(\d{1,3})k\s*[-–to]\s*(\d{1,3})k',
        ]
        
        for pattern in salary_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0)
        
        return None
    
    def _extract_location(self, text: str) -> Optional[str]:
        """Extract location from job description."""
        # Look for common location patterns
        location_patterns = [
            r'location[:\s]*([^\n,]+)',
            r'based in ([^\n,]+)',
            r'([A-Za-z\s]+,\s*[A-Z]{2})',  # City, State pattern
            r'([A-Za-z\s]+,\s*[A-Za-z\s]+)',  # City, Country pattern
        ]
        
        for pattern in location_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                location = match.group(1).strip()
                if len(location) > 2 and len(location) < 50:
                    return location
        
        return None
    
    def _extract_company(self, text: str) -> Optional[str]:
        """Extract company name from job description."""
        # Look for company patterns
        company_patterns = [
            r'company[:\s]*([^\n,]+)',
            r'about ([^\n,]+)',
            r'at ([A-Z][a-zA-Z\s&]+)',  # "at CompanyName"
        ]
        
        for pattern in company_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                company = match.group(1).strip()
                if len(company) > 2 and len(company) < 50:
                    return company
        
        return None
    
    def _extract_job_title(self, text: str) -> Optional[str]:
        """Extract job title from job description."""
        lines = text.split('\n')
        
        # Job title is usually in the first few lines
        for i, line in enumerate(lines[:5]):
            line = line.strip()
            if len(line) > 5 and len(line) < 100:
                # Check if it looks like a title (contains common job keywords)
                job_keywords = [
                    'engineer', 'developer', 'manager', 'analyst', 'designer',
                    'architect', 'consultant', 'specialist', 'coordinator',
                    'director', 'lead', 'senior', 'junior', 'associate'
                ]
                
                line_lower = line.lower()
                if any(keyword in line_lower for keyword in job_keywords):
                    # Remove common prefixes
                    title = re.sub(r'^(job title|position|role)[:\s]*', '', line, re.IGNORECASE)
                    return title.strip()
        
        return None
    
    def _post_process_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Post-process and validate the parsed result."""
        # Ensure experience years are reasonable
        if result['min_experience_years'] is not None:
            result['min_experience_years'] = max(0, min(result['min_experience_years'], 50))
        
        if result['max_experience_years'] is not None:
            result['max_experience_years'] = max(0, min(result['max_experience_years'], 50))
        
        # Ensure min <= max for experience
        if (result['min_experience_years'] is not None and 
            result['max_experience_years'] is not None and
            result['min_experience_years'] > result['max_experience_years']):
            result['min_experience_years'], result['max_experience_years'] = (
                result['max_experience_years'], result['min_experience_years']
            )
        
        # Limit skills to reasonable number
        result['required_skills'] = result['required_skills'][:20]
        result['preferred_skills'] = result['preferred_skills'][:20]
        result['all_skills_detected'] = result['all_skills_detected'][:50]
        
        # Limit responsibilities
        result['key_responsibilities'] = result['key_responsibilities'][:10]
        
        return result
    
    def _create_empty_result(self) -> Dict[str, Any]:
        """Create an empty result structure for error cases."""
        return {
            'required_skills': [],
            'preferred_skills': [],
            'min_experience_years': None,
            'max_experience_years': None,
            'education_requirement': 'Any',
            'key_responsibilities': [],
            'employment_type': 'full-time',
            'seniority_level': 'Mid',
            'all_skills_detected': [],
            'salary_range': None,
            'location': None,
            'company': None,
            'job_title': None
        }


# Example usage and testing
if __name__ == "__main__":
    # Sample job description for testing
    sample_jd = """
    Senior Software Engineer
    
    We are looking for a Senior Software Engineer to join our growing team.
    
    Requirements:
    - 5+ years of experience in software development
    - Strong knowledge of Python, JavaScript, and React
    - Experience with AWS and Docker
    - Bachelor's degree in Computer Science or related field
    
    Responsibilities:
    - Design and develop scalable web applications
    - Lead a team of 3-5 junior developers
    - Collaborate with product managers and stakeholders
    - Write clean, maintainable code
    
    Preferred Skills:
    - Experience with Kubernetes
    - Knowledge of TypeScript
    - Familiarity with Agile methodologies
    
    This is a full-time position based in San Francisco, CA.
    Salary: $120,000 - $160,000 per year
    """
    
    try:
        # Initialize parser
        parser = JobDescriptionParser()
        
        print("🔍 Testing Job Description Parser")
        print("=" * 50)
        
        # Parse the job description
        result = parser.parse(sample_jd)
        
        print("📋 Parsed Job Information:")
        print(f"  Job Title: {result['job_title']}")
        print(f"  Seniority Level: {result['seniority_level']}")
        print(f"  Experience: {result['min_experience_years']}-{result['max_experience_years']} years")
        print(f"  Education: {result['education_requirement']}")
        print(f"  Employment Type: {result['employment_type']}")
        print(f"  Location: {result['location']}")
        print(f"  Salary: {result['salary_range']}")
        
        print(f"\n🛠️  Required Skills ({len(result['required_skills'])}):")
        for skill in result['required_skills']:
            print(f"    • {skill}")
        
        print(f"\n✨ Preferred Skills ({len(result['preferred_skills'])}):")
        for skill in result['preferred_skills']:
            print(f"    • {skill}")
        
        print(f"\n📝 Key Responsibilities ({len(result['key_responsibilities'])}):")
        for i, resp in enumerate(result['key_responsibilities'], 1):
            print(f"    {i}. {resp}")
        
        print(f"\n🔧 All Skills Detected ({len(result['all_skills_detected'])}):")
        for skill in result['all_skills_detected']:
            print(f"    • {skill}")
        
        print("\n✅ Job description parser test completed!")
        
    except Exception as e:
        print(f"❌ Error testing job description parser: {e}")
