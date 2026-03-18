#!/usr/bin/env python3
"""
Quick Work Experience Parser - Rule-based approach
Achieves target JSON structure immediately
"""

import re
import pandas as pd
import os
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

class QuickWorkExperienceParser:
    """Quick rule-based work experience parser"""
    
    def __init__(self):
        self.companies_db = self._load_companies_database()
        self.job_titles_db = self._load_job_titles_database()
        self.skills_db = self._load_skills_database()
    
    def _load_companies_database(self) -> set:
        """Load companies from external database"""
        try:
            companies_path = "data/external/companies.csv"
            if os.path.exists(companies_path):
                df = pd.read_csv(companies_path)
                if 'name' in df.columns:
                    return set(df['name'].dropna().astype(str).tolist())
        except Exception as e:
            logger.warning(f"⚠️ Could not load companies database: {e}")
        
        return set()
    
    def _load_job_titles_database(self) -> set:
        """Load job titles from external database"""
        try:
            job_titles_path = "data/external/job_titles.csv"
            if os.path.exists(job_titles_path):
                df = pd.read_csv(job_titles_path)
                if 'title' in df.columns:
                    return set(df['title'].dropna().astype(str).tolist())
        except Exception as e:
            logger.warning(f"⚠️ Could not load job titles database: {e}")
        
        return set()
    
    def _load_skills_database(self) -> set:
        """Load skills from external database"""
        try:
            skills_path = "data/external/skills.csv"
            if os.path.exists(skills_path):
                df = pd.read_csv(skills_path)
                if 'skill_name' in df.columns:
                    return set(df['skill_name'].dropna().astype(str).tolist())
        except Exception as e:
            logger.warning(f"⚠️ Could not load skills database: {e}")
        
        return set()
    
    def parse_work_experience(self, work_text: str) -> List[Dict[str, Any]]:
        """
        Parse work experience using rule-based approach
        
        Args:
            work_text: Raw work experience text from resume
            
        Returns:
            List of work experience entries in target JSON format
        """
        try:
            logger.info("🚀 Starting quick work experience parsing...")
            
            # Split work text into individual jobs
            job_entries = self._split_work_entries(work_text)
            
            # Parse each job entry
            parsed_entries = []
            for job_text in job_entries:
                entry = self._parse_single_job(job_text)
                if entry:
                    parsed_entries.append(entry)
            
            logger.info(f"✅ Successfully parsed {len(parsed_entries)} work experience entries!")
            return parsed_entries
            
        except Exception as e:
            logger.error(f"❌ Error parsing work experience: {e}")
            return []
    
    def _split_work_entries(self, work_text: str) -> List[str]:
        """Split work text into individual job entries"""
        # Common job entry separators
        separators = [
            r'\n\s*[A-Z][a-z]+\s+\|\s*[A-Za-z\s&]+',  # Company | Title
            r'\n\s*[A-Z][a-z]+\s+\|\s*\d{4}',          # Company | Year
            r'\n\s*[A-Z][a-z]+\s+[A-Za-z]+\s+\|\s*\d{4}',  # Company Name | Year
            r'\n\s*[A-Z][a-z]+\s+\d{4}',              # Company Year
            r'\n\s*[A-Z][a-z]+\s+\|\s*[A-Z]',        # Company | Uppercase
        ]
        
        # Try to split using separators
        for separator in separators:
            parts = re.split(separator, work_text)
            if len(parts) > 1:
                return [part.strip() for part in parts if part.strip()]
        
        # If no separators found, treat as single entry
        return [work_text.strip()] if work_text.strip() else []
    
    def _parse_single_job(self, job_text: str) -> Optional[Dict[str, Any]]:
        """Parse a single job entry"""
        try:
            entry = {
                "company": self._extract_company(job_text),
                "job_title": self._extract_job_title(job_text),
                "start_date": self._extract_start_date(job_text),
                "end_date": self._extract_end_date(job_text),
                "is_current": self._is_current_job(job_text),
                "location": self._extract_location(job_text),
                "employment_type": self._extract_employment_type(job_text),
                "responsibilities": self._extract_responsibilities(job_text),
                "tech_stack": self._extract_tech_stack(job_text),
                "confidence": 0.0,
                "_source_model": "rule-based",
                "_missing_fields": []
            }
            
            # Calculate confidence
            entry["confidence"] = self._calculate_confidence(entry)
            
            # Identify missing fields
            entry["_missing_fields"] = self._get_missing_fields(entry)
            
            return entry
            
        except Exception as e:
            logger.error(f"❌ Error parsing job entry: {e}")
            return None
    
    def _extract_company(self, text: str) -> str:
        """Extract company name"""
        # Company patterns
        company_patterns = [
            r'^([A-Z][A-Za-z\s&.,\'-]+)\s*\|',  # Company | Title
            r'(?:Company|Employer|Organization):\s*([^\n\r]+)',
            r'(?:at|@)\s*([A-Z][A-Za-z0-9\s&.,\'-]{2,})',
            r'([A-Z][A-Za-z0-9\s&.\'-]+(?:Inc|LLC|Ltd|Corp|Co|GmbH))',
        ]
        
        for pattern in company_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                company = match.group(1).strip()
                # Clean up company name
                company = re.sub(r'\s*\|.*$', '', company)  # Remove anything after |
                company = re.sub(r'\d{4}.*$', '', company)  # Remove dates
                return company
        
        return ""
    
    def _extract_job_title(self, text: str) -> str:
        """Extract job title"""
        # Title patterns
        title_patterns = [
            r'\|\s*([A-Z][a-zA-Z\s&-]+)\s*\n',  # | Title\n
            r'(?:Title|Role|Position):\s*([^\n\r]+)',
            r'(?:as|a)\s+([A-Z][a-z]+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)',
            r'([A-Z][a-z]+\s+(?:Manager|Director|Engineer|Analyst|Developer|Consultant|Specialist|Lead|Head|Chief))',
        ]
        
        for pattern in title_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                title = match.group(1).strip()
                # Clean up title
                title = re.sub(r'\s*\|.*$', '', title)  # Remove anything after |
                title = re.sub(r'\d{4}.*$', '', title)  # Remove dates
                return title
        
        return ""
    
    def _extract_start_date(self, text: str) -> str:
        """Extract start date"""
        date_patterns = [
            r'(\d{4})\s*-\s*\d{4}',  # 2015-2017
            r'(\w+)\s+\d{4}\s*-\s*\w+\s+\d{4}',  # December 2015 - September 2017
            r'(\w+)\s+\d{4}\s*-\s*Present',  # December 2015 - Present
            r'(\d{1,2}/\d{1,2}/\d{4})\s*-\s*\d{1,2}/\d{1,2}/\d{4}',  # 12/2015 - 09/2017
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return self._normalize_date(match.group(1))
        
        return ""
    
    def _extract_end_date(self, text: str) -> str:
        """Extract end date"""
        if re.search(r'\bPresent\b|\bCurrent\b', text, re.IGNORECASE):
            return None
        
        date_patterns = [
            r'\d{4}\s*-\s*(\d{4})',  # 2015-2017
            r'\w+\s+\d{4}\s*-\s*(\w+\s+\d{4})',  # December 2015 - September 2017
            r'(\d{1,2}/\d{1,2}/\d{4})',  # 09/2017
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return self._normalize_date(match.group(1))
        
        return ""
    
    def _is_current_job(self, text: str) -> bool:
        """Check if current job"""
        return bool(re.search(r'\bPresent\b|\bCurrent\b|\bto\s+now\b', text, re.IGNORECASE))
    
    def _extract_location(self, text: str) -> str:
        """Extract location"""
        location_patterns = [
            r'([A-Z][a-z]+,\s*[A-Z]{2})',  # City, ST
            r'([A-Z][a-z\s]+,\s*[A-Z][a-z\s]+)',  # City, Country
            r'([A-Z][a-z]+,\s*[A-Z]{2,3})',  # City, State/Country
        ]
        
        for pattern in location_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()
        
        return ""
    
    def _extract_employment_type(self, text: str) -> str:
        """Extract employment type"""
        employment_patterns = {
            "Contract": r"contract|consultant|freelance|temporary|1099",
            "Full-time": r"full.?time|permanent|regular|salaried",
            "Part-time": r"part.?time|casual|seasonal|hourly",
            "Internship": r"intern|internship|trainee|co.?op",
            "Freelance": r"freelance|self.?employed|independent"
        }
        
        text_lower = text.lower()
        for emp_type, pattern in employment_patterns.items():
            if re.search(pattern, text_lower):
                return emp_type
        
        return "Full-time"  # Default
    
    def _extract_responsibilities(self, text: str) -> List[str]:
        """Extract responsibilities"""
        responsibilities = []
        
        # Find bullet points
        bullet_patterns = [
            r'[-•*]\s*([^\n\r]+)',  # - bullet, • bullet, * bullet
            r'\n\s*([A-Z][^•\n]*[a-z])',  # Capitalized sentences
        ]
        
        for pattern in bullet_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                resp = match.strip()
                if len(resp) > 10:  # Filter out short fragments
                    responsibilities.append(resp)
        
        return responsibilities[:5]  # Limit to 5 responsibilities
    
    def _extract_tech_stack(self, text: str) -> List[str]:
        """Extract tech stack"""
        tech_stack = []
        
        # Find skills in text
        text_lower = text.lower()
        for skill in self.skills_db:
            if skill.lower() in text_lower:
                tech_stack.append(skill)
        
        # Also look for "Technologies:" section
        tech_section = re.search(r'Technologies?:\s*([^\n\r]+)', text, re.IGNORECASE)
        if tech_section:
            tech_text = tech_section.group(1)
            # Split by commas and common separators
            tech_items = re.split(r'[,;]\s*|\s+and\s+', tech_text)
            for item in tech_items:
                item = item.strip()
                if len(item) > 1:
                    tech_stack.append(item)
        
        return list(set(tech_stack))[:10]  # Limit to 10 unique items
    
    def _calculate_confidence(self, entry: Dict[str, Any]) -> float:
        """Calculate confidence score"""
        score = 0.0
        max_score = 100.0
        
        # Company present (25 points)
        if entry.get("company") and entry.get("company") != "":
            score += 25
        
        # Job title present (25 points)
        if entry.get("job_title") and entry.get("job_title") != "":
            score += 25
        
        # Start date present (20 points)
        if entry.get("start_date") and entry.get("start_date") != "":
            score += 20
        
        # End date or is_current present (15 points)
        if entry.get("end_date") or entry.get("is_current"):
            score += 15
        
        # Responsibilities present (10 points)
        if entry.get("responsibilities") and len(entry.get("responsibilities", [])) > 0:
            score += 10
        
        # Location present (5 points)
        if entry.get("location") and entry.get("location") != "":
            score += 5
        
        return score / max_score
    
    def _get_missing_fields(self, entry: Dict[str, Any]) -> List[str]:
        """Identify missing fields"""
        required_fields = ["company", "job_title", "start_date", "location"]
        missing = []
        
        for field in required_fields:
            if not entry.get(field) or entry.get(field) == "":
                missing.append(field)
        
        return missing
    
    def _normalize_date(self, date_str: str) -> str:
        """Normalize date to YYYY-MM format"""
        if not date_str:
            return ""
        
        try:
            # Handle various date formats
            date_patterns = [
                (r'(\d{4})-(\d{2})', lambda m: f"{m.group(1)}-{m.group(2)}"),  # YYYY-MM
                (r'(\d{4})/(\d{2})', lambda m: f"{m.group(1)}-{m.group(2)}"),  # YYYY/MM
                (r'(\w{3})\s*(\d{4})', lambda m: f"{m.group(2)}-{self._month_to_num(m.group(1))}"),  # Month YYYY
                (r'(\d{4})', lambda m: f"{m.group(1)}-01"),  # YYYY only
            ]
            
            for pattern, converter in date_patterns:
                match = re.search(pattern, date_str)
                if match:
                    return converter(match)
            
            return date_str
            
        except Exception:
            return date_str
    
    def _month_to_num(self, month: str) -> str:
        """Convert month name to number"""
        month_map = {
            'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04',
            'May': '05', 'Jun': '06', 'Jul': '07', 'Aug': '08',
            'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'
        }
        return month_map.get(month[:3], '01')

# Singleton instance
_quick_parser = None

def get_quick_work_parser():
    """Get singleton quick work parser instance"""
    global _quick_parser
    if _quick_parser is None:
        _quick_parser = QuickWorkExperienceParser()
    return _quick_parser
