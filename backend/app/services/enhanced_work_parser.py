#!/usr/bin/env python3
"""
Enhanced Work Experience Parser
Integrates Flan-T5 with existing rule-based approach
"""

import re
import pandas as pd
import os
from typing import Dict, List, Any, Optional
import logging
from .flan_t5_extractor import get_flan_t5_extractor

logger = logging.getLogger(__name__)

class EnhancedWorkExperienceParser:
    """Enhanced work experience parser with Flan-T5 integration"""
    
    def __init__(self):
        self.flan_t5 = get_flan_t5_extractor()
        self.companies_db = self._load_companies_database()
        self.job_titles_db = self._load_job_titles_database()
        self.employment_patterns = self._load_employment_patterns()
    
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
    
    def _load_employment_patterns(self) -> Dict[str, str]:
        """Load employment type patterns"""
        return {
            "contract": r"contract|consultant|freelance|temporary|1099",
            "full-time": r"full.?time|permanent|regular|salaried",
            "part-time": r"part.?time|casual|seasonal|hourly",
            "internship": r"intern|internship|trainee|co.?op",
            "freelance": r"freelance|self.?employed|independent"
        }
    
    def parse_work_experience(self, work_text: str) -> List[Dict[str, Any]]:
        """
        Parse work experience using hybrid approach
        
        Args:
            work_text: Raw work experience text
            
        Returns:
            List of enhanced work experience entries
        """
        try:
            logger.info("🚀 Starting enhanced work experience parsing...")
            
            # Step 1: Try Flan-T5 extraction
            flan_t5_results = self._extract_with_flan_t5(work_text)
            
            # Step 2: Enhance with rule-based validation
            enhanced_results = self._enhance_with_rules(flan_t5_results, work_text)
            
            # Step 3: Apply confidence-based filtering
            final_results = self._apply_confidence_filtering(enhanced_results)
            
            logger.info(f"✅ Parsed {len(final_results)} work experience entries")
            return final_results
            
        except Exception as e:
            logger.error(f"❌ Error parsing work experience: {e}")
            return []
    
    def _extract_with_flan_t5(self, work_text: str) -> List[Dict[str, Any]]:
        """Extract work experience using Flan-T5"""
        try:
            logger.info("🤖 Using Flan-T5 for extraction...")
            return self.flan_t5.extract_work_experience(work_text)
        except Exception as e:
            logger.error(f"❌ Flan-T5 extraction failed: {e}")
            return []
    
    def _enhance_with_rules(self, entries: List[Dict[str, Any]], original_text: str) -> List[Dict[str, Any]]:
        """Enhance Flan-T5 results with rule-based validation"""
        enhanced_entries = []
        
        for entry in entries:
            # Ensure entry is a dictionary
            if isinstance(entry, dict):
                enhanced_entry = entry.copy()
            else:
                # Skip invalid entries
                continue
            
            # Validate and enhance company
            enhanced_entry["company"] = self._validate_company(enhanced_entry.get("company", ""), original_text)
            
            # Validate and enhance job title
            enhanced_entry["job_title"] = self._validate_job_title(enhanced_entry.get("job_title", ""), original_text)
            
            # Extract employment type if missing
            if not enhanced_entry.get("employment_type"):
                enhanced_entry["employment_type"] = self._extract_employment_type(original_text)
            
            # Extract tech stack from responsibilities
            if enhanced_entry.get("responsibilities"):
                enhanced_entry["tech_stack"] = self._extract_tech_stack(enhanced_entry["responsibilities"])
            
            enhanced_entries.append(enhanced_entry)
        
        return enhanced_entries
    
    def _validate_company(self, company: str, original_text: str) -> str:
        """Validate and enhance company name"""
        if not company:
            return self._extract_company_from_text(original_text)
        
        # Check if company matches known companies
        for known_company in self.companies_db:
            if known_company.lower() in company.lower() or company.lower() in known_company.lower():
                return known_company
        
        return company
    
    def _validate_job_title(self, job_title: str, original_text: str) -> str:
        """Validate and enhance job title"""
        if not job_title:
            return self._extract_job_title_from_text(original_text)
        
        # Check if job title matches known titles
        for known_title in self.job_titles_db:
            if known_title.lower() in job_title.lower() or job_title.lower() in known_title.lower():
                return known_title
        
        return job_title
    
    def _extract_company_from_text(self, text: str) -> str:
        """Extract company name from text using patterns"""
        company_patterns = [
            r'(?:Company|Employer|Organization):\s*([^\n\r]+)',
            r'(?:at|@)\s*([A-Z][A-Za-z0-9\s&.,\'-]{2,})',
            r'([A-Z][A-Za-z0-9\s&.\'-]+(?:Inc|LLC|Ltd|Corp|Co|GmbH))',
        ]
        
        for pattern in company_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return ""
    
    def _extract_job_title_from_text(self, text: str) -> str:
        """Extract job title from text using patterns"""
        title_patterns = [
            r'(?:Title|Role|Position):\s*([^\n\r]+)',
            r'(?:as|a)\s+([A-Z][a-z]+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)',
            r'([A-Z][a-z]+\s+(?:Manager|Director|Engineer|Analyst|Developer|Consultant|Specialist|Lead|Head|Chief))',
        ]
        
        for pattern in title_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return ""
    
    def _extract_employment_type(self, text: str) -> str:
        """Extract employment type from text"""
        text_lower = text.lower()
        
        for emp_type, pattern in self.employment_patterns.items():
            if re.search(pattern, text_lower):
                return emp_type.capitalize()
        
        return "Full-time"  # Default assumption
    
    def _extract_tech_stack(self, responsibilities: List[str]) -> List[str]:
        """Extract tech stack from responsibilities"""
        try:
            # Load skills database
            skills_path = "data/external/skills.csv"
            tech_stack = []
            
            if os.path.exists(skills_path):
                df = pd.read_csv(skills_path)
                if 'skill_name' in df.columns:
                    known_skills = set(df['skill_name'].dropna().astype(str).tolist())
                    
                    # Find skills in responsibilities
                    resp_text = " ".join(responsibilities).lower()
                    for skill in known_skills:
                        if skill.lower() in resp_text:
                            tech_stack.append(skill)
            
            return list(set(tech_stack))[:10]  # Limit to top 10
            
        except Exception as e:
            logger.warning(f"⚠️ Could not extract tech stack: {e}")
            return []
    
    def _apply_confidence_filtering(self, entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply confidence-based filtering"""
        filtered_entries = []
        
        for entry in entries:
            confidence = entry.get("confidence", 0.0)
            
            # High confidence: Accept as-is
            if confidence >= 0.8:
                filtered_entries.append(entry)
            
            # Medium confidence: Accept but flag for review
            elif confidence >= 0.5:
                entry["_flagged_for_review"] = True
                filtered_entries.append(entry)
            
            # Low confidence: Reject
            else:
                logger.warning(f"⚠️ Low confidence entry rejected: {entry.get('company', 'Unknown')}")
        
        return filtered_entries

# Singleton instance
_enhanced_parser = None

def get_enhanced_work_parser():
    """Get singleton enhanced work parser instance"""
    global _enhanced_parser
    if _enhanced_parser is None:
        _enhanced_parser = EnhancedWorkExperienceParser()
    return _enhanced_parser
