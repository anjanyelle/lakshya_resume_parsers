#!/usr/bin/env python3
"""
Enhanced Work Experience and Certification Parser
Based on Kickresume-style approach for better extraction
"""

import re
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from pathlib import Path

class WorkExperienceParser:
    """Specialized parser for work experience sections"""
    
    def __init__(self):
        self.job_title_patterns = self._load_job_title_patterns()
        self.company_patterns = self._load_company_patterns()
        self.date_patterns = self._load_date_patterns()
    
    def _load_job_title_patterns(self) -> Dict[str, List[str]]:
        """Load job title normalization patterns"""
        return {
            "software_engineer": ["software engineer", "software developer", "sde", "software dev"],
            "data_scientist": ["data scientist", "data science", "ds", "data analyst"],
            "product_manager": ["product manager", "pm", "product owner"],
            "project_manager": ["project manager", "pmp", "project lead"],
            "business_analyst": ["business analyst", "ba", "systems analyst"],
            "devops_engineer": ["devops engineer", "devops", "site reliability engineer", "sre"],
            "full_stack_developer": ["full stack", "full-stack", "fullstack developer"],
            "frontend_developer": ["frontend", "front-end", "ui developer", "front end"],
            "backend_developer": ["backend", "back-end", "api developer", "back end"]
        }
    
    def _load_company_patterns(self) -> Dict[str, List[str]]:
        """Load company name normalization patterns"""
        return {
            "google": ["google", "alphabet", "alphabet inc."],
            "microsoft": ["microsoft", "msft", "microsoft corporation"],
            "amazon": ["amazon", "aws", "amazon web services"],
            "apple": ["apple", "apple inc.", "apple computer"],
            "meta": ["meta", "facebook", "fb"],
            "netflix": ["netflix", "netflix inc."],
            "uber": ["uber", "uber technologies"],
            "airbnb": ["airbnb", "airbnb inc."]
        }
    
    def _load_date_patterns(self) -> List[str]:
        """Load date parsing patterns"""
        return [
            r'(\w{3,9}\s+\d{4})\s*-\s*(\w{3,9}\s+\d{4})',  # Jan 2020 - Dec 2021
            r'(\d{1,2}/\d{4})\s*-\s*(\d{1,2}/\d{4})',      # 01/2020 - 12/2021
            r'(\d{4})\s*-\s*(\d{4})',                      # 2020 - 2021
            r'(\w{3,9}\s+\d{4})\s*-\s*Present',           # Jan 2020 - Present
            r'(\d{1,2}/\d{4})\s*-\s*Present'              # 01/2020 - Present
        ]
    
    def normalize_job_title(self, title: str) -> str:
        """Normalize job title to standard format"""
        if not title:
            return ""
        
        title_lower = title.lower().strip()
        
        for standard_title, variations in self.job_title_patterns.items():
            for variation in variations:
                if variation in title_lower:
                    return standard_title
        
        return title.strip()
    
    def normalize_company_name(self, company: str) -> str:
        """Normalize company name to standard format"""
        if not company:
            return ""
        
        company_lower = company.lower().strip()
        
        for standard_name, variations in self.company_patterns.items():
            for variation in variations:
                if variation in company_lower:
                    return standard_name
        
        return company.strip()
    
    def extract_dates(self, date_text: str) -> Tuple[Optional[str], Optional[str], Optional[int]]:
        """Extract start date, end date, and duration in months"""
        if not date_text:
            return None, None, None
        
        for pattern in self.date_patterns:
            match = re.search(pattern, date_text, re.IGNORECASE)
            if match:
                start_date = self._parse_date(match.group(1))
                end_date = self._parse_date(match.group(2)) if len(match.groups()) > 1 else None
                
                if start_date and end_date:
                    duration = self._calculate_duration(start_date, end_date)
                elif start_date:
                    duration = self._calculate_duration(start_date, datetime.now())
                else:
                    duration = None
                
                return start_date, end_date, duration
        
        return None, None, None
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse date string to datetime object"""
        date_formats = [
            "%B %Y", "%b %Y",  # January 2020, Jan 2020
            "%m/%Y", "%Y",     # 01/2020, 2020
        ]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except ValueError:
                continue
        
        return None
    
    def _calculate_duration(self, start: datetime, end: datetime) -> int:
        """Calculate duration in months between two dates"""
        return (end.year - start.year) * 12 + (end.month - start.month)
    
    def extract_skills_from_description(self, description: str) -> List[str]:
        """Extract technical skills from job description"""
        if not description:
            return []
        
        # Common technical skills to look for
        tech_skills = [
            "python", "java", "javascript", "react", "angular", "vue", "node.js",
            "aws", "azure", "gcp", "docker", "kubernetes", "jenkins", "git",
            "sql", "nosql", "mongodb", "postgresql", "mysql", "oracle",
            "tensorflow", "pytorch", "keras", "scikit-learn", "pandas", "numpy",
            "html", "css", "sass", "webpack", "babel", "typescript",
            "linux", "unix", "windows", "macos", "ubuntu", "centos",
            "agile", "scrum", "kanban", "jira", "confluence", "slack"
        ]
        
        description_lower = description.lower()
        found_skills = []
        
        for skill in tech_skills:
            if skill in description_lower:
                found_skills.append(skill)
        
        return found_skills
    
    def parse_work_experience(self, text: str) -> List[Dict]:
        """Parse work experience section from resume text"""
        experiences = []
        
        # Split by common work experience separators
        sections = re.split(r'\n\s*\n|\n-{3,}', text)
        
        for section in sections:
            if not section.strip():
                continue
            
            experience = self._parse_single_experience(section)
            if experience:
                experiences.append(experience)
        
        return experiences
    
    def _parse_single_experience(self, section: str) -> Optional[Dict]:
        """Parse a single work experience entry"""
        lines = [line.strip() for line in section.split('\n') if line.strip()]
        
        if len(lines) < 2:
            return None
        
        # Extract job title and company (usually first lines)
        job_title = ""
        company = ""
        dates = None
        
        # Look for job title patterns
        for i, line in enumerate(lines):
            if any(keyword in line.lower() for keyword in ["engineer", "scientist", "analyst", "manager", "developer", "architect"]):
                job_title = self.normalize_job_title(line)
                # Company is usually in the next line
                if i + 1 < len(lines):
                    company = self.normalize_company_name(lines[i + 1])
                break
        
        # Look for dates
        for line in lines:
            if any(keyword in line.lower() for keyword in ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec", "2020", "2021", "2022", "2023", "2024", "present"]):
                dates = line
                break
        
        start_date, end_date, duration = self.extract_dates(dates)
        
        # Extract responsibilities (remaining lines)
        responsibilities = []
        description = ""
        
        for line in lines:
            if line.startswith('•') or line.startswith('-') or line.startswith('*'):
                responsibilities.append(line.lstrip('•-*').strip())
        
        description = " ".join(responsibilities)
        
        # Extract skills from description
        skills_used = self.extract_skills_from_description(description)
        
        return {
            "job_title": job_title,
            "company": company,
            "start_date": start_date.isoformat() if start_date else None,
            "end_date": end_date.isoformat() if end_date else None,
            "duration_months": duration,
            "responsibilities": responsibilities,
            "skills_used": skills_used,
            "description": description,
            "raw_text": section
        }


class CertificationParser:
    """Specialized parser for certification sections"""
    
    def __init__(self):
        self.certification_patterns = self._load_certification_patterns()
        self.issuer_patterns = self._load_issuer_patterns()
    
    def _load_certification_patterns(self) -> Dict[str, List[str]]:
        """Load certification name patterns"""
        return {
            "aws_solutions_architect": [
                "aws solutions architect", "aws certified solutions architect", "aws sa"
            ],
            "aws_developer": [
                "aws certified developer", "aws developer", "aws cd"
            ],
            "google_cloud_architect": [
                "google cloud architect", "gcp architect", "google certified professional cloud architect"
            ],
            "azure_fundamentals": [
                "azure fundamentals", "az-900", "microsoft azure fundamentals"
            ],
            "compTIA_a+": [
                "comptia a+", "a+ certification", "comptia a plus"
            ],
            "pmp": [
                "pmp", "project management professional", "pmi pmp"
            ],
            "csm": [
                "csm", "certified scrummaster", "scrum master certified"
            ]
        }
    
    def _load_issuer_patterns(self) -> Dict[str, List[str]]:
        """Load certification issuer patterns"""
        return {
            "amazon": ["amazon", "aws", "amazon web services"],
            "google": ["google", "gcp", "google cloud"],
            "microsoft": ["microsoft", "ms", "azure"],
            "compTIA": ["comptia", "computing technology industry association"],
            "pmi": ["pmi", "project management institute"],
            "scrum_alliance": ["scrum alliance"],
            "cisco": ["cisco", "cisco systems"],
            "oracle": ["oracle", "oracle corporation"]
        }
    
    def normalize_certification_name(self, name: str) -> str:
        """Normalize certification name"""
        if not name:
            return ""
        
        name_lower = name.lower().strip()
        
        for standard_name, variations in self.certification_patterns.items():
            for variation in variations:
                if variation in name_lower:
                    return standard_name
        
        return name.strip()
    
    def extract_issuer(self, text: str) -> str:
        """Extract certification issuer from text"""
        if not text:
            return ""
        
        text_lower = text.lower()
        
        for issuer, variations in self.issuer_patterns.items():
            for variation in variations:
                if variation in text_lower:
                    return issuer
        
        return ""
    
    def extract_certification_id(self, text: str) -> Optional[str]:
        """Extract certification ID from text"""
        # Look for common ID patterns
        id_patterns = [
            r'([A-Z]{2,}-\d{6,})',      # AWS-123456
            r'([A-Z]{3,}\d{3,})',       # PMP123
            r'ID:\s*(\w+)',            # ID: 12345
            r'Cert\.\s*(\w+)',        # Cert. 12345
        ]
        
        for pattern in id_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1) if len(match.groups()) > 0 else match.group(0)
        
        return None
    
    def extract_dates(self, text: str) -> Tuple[Optional[str], Optional[str]]:
        """Extract issue and expiration dates"""
        date_patterns = [
            r'Issued:\s*(\w{3,9}\s+\d{4})\s*Expires:\s*(\w{3,9}\s+\d{4})',
            r'(\w{3,9}\s+\d{4})\s*-\s*(\w{3,9}\s+\d{4})',
            r'Valid:\s*(\w{3,9}\s+\d{4})\s*to\s*(\w{3,9}\s+\d{4})'
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                issue_date = self._parse_date(match.group(1))
                expiry_date = self._parse_date(match.group(2))
                return (
                    issue_date.isoformat() if issue_date else None,
                    expiry_date.isoformat() if expiry_date else None
                )
        
        return None, None
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse date string to datetime"""
        date_formats = ["%B %Y", "%b %Y", "%m/%Y", "%Y"]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except ValueError:
                continue
        
        return None
    
    def parse_certifications(self, text: str) -> List[Dict]:
        """Parse certification section from resume text"""
        certifications = []
        
        # Split by common separators
        sections = re.split(r'\n\s*\n|\n-{3,}', text)
        
        for section in sections:
            if not section.strip():
                continue
            
            cert = self._parse_single_certification(section)
            if cert:
                certifications.append(cert)
        
        return certifications
    
    def _parse_single_certification(self, section: str) -> Optional[Dict]:
        """Parse a single certification entry"""
        lines = [line.strip() for line in section.split('\n') if line.strip()]
        
        if not lines:
            return None
        
        # Extract certification name (usually first line)
        name = self.normalize_certification_name(lines[0])
        
        # Extract issuer from full text
        issuer = self.extract_issuer(section)
        
        # Extract dates
        issue_date, expiry_date = self.extract_dates(section)
        
        # Extract certification ID
        cert_id = self.extract_certification_id(section)
        
        return {
            "name": name,
            "issuer": issuer,
            "issue_date": issue_date,
            "expiration_date": expiry_date,
            "credential_id": cert_id,
            "raw_text": section
        }


def main():
    """Test the parsers with sample data"""
    
    # Sample work experience text
    work_text = """
    Senior Software Engineer
    Google
    Jan 2020 - Dec 2021
    
    • Developed scalable web applications using React and Node.js
    • Led team of 5 engineers on cloud migration project
    • Implemented CI/CD pipelines with Jenkins and Docker
    • Worked with AWS and Kubernetes for deployment
    """
    
    # Sample certification text
    cert_text = """
    AWS Certified Solutions Architect
    Amazon Web Services
    Issued: June 2023 Expires: June 2026
    ID: AWS-123456
    """
    
    # Parse work experience
    work_parser = WorkExperienceParser()
    experiences = work_parser.parse_work_experience(work_text)
    
    # Parse certifications
    cert_parser = CertificationParser()
    certifications = cert_parser.parse_certifications(cert_text)
    
    # Output results
    result = {
        "work_experience": experiences,
        "certifications": certifications
    }
    
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
