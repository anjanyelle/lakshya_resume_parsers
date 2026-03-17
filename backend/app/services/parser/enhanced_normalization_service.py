"""
Enhanced Normalization Service for Resume Parser
Leverages expanded external datasets for improved accuracy
"""

import os
import csv
import re
import logging
from typing import Dict, Optional, List, Tuple
from difflib import SequenceMatcher
from rapidfuzz import fuzz, process

logger = logging.getLogger(__name__)

class EnhancedNormalizationService:
    """
    Enhanced normalization service using external datasets with fuzzy matching
    and intelligent pattern recognition for better resume parsing accuracy.
    """
    
    def __init__(self):
        self.companies_data = self._load_companies_data()
        self.job_titles_data = self._load_job_titles_data()
        self.skills_data = self._load_skills_data()
        self.education_data = self._load_education_data()
        self.locations_data = self._load_locations_data()
        
        # Build fuzzy matching indexes
        self.company_index = self._build_company_index()
        self.job_title_index = self._build_job_title_index()
        self.university_index = self._build_university_index()
        
        logger.info("Enhanced Normalization Service initialized with expanded datasets")
    
    def _get_project_root(self) -> str:
        """Get the project root directory"""
        base_dir = os.path.dirname(__file__)
        return os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(base_dir))))
    
    def _load_companies_data(self) -> Dict:
        """Load companies data from multiple CSV files"""
        companies = {}
        
        company_files = [
            ("data/external/companies/fortune500_companies/csv/fortune500-2019.csv", "fortune500"),
            ("data/external/companies/startups_companies.csv", "startups"),
            ("data/external/companies/consulting_companies.csv", "consulting"),
            ("data/external/companies/healthcare_companies.csv", "healthcare")
        ]
        
        try:
            project_root = self._get_project_root()
            
            for csv_file, file_type in company_files:
                csv_path = os.path.join(project_root, csv_file)
                if not os.path.exists(csv_path):
                    logger.warning(f"Company file not found: {csv_path}")
                    continue
                    
                with open(csv_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        if file_type == "fortune500":
                            company_name = row['company'].strip().lower()
                            companies[company_name] = {
                                'name': row['company'].strip(),
                                'type': 'fortune500',
                                'rank': int(row['rank']),
                                'revenue': float(row['revenue ($ millions)'] or 0),
                                'profit': float(row['profit ($ millions)'] or 0)
                            }
                        elif file_type in ["startups", "consulting", "healthcare"]:
                            company_name = row.get('company', row.get('normalized_company', '')).strip().lower()
                            if company_name:
                                companies[company_name] = {
                                    'name': row.get('company', row.get('normalized_company', '')).strip(),
                                    'type': file_type,
                                    'normalized_company': row.get('normalized_company', '').strip(),
                                    'industry': row.get('industry', '').strip(),
                                    'specialization': row.get('specialization', '').strip(),
                                    'employee_count': row.get('employee_count', '').strip(),
                                    'headquarters': row.get('headquarters', '').strip(),
                                    'funding_stage': row.get('funding_stage', '').strip()
                                }
        except Exception as e:
            logger.warning(f"Could not load companies data: {e}")
        
        logger.info(f"Loaded {len(companies)} companies from external datasets")
        return companies
    
    def _load_job_titles_data(self) -> Dict:
        """Load job titles data from CSV"""
        job_titles = {}
        try:
            project_root = self._get_project_root()
            csv_path = os.path.join(project_root, "data/external/job_titles.csv")
            
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    job_titles[row['raw_title'].strip().lower()] = {
                        'normalized': row['normalized_title'].strip(),
                        'category': row['category'].strip()
                    }
        except Exception as e:
            logger.warning(f"Could not load job titles data: {e}")
        
        logger.info(f"Loaded {len(job_titles)} job titles from external dataset")
        return job_titles
    
    def _load_skills_data(self) -> Dict:
        """Load skills data from CSV"""
        skills = {}
        try:
            project_root = self._get_project_root()
            csv_path = os.path.join(project_root, "data/external/skills.csv")
            
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    skills[row['skill_name'].strip().lower()] = {
                        'category': row['category'].strip(),
                        'subcategory': row['subcategory'].strip(),
                        'level': row['level'].strip()
                    }
        except Exception as e:
            logger.warning(f"Could not load skills data: {e}")
        
        logger.info(f"Loaded {len(skills)} skills from external dataset")
        return skills
    
    def _load_education_data(self) -> Dict:
        """Load education data from CSV"""
        education = {}
        try:
            project_root = self._get_project_root()
            csv_path = os.path.join(project_root, "data/external/education.csv")
            
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    institution_name = row['institution'].strip().lower()
                    education[institution_name] = {
                        'name': row['institution'].strip(),
                        'normalized': row['normalized_institution'].strip(),
                        'type': row['type'].strip(),
                        'country': row['country'].strip(),
                        'state': row['state'].strip(),
                        'city': row['city'].strip(),
                        'ranking': row.get('ranking', '').strip()
                    }
        except Exception as e:
            logger.warning(f"Could not load education data: {e}")
        
        logger.info(f"Loaded {len(education)} education institutions from external dataset")
        return education
    
    def _load_locations_data(self) -> Dict:
        """Load locations data from CSV"""
        locations = {}
        try:
            project_root = self._get_project_root()
            csv_path = os.path.join(project_root, "data/external/locations.csv")
            
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    city_state = f"{row['city'].strip()}, {row['state'].strip()}"
                    locations[city_state.lower()] = {
                        'city': row['city'].strip(),
                        'state': row['state'].strip(),
                        'country': row['country'].strip(),
                        'country_code': row['country_code'].strip(),
                        'latitude': float(row['latitude']),
                        'longitude': float(row['longitude'])
                    }
                    # Also add city only for matching
                    locations[row['city'].strip().lower()] = {
                        'city': row['city'].strip(),
                        'state': row['state'].strip(),
                        'country': row['country'].strip(),
                        'country_code': row['country_code'].strip(),
                        'latitude': float(row['latitude']),
                        'longitude': float(row['longitude'])
                    }
        except Exception as e:
            logger.warning(f"Could not load locations data: {e}")
        
        logger.info(f"Loaded {len(locations)} locations from external dataset")
        return locations
    
    def _build_company_index(self) -> List[str]:
        """Build index for fuzzy company matching"""
        return list(self.companies_data.keys())
    
    def _build_job_title_index(self) -> List[str]:
        """Build index for fuzzy job title matching"""
        return list(self.job_titles_data.keys())
    
    def _build_university_index(self) -> List[str]:
        """Build index for fuzzy university matching"""
        return list(self.education_data.keys())
    
    def normalize_company_name(self, name: str, use_fuzzy: bool = True) -> Tuple[str, float]:
        """
        Normalize company name with fuzzy matching support
        
        Args:
            name: Raw company name
            use_fuzzy: Whether to use fuzzy matching for unknown companies
            
        Returns:
            Tuple of (normalized_name, confidence_score)
        """
        if not name:
            return None, 0.0
        
        name_lower = name.strip().lower()
        
        # Exact match first
        if name_lower in self.companies_data:
            company_data = self.companies_data[name_lower]
            normalized = company_data.get('normalized_company', company_data['name'])
            return normalized, 1.0
        
        # Try common variations and cleanup
        cleaned_name = self._clean_company_name(name)
        cleaned_lower = cleaned_name.lower()
        
        if cleaned_lower in self.companies_data:
            company_data = self.companies_data[cleaned_lower]
            normalized = company_data.get('normalized_company', company_data['name'])
            return normalized, 0.95
        
        # Fuzzy matching for unknown companies
        if use_fuzzy and self.company_index:
            result = process.extractOne(
                cleaned_name, 
                self.company_index,
                scorer=fuzz.token_set_ratio,
                score_cutoff=70
            )
            
            if result:
                match_name, score, _ = result
                company_data = self.companies_data[match_name]
                normalized = company_data.get('normalized_company', company_data['name'])
                return normalized, score / 100.0
        
        return cleaned_name, 0.5
    
    def _clean_company_name(self, name: str) -> str:
        """Clean company name for better matching"""
        # Remove common suffixes and prefixes
        suffixes = [
            r'\s+(inc|llc|corp|corporation|ltd|limited|co|company|group|holdings|international|global|worldwide)$',
            r'\s+(technologies|solutions|systems|services|consulting|partners|associates)$',
            r'\.com$'
        ]
        
        prefixes = [
            r'^the\s+'
        ]
        
        cleaned = name.strip()
        
        # Remove suffixes
        for suffix in suffixes:
            cleaned = re.sub(suffix, '', cleaned, flags=re.IGNORECASE)
        
        # Remove prefixes  
        for prefix in prefixes:
            cleaned = re.sub(prefix, '', cleaned, flags=re.IGNORECASE)
        
        # Clean up extra whitespace
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        return cleaned
    
    def normalize_job_title(self, title: str, use_fuzzy: bool = True) -> Tuple[str, str, float]:
        """
        Normalize job title with seniority detection and fuzzy matching
        
        Args:
            title: Raw job title
            use_fuzzy: Whether to use fuzzy matching
            
        Returns:
            Tuple of (normalized_title, category, confidence_score)
        """
        if not title:
            return None, None, 0.0
        
        title_lower = title.strip().lower()
        
        # Exact match first
        if title_lower in self.job_titles_data:
            job_data = self.job_titles_data[title_lower]
            return job_data['normalized'], job_data['category'], 1.0
        
        # Extract and normalize seniority
        cleaned_title, seniority = self._extract_seniority(title)
        
        # Try cleaned title
        cleaned_lower = cleaned_title.lower()
        if cleaned_lower in self.job_titles_data:
            job_data = self.job_titles_data[cleaned_lower]
            normalized = self._apply_seniority(job_data['normalized'], seniority)
            return normalized, job_data['category'], 0.95
        
        # Fuzzy matching
        if use_fuzzy and self.job_title_index:
            result = process.extractOne(
                cleaned_title,
                self.job_title_index,
                scorer=fuzz.token_set_ratio,
                score_cutoff=70
            )
            
            if result:
                match_name, score, _ = result
                job_data = self.job_titles_data[match_name]
                normalized = self._apply_seniority(job_data['normalized'], seniority)
                return normalized, job_data['category'], score / 100.0
        
        # Fallback with seniority detection
        return self._apply_seniority(cleaned_title, seniority), "General", 0.5
    
    def _extract_seniority(self, title: str) -> Tuple[str, str]:
        """Extract seniority level from job title"""
        seniority_patterns = {
            'senior': r'\b(senior|sr|sr\.|lead|principal|staff|head)\b',
            'junior': r'\b(junior|jr|jr\.|associate|assistant|intern|trainee)\b',
            'executive': r'\b(chief|c[ -]?[a-z]+o|vice president|vp|director|manager)\b'
        }
        
        title_lower = title.lower()
        detected_seniority = None
        
        for seniority, pattern in seniority_patterns.items():
            if re.search(pattern, title_lower):
                detected_seniority = seniority
                # Remove seniority indicators from title
                title = re.sub(pattern, '', title, flags=re.IGNORECASE)
                break
        
        return title.strip(), detected_seniority
    
    def _apply_seniority(self, title: str, seniority: str) -> str:
        """Apply seniority prefix to normalized title"""
        if not seniority:
            return title
        
        seniority_mapping = {
            'senior': 'Senior',
            'junior': 'Junior',
            'executive': 'Executive'
        }
        
        prefix = seniority_mapping.get(seniority, seniority.title())
        
        # Avoid double prefixes
        if title.startswith(prefix):
            return title
        
        return f"{prefix} {title}"
    
    def normalize_education_institution(self, name: str, use_fuzzy: bool = True) -> Tuple[str, float]:
        """
        Normalize education institution with abbreviation handling and fuzzy matching
        
        Args:
            name: Raw institution name
            use_fuzzy: Whether to use fuzzy matching
            
        Returns:
            Tuple of (normalized_name, confidence_score)
        """
        if not name:
            return None, 0.0
        
        name_lower = name.strip().lower()
        
        # Exact match first
        if name_lower in self.education_data:
            return self.education_data[name_lower]['normalized'], 1.0
        
        # Check abbreviation mappings
        abbreviations = {
            'mit': 'Massachusetts Institute of Technology',
            'caltech': 'California Institute of Technology',
            'ucla': 'University of California Los Angeles',
            'uc berkeley': 'University of California Berkeley',
            'ucsd': 'University of California San Diego',
            'uc davis': 'University of California Davis',
            'uc irvine': 'University of California Irvine',
            'ucsb': 'University of California Santa Barbara',
            'ucr': 'University of California Riverside',
            'ucsc': 'University of California Santa Cruz',
            'ut austin': 'University of Texas Austin',
            'ut dallas': 'University of Texas Dallas',
            'uw madison': 'University of Wisconsin Madison',
            'um ann arbor': 'University of Michigan Ann Arbor',
            'uiuc': 'University of Illinois Urbana-Champaign',
            'unc chapel hill': 'University of North Carolina Chapel Hill',
            'um twin cities': 'University of Minnesota Twin Cities',
            'cu boulder': 'University of Colorado Boulder',
            'umd college park': 'University of Maryland College Park',
            'ua tucson': 'University of Arizona',
            'uf gainesville': 'University of Florida',
            'uva charlottesville': 'University of Virginia',
            'u utah': 'University of Utah',
            'upitt': 'University of Pittsburgh',
            'bu boston': 'Boston University',
            'osu columbus': 'Ohio State University',
            'uga athens': 'University of Georgia',
            'ua tuscaloosa': 'University of Alabama',
            'stanford': 'Stanford University',
            'harvard': 'Harvard University',
            'yale': 'Yale University',
            'princeton': 'Princeton University',
            'columbia': 'Columbia University',
            'upenn': 'University of Pennsylvania',
            'brown': 'Brown University',
            'dartmouth': 'Dartmouth College',
            'cornell': 'Cornell University',
            'nyu': 'New York University',
            'northwestern': 'Northwestern University',
            'duke': 'Duke University',
            'vanderbilt': 'Vanderbilt University',
            'rice': 'Rice University',
            'emory': 'Emory University',
            'georgetown': 'Georgetown University',
            'oxford': 'University of Oxford',
            'cambridge': 'University of Cambridge',
            'ucl': 'University College London',
            'imperial': 'Imperial College London',
            'edinburgh': 'University of Edinburgh',
            'eth zurich': 'ETH Zurich',
            'nus': 'National University of Singapore',
            'toronto': 'University of Toronto',
            'ubc': 'University of British Columbia',
            'mcgill': 'McGill University',
            'hku': 'University of Hong Kong',
            'unsw': 'University of New South Wales',
            'uq': 'University of Queensland',
            'melbourne': 'University of Melbourne',
            'sydney': 'University of Sydney',
            'anu': 'Australian National University',
            'tsinghua': 'Tsinghua University',
            'peking': 'Peking University',
            'tokyo': 'University of Tokyo'
        }
        
        if name_lower in abbreviations:
            normalized_name = abbreviations[name_lower]
            if normalized_name.lower() in self.education_data:
                return self.education_data[normalized_name.lower()]['normalized'], 0.95
        
        # Fuzzy matching
        if use_fuzzy and self.university_index:
            result = process.extractOne(
                name,
                self.university_index,
                scorer=fuzz.token_set_ratio,
                score_cutoff=70
            )
            
            if result:
                match_name, score, _ = result
                return self.education_data[match_name]['normalized'], score / 100.0
        
        return name.strip(), 0.5
    
    def validate_skill(self, skill: str) -> Tuple[bool, Dict]:
        """
        Validate and categorize skill
        
        Args:
            skill: Skill name to validate
            
        Returns:
            Tuple of (is_valid, skill_data)
        """
        if not skill:
            return False, {}
        
        skill_lower = skill.strip().lower()
        
        if skill_lower in self.skills_data:
            return True, self.skills_data[skill_lower]
        
        # Try fuzzy matching for similar skills
        skill_list = list(self.skills_data.keys())
        result = process.extractOne(
            skill,
            skill_list,
            scorer=fuzz.token_set_ratio,
            score_cutoff=80
        )
        
        if result:
            match_name, score, _ = result
            return True, self.skills_data[match_name]
        
        return False, {}
    
    def normalize_location(self, location: str) -> Tuple[str, float]:
        """
        Normalize location with validation
        
        Args:
            location: Raw location string
            
        Returns:
            Tuple of (normalized_location, confidence_score)
        """
        if not location:
            return None, 0.0
        
        location_lower = location.strip().lower()
        
        # Direct match
        if location_lower in self.locations_data:
            loc_data = self.locations_data[location_lower]
            normalized = f"{loc_data['city']}, {loc_data['state']}"
            return normalized, 1.0
        
        # Try city only
        if location_lower in self.locations_data:
            loc_data = self.locations_data[location_lower]
            normalized = f"{loc_data['city']}, {loc_data['state']}"
            return normalized, 0.9
        
        # Try fuzzy matching on city names
        cities = [loc['city'] for loc in self.locations_data.values()]
        result = process.extractOne(
            location,
            cities,
            scorer=fuzz.token_set_ratio,
            score_cutoff=70
        )
        
        if result:
            match_city, score, _ = result
            # Find the state for this city
            for loc_data in self.locations_data.values():
                if loc_data['city'].lower() == match_city.lower():
                    normalized = f"{loc_data['city']}, {loc_data['state']}"
                    return normalized, score / 100.0
        
        return location.strip(), 0.5
    
    def get_statistics(self) -> Dict:
        """Get statistics about loaded datasets"""
        return {
            'companies': {
                'total': len(self.companies_data),
                'fortune500': len([c for c in self.companies_data.values() if c.get('type') == 'fortune500']),
                'startups': len([c for c in self.companies_data.values() if c.get('type') == 'startups']),
                'consulting': len([c for c in self.companies_data.values() if c.get('type') == 'consulting']),
                'healthcare': len([c for c in self.companies_data.values() if c.get('type') == 'healthcare'])
            },
            'job_titles': len(self.job_titles_data),
            'skills': len(self.skills_data),
            'education': len(self.education_data),
            'locations': len(self.locations_data)
        }
