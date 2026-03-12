"""
Advanced work experience extractor for resume parsing.
Extracts structured work experience with dates, duration, and skills analysis.
"""

import re
import logging
from typing import List, Dict, Optional, Tuple
from datetime import datetime, date
from dateparser import parse as dateparse
import calendar

# Configure logging
logger = logging.getLogger(__name__)


class ExperienceExtractor:
    """
    Advanced work experience extractor with comprehensive parsing capabilities.
    Extracts structured work history with duration calculation and skills analysis.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Pre-compiled patterns for better performance
        self._compile_patterns()
    
    def _compile_patterns(self):
        """Pre-compile regex patterns for experience extraction."""
        
        # Date patterns
        self.date_range_pattern = re.compile(
            r'(\w+\s+\d{4})\s*[-–—]\s*(\w+\s+\d{4}|\bPresent\b|\bCurrent\b|\bNow\b)',
            re.IGNORECASE
        )
        
        self.year_range_pattern = re.compile(
            r'(\d{4})\s*[-–—]\s*(\d{4}|\bPresent\b|\bCurrent\b|\bNow\b)',
            re.IGNORECASE
        )
        
        self.single_date_pattern = re.compile(
            r'\b(\w+\s+\d{4}|\d{4})\b',
            re.IGNORECASE
        )
        
        # Job title patterns
        self.job_title_patterns = [
            r'(?:Senior|Junior|Lead|Principal|Staff|Chief|Head|VP|Director|Manager|Associate|Assistant)?\s*'
            r'(?:Software|Web|Mobile|Front[-\s]?end|Back[-\s]?end|Full[-\s]?stack|Data|Machine\sLearning|AI|DevOps|Cloud|Security|QA|Test)?\s*'
            r'(?:Engineer|Developer|Architect|Consultant|Analyst|Specialist|Scientist|Researcher|Designer|Product\sManager|Project\sManager)',
            
            r'(?:Senior|Junior|Lead|Principal|Staff|Chief|Head|VP|Director|Manager)?\s*'
            r'(?:Marketing|Sales|Business|Financial|Human\sResource|Operations|Customer|Technical)?\s*'
            r'(?:Manager|Director|VP|Specialist|Analyst|Consultant|Coordinator|Representative|Associate)',
            
            r'(?:Chief|Head|VP|Director|Lead|Senior|Principal|Staff)?\s*'
            r'(?:Executive|Operating|Technical|Financial|Marketing|Sales|Product)?\s*'
            r'(?:Officer|Specialist|Manager|Director)'
        ]
        
        # Company patterns
        self.company_patterns = [
            r'(?:at|@)\s+([A-Za-z0-9\s&.,\-\'\"]+(?:Inc|LLC|Ltd|Corp|Company|Group|Technologies|Solutions)?)(?:\s|\n|$)',
            r'^([A-Za-z0-9\s&.,\-\'\"]+(?:Inc|LLC|Ltd|Corp|Company|Group|Technologies|Solutions)?)\s*[\|\-•]',
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*(?:\s+(?:Inc|LLC|Ltd|Corp|Company|Group|Technologies|Solutions))?)'
        ]
        
        # Location patterns
        self.location_pattern = re.compile(
            r'([A-Za-z\s]+,\s*[A-Z]{2}|[A-Za-z\s]+,\s*[A-Za-z]+|[A-Za-z\s]+,\s*[A-Za-z\s]+)',
            re.IGNORECASE
        )
        
        # Skills indicators in descriptions
        self.skill_indicators = [
            r'(?:developed|built|created|implemented|designed|architected|used|worked\s+with|experienced\s+in)\s+([A-Za-z0-9\s+#\-\.]+)',
            r'(?:proficient\s+in|skilled\s+in|expertise\s+in|knowledge\s+of)\s+([A-Za-z0-9\s+#\-\.]+)',
            r'(?:languages?:|technologies?:|tools?:|frameworks?:)\s*([A-Za-z0-9\s,#\-\.]+)'
        ]
    
    def extract_work_experience(self, experience_section_text: str) -> List[Dict]:
        """
        Extract structured work experience from experience section text.
        
        Args:
            experience_section_text: Text from the experience section
            
        Returns:
            List of work experience dictionaries with detailed information
        """
        try:
            if not experience_section_text or not experience_section_text.strip():
                return []
            
            # Split into individual job blocks
            job_blocks = self._split_into_job_blocks(experience_section_text)
            
            experiences = []
            
            for block in job_blocks:
                experience = self._parse_job_experience(block)
                if experience:
                    experiences.append(experience)
            
            # Sort by start date (most recent first)
            experiences.sort(key=lambda x: self._parse_date(x.get('start_date', '')), reverse=True)
            
            self.logger.info(f"Extracted {len(experiences)} work experiences")
            return experiences
            
        except Exception as e:
            self.logger.error(f"Error extracting work experience: {e}")
            return []
    
    def _split_into_job_blocks(self, text: str) -> List[str]:
        """
        Split experience text into individual job blocks.
        
        Args:
            text: Experience section text
            
        Returns:
            List of job blocks
        """
        # Split by common job separators
        separators = [
            r'\n(?=[A-Z][a-zA-Z\s]*\s*(?:Engineer|Developer|Manager|Director|Analyst|Specialist|Consultant))',
            r'\n(?=\w+\s+\d{4}\s*[-–—])',
            r'\n(?=[A-Z][a-zA-Z0-9\s&.,\-\'\"]+(?:Inc|LLC|Ltd|Corp|Company))',
            r'\n(?=[A-Z][A-Za-z\s]{10,})\s*\n'  # All caps company names
        ]
        
        combined_pattern = '|'.join(separators)
        blocks = re.split(combined_pattern, text, flags=re.MULTILINE)
        
        return [block.strip() for block in blocks if block.strip()]
    
    def _parse_job_experience(self, block: str) -> Optional[Dict]:
        """
        Parse a single job block into structured experience data.
        
        Args:
            block: Job block text
            
        Returns:
            Dictionary with structured job information
        """
        try:
            lines = [line.strip() for line in block.split('\n') if line.strip()]
            if not lines:
                return None
            
            experience = {
                'job_title': '',
                'company_name': '',
                'start_date': '',
                'end_date': '',
                'duration_months': 0,
                'location': None,
                'description': '',
                'skills_mentioned': []
            }
            
            # Extract job title (usually first line with title keywords)
            experience['job_title'] = self._extract_job_title(lines)
            
            # Extract company name
            experience['company_name'] = self._extract_company_name(block, experience['job_title'])
            
            # Extract dates
            start_date, end_date = self._extract_dates(block)
            experience['start_date'] = start_date
            experience['end_date'] = end_date
            
            # Calculate duration
            experience['duration_months'] = self._calculate_duration_months(start_date, end_date)
            
            # Extract location
            experience['location'] = self._extract_location(block)
            
            # Extract description
            experience['description'] = self._extract_description(block, experience['job_title'], experience['company_name'])
            
            # Extract skills from description
            experience['skills_mentioned'] = self._extract_skills_from_description(experience['description'])
            
            return experience if experience['job_title'] else None
            
        except Exception as e:
            self.logger.error(f"Error parsing job experience: {e}")
            return None
    
    def _extract_job_title(self, lines: List[str]) -> str:
        """Extract job title from lines."""
        for line in lines:
            for pattern in self.job_title_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    return line.strip()
        return lines[0] if lines else ''
    
    def _extract_company_name(self, block: str, job_title: str) -> str:
        """Extract company name from block."""
        # Remove job title from block to avoid false matches
        block_without_title = block.replace(job_title, '', 1)
        
        for pattern in self.company_patterns:
            matches = re.findall(pattern, block_without_title, re.IGNORECASE)
            if matches:
                company = matches[0].strip()
                # Clean up company name
                company = re.sub(r'[\|\-•].*$', '', company).strip()
                if len(company) > 2:  # Minimum length check
                    return company
        
        return ''
    
    def _extract_dates(self, block: str) -> Tuple[str, str]:
        """Extract start and end dates from block."""
        # Try date range patterns first
        for pattern in [self.date_range_pattern, self.year_range_pattern]:
            matches = re.findall(pattern, block)
            if matches:
                start_date, end_date = matches[0]
                return self._normalize_date(start_date), self._normalize_date(end_date)
        
        # Try individual dates
        dates = re.findall(self.single_date_pattern, block)
        if len(dates) >= 2:
            return self._normalize_date(dates[0]), self._normalize_date(dates[1])
        elif dates:
            return self._normalize_date(dates[0]), 'Present'
        
        return '', ''
    
    def _normalize_date(self, date_str: str) -> str:
        """Normalize date string to standard format."""
        if not date_str or date_str.lower() in ['present', 'current', 'now']:
            return 'Present'
        
        try:
            parsed_date = dateparse(date_str)
            if parsed_date:
                return parsed_date.strftime('%B %Y')
        except:
            pass
        
        return date_str.strip()
    
    def _calculate_duration_months(self, start_date: str, end_date: str) -> int:
        """Calculate duration in months between start and end dates."""
        if not start_date:
            return 0
        
        try:
            start = self._parse_date(start_date)
            end = self._parse_date(end_date) if end_date.lower() != 'present' else date.today()
            
            if start and end:
                months = (end.year - start.year) * 12 + (end.month - start.month)
                return max(0, months)
        except:
            pass
        
        return 0
    
    def _parse_date(self, date_str: str) -> Optional[date]:
        """Parse date string into date object."""
        if not date_str or date_str.lower() in ['present', 'current', 'now']:
            return None
        
        try:
            parsed_date = dateparse(date_str)
            if parsed_date:
                return parsed_date.date()
        except:
            pass
        
        return None
    
    def _extract_location(self, block: str) -> Optional[str]:
        """Extract location from block."""
        matches = re.findall(self.location_pattern, block)
        if matches:
            # Return the most likely location (usually after company/dates)
            return matches[-1].strip()
        return None
    
    def _extract_description(self, block: str, job_title: str, company_name: str) -> str:
        """Extract job description from block."""
        # Remove job title, company, dates, and location from block
        description = block
        
        # Remove job title
        if job_title:
            description = description.replace(job_title, '', 1)
        
        # Remove company name
        if company_name:
            description = description.replace(company_name, '', 1)
        
        # Remove dates
        description = re.sub(r'\b\w+\s+\d{4}\s*[-–—]\s*(\w+\s+\d{4}|\bPresent\b|\bCurrent\b|\bNow\b)', '', description)
        description = re.sub(r'\b\d{4}\s*[-–—]\s*(\d{4}|\bPresent\b|\bCurrent\b|\bNow\b)', '', description)
        
        # Remove location patterns
        description = re.sub(self.location_pattern, '', description)
        
        # Clean up bullet points and formatting
        lines = [line.strip() for line in description.split('\n') if line.strip()]
        
        # Filter out lines that are likely titles/dates/locations
        description_lines = []
        for line in lines:
            # Skip if it looks like a title, company, or date
            if (len(line) < 10 or 
                re.search(r'(?:Engineer|Developer|Manager|Director|Analyst|Specialist|Consultant)', line, re.IGNORECASE) or
                re.search(r'\b\d{4}\b', line) or
                re.search(r'\bPresent\b|\bCurrent\b', line, re.IGNORECASE)):
                continue
            description_lines.append(line)
        
        return '\n'.join(description_lines)
    
    def _extract_skills_from_description(self, description: str) -> List[str]:
        """Extract skills mentioned in job description."""
        skills = set()
        
        # Common technology skills to look for
        tech_skills = [
            'Python', 'Java', 'JavaScript', 'TypeScript', 'C++', 'C#', 'Go', 'Rust', 'PHP', 'Ruby', 'Swift',
            'React', 'Angular', 'Vue.js', 'Node.js', 'Express', 'Django', 'Flask', 'Spring', 'Laravel',
            'HTML', 'CSS', 'SASS', 'Bootstrap', 'Tailwind', 'jQuery',
            'SQL', 'MySQL', 'PostgreSQL', 'MongoDB', 'Redis', 'Elasticsearch',
            'AWS', 'Azure', 'Google Cloud', 'Docker', 'Kubernetes', 'Jenkins', 'Git', 'Linux',
            'Machine Learning', 'AI', 'Data Science', 'TensorFlow', 'PyTorch', 'Scikit-learn',
            'Agile', 'Scrum', 'DevOps', 'CI/CD', 'REST API', 'GraphQL', 'Microservices'
        ]
        
        # Check for skill mentions
        for skill in tech_skills:
            if re.search(r'\b' + re.escape(skill) + r'\b', description, re.IGNORECASE):
                skills.add(skill)
        
        return sorted(list(skills))
    
    def calculate_total_experience(self, work_history: List[Dict]) -> Dict:
        """
        Calculate total experience metrics from work history.
        
        Args:
            work_history: List of work experience dictionaries
            
        Returns:
            Dictionary with total experience metrics
        """
        try:
            total_months = 0
            all_periods = []
            
            for job in work_history:
                duration = job.get('duration_months', 0)
                if duration > 0:
                    total_months += duration
                    
                    # Add period for gap analysis
                    start_date = self._parse_date(job.get('start_date', ''))
                    end_date = self._parse_date(job.get('end_date', ''))
                    if start_date:
                        if not end_date or job.get('end_date', '').lower() in ['present', 'current']:
                            end_date = date.today()
                        all_periods.append((start_date, end_date))
            
            # Calculate gaps
            gap_months = 0
            has_gaps = False
            
            if len(all_periods) > 1:
                # Sort periods by start date
                all_periods.sort(key=lambda x: x[0])
                
                for i in range(1, len(all_periods)):
                    prev_end = all_periods[i-1][1]
                    curr_start = all_periods[i][0]
                    
                    if curr_start > prev_end:
                        gap = (curr_start.year - prev_end.year) * 12 + (curr_start.month - prev_end.month)
                        if gap > 1:  # Allow 1 month gap
                            gap_months += gap
                            has_gaps = True
            
            total_years = round(total_months / 12, 1)
            
            result = {
                'total_months': total_months,
                'total_years': total_years,
                'has_gaps': has_gaps,
                'gap_months': gap_months
            }
            
            self.logger.info(f"Calculated total experience: {total_years} years, gaps: {has_gaps}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error calculating total experience: {e}")
            return {
                'total_months': 0,
                'total_years': 0.0,
                'has_gaps': False,
                'gap_months': 0
            }


# Example usage and testing
if __name__ == "__main__":
    # Sample experience text for testing
    sample_experience = """
    Senior Software Engineer at Tech Corp
    January 2020 - Present
    San Francisco, CA
    • Developed scalable web applications using React and Node.js
    • Led a team of 3 junior developers
    • Improved application performance by 40%
    • Worked with AWS, Docker, and Kubernetes
    
    Software Developer at StartupXYZ
    June 2018 - December 2019
    • Built RESTful APIs and microservices
    • Used Python, Django, and PostgreSQL
    • Implemented CI/CD pipelines with Jenkins
    """
    
    extractor = ExperienceExtractor()
    
    # Test experience extraction
    experiences = extractor.extract_work_experience(sample_experience)
    print(f"Extracted {len(experiences)} experiences:")
    
    for i, exp in enumerate(experiences, 1):
        print(f"\n{i}. {exp['job_title']} at {exp['company_name']}")
        print(f"   Dates: {exp['start_date']} - {exp['end_date']}")
        print(f"   Duration: {exp['duration_months']} months")
        print(f"   Location: {exp['location']}")
        print(f"   Skills: {', '.join(exp['skills_mentioned'])}")
    
    # Test total experience calculation
    total_exp = extractor.calculate_total_experience(experiences)
    print(f"\nTotal Experience: {total_exp['total_years']} years")
    print(f"Has gaps: {total_exp['has_gaps']}")
    print(f"Gap months: {total_exp['gap_months']}")
