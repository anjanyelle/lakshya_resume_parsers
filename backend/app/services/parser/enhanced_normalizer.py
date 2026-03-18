"""
Unified Normalization Layer - Uses ALL Datasets Simultaneously
Integrates all existing + external datasets for comprehensive normalization
"""

import re
import logging
from typing import Dict, List, Optional, Tuple, Any
from app.services.parser.utils.enhanced_dataset_loader import unified_loader

logger = logging.getLogger(__name__)

class UnifiedNormalizer:
    """
    Unified normalization layer that uses ALL datasets (existing + external)
    simultaneously for comprehensive data normalization.
    
    No priority - all datasets contribute equally for maximum coverage.
    """
    
    def __init__(self):
        self.loader = unified_loader
        self._compile_normalization_patterns()
        
        logger.info("Unified Normalizer initialized")
        logger.info(f"Using ALL unified datasets for normalization")
    
    def _compile_normalization_patterns(self):
        """Compile patterns for fuzzy matching across ALL datasets"""
        # Common company suffixes to normalize
        self.company_suffixes = [
            r'\b(?:inc|llc|ltd|corp|corporation|company|technologies|systems|health|bank|solutions|services)\b',
            r'\b(?:(?:inc|llc|ltd|corp)\.?)(?:\s+(?:of|and|&))?\s*',
            r'\b(?:pvt|private|ltd|limited)\b',
        ]
        
        # Common job title prefixes/suffixes
        self.title_prefixes = [
            r'^(?:senior|sr|junior|jr|lead|principal|associate|assistant|staff)\s+',
            r'^(?:assistant|associate|senior|lead|principal|chief|head|director|manager)\s+',
        ]
        
        # Degree patterns
        self.degree_patterns = [
            r'\b(?:bachelor|master|ph\.?d|mba|b\.?s|m\.?s|b\.?tech|m\.?tech)\b',
            r'\b(?:b\.?sc|m\.?sc|b\.?a|m\.?a)\b',
            r'\b(?:engineer|engineering|science|arts|business|administration)\b',
        ]
        
        # Location patterns
        self.location_patterns = [
            r'\b(?:usa|united\s+states|america)\b',
            r'\b(?:uk|united\s+kingdom|britain)\b',
            r'\b(?:india|bharat)\b',
        ]
    
    def normalize_company_name(self, company_name: str) -> str:
        """
        Normalize company name using ALL unified datasets
        No priority - uses best match from any source
        """
        if not company_name or not company_name.strip():
            return company_name
        
        original = company_name.strip()
        
        # Step 1: Try exact match in ALL unified datasets
        unified_lookup = self.loader.lookup_company(original)
        if unified_lookup:
            for field in ['normalized_name', 'name']:
                if unified_lookup.get(field):
                    sources = unified_lookup.get('_all_sources', ['unknown'])
                    logger.debug(f"Company normalized using unified datasets: {original} -> {unified_lookup[field]} from sources: {sources}")
                    return unified_lookup[field]
        
        # Step 2: Apply pattern-based normalization
        normalized = self._apply_company_patterns(original)
        
        # Step 3: Try fuzzy matching in ALL unified datasets
        fuzzy_match = self._fuzzy_company_match_all_datasets(original)
        if fuzzy_match:
            logger.debug(f"Company normalized using fuzzy match: {original} -> {fuzzy_match}")
            return fuzzy_match
        
        return normalized
    
    def _apply_company_patterns(self, company_name: str) -> str:
        """Apply common company normalization patterns"""
        normalized = company_name
        
        # Remove common suffixes and normalize
        for suffix_pattern in self.company_suffixes:
            normalized = re.sub(suffix_pattern, '', normalized, flags=re.IGNORECASE)
        
        # Clean up extra spaces and punctuation
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        normalized = re.sub(r'[,.–—]+$', '', normalized)
        
        # Capitalize properly
        normalized = ' '.join(word.capitalize() for word in normalized.split())
        
        return normalized
    
    def _fuzzy_company_match_all_datasets(self, company_name: str) -> Optional[str]:
        """Fuzzy matching across ALL unified datasets"""
        companies = self.loader.get_unified_dataset('companies')
        company_lower = company_name.lower()
        
        # Remove common words for comparison
        cleaned_input = re.sub(r'\b(?:inc|llc|ltd|corp|corporation)\b', '', company_lower).strip()
        
        best_match = None
        best_score = 0
        
        for company in companies:
            for field in ['name', 'normalized_name']:
                candidate = company.get(field, '')
                if not candidate:
                    continue
                
                candidate_lower = candidate.lower()
                cleaned_candidate = re.sub(r'\b(?:inc|llc|ltd|corp|corporation)\b', '', candidate_lower).strip()
                
                # Calculate similarity score
                if cleaned_input == cleaned_candidate:
                    score = 1.0
                elif cleaned_input in cleaned_candidate or cleaned_candidate in cleaned_input:
                    score = 0.8
                else:
                    # Simple word overlap scoring
                    input_words = set(cleaned_input.split())
                    candidate_words = set(cleaned_candidate.split())
                    overlap = len(input_words & candidate_words)
                    total = len(input_words | candidate_words)
                    score = overlap / total if total > 0 else 0
                
                if score > best_score and score >= 0.6:  # Minimum threshold
                    best_score = score
                    best_match = candidate
                    sources = company.get('_all_sources', ['unknown'])
                    logger.debug(f"Fuzzy match found: {company_name} -> {candidate} from sources: {sources}")
        
        return best_match
    
    def normalize_job_title(self, job_title: str) -> str:
        """
        Normalize job title using ALL unified datasets
        No priority - uses best match from any source
        """
        if not job_title or not job_title.strip():
            return job_title
        
        original = job_title.strip()
        
        # Step 1: Try exact match in ALL unified datasets
        unified_lookup = self.loader.lookup_job_title(original)
        if unified_lookup:
            for field in ['normalized_title', 'title']:
                if unified_lookup.get(field):
                    sources = unified_lookup.get('_all_sources', ['unknown'])
                    logger.debug(f"Job title normalized using unified datasets: {original} -> {unified_lookup[field]} from sources: {sources}")
                    return unified_lookup[field]
        
        # Step 2: Apply pattern-based normalization
        normalized = self._apply_title_patterns(original)
        
        # Step 3: Try fuzzy matching in ALL unified datasets
        fuzzy_match = self._fuzzy_title_match_all_datasets(original)
        if fuzzy_match:
            logger.debug(f"Job title normalized using fuzzy match: {original} -> {fuzzy_match}")
            return fuzzy_match
        
        return normalized
    
    def _apply_title_patterns(self, job_title: str) -> str:
        """Apply common job title normalization patterns"""
        normalized = job_title
        
        # Normalize common abbreviations
        abbreviations = {
            r'\bsr\b': 'Senior',
            r'\bjr\b': 'Junior',
            r'\bvp\b': 'Vice President',
            r'\bcto\b': 'Chief Technology Officer',
            r'\bcfo\b': 'Chief Financial Officer',
            r'\bceo\b': 'Chief Executive Officer',
            r'\bsde\b': 'Software Development Engineer',
            r'\bqa\b': 'Quality Assurance',
        }
        
        for pattern, replacement in abbreviations.items():
            normalized = re.sub(pattern, replacement, normalized, flags=re.IGNORECASE)
        
        # Clean up prefixes
        for prefix_pattern in self.title_prefixes:
            normalized = re.sub(prefix_pattern, '', normalized, flags=re.IGNORECASE)
        
        # Capitalize properly
        normalized = ' '.join(word.capitalize() for word in normalized.split())
        
        return normalized
    
    def _fuzzy_title_match_all_datasets(self, job_title: str) -> Optional[str]:
        """Fuzzy matching across ALL unified datasets"""
        job_titles = self.loader.get_unified_dataset('job_titles')
        title_lower = job_title.lower()
        
        best_match = None
        best_score = 0
        
        for title in job_titles:
            for field in ['title', 'normalized_title']:
                candidate = title.get(field, '')
                if not candidate:
                    continue
                
                candidate_lower = candidate.lower()
                
                # Calculate similarity score
                if title_lower == candidate_lower:
                    score = 1.0
                elif title_lower in candidate_lower or candidate_lower in title_lower:
                    score = 0.8
                else:
                    # Word overlap scoring
                    input_words = set(title_lower.split())
                    candidate_words = set(candidate_lower.split())
                    overlap = len(input_words & candidate_words)
                    total = len(input_words | candidate_words)
                    score = overlap / total if total > 0 else 0
                
                if score > best_score and score >= 0.6:  # Minimum threshold
                    best_score = score
                    best_match = candidate
                    sources = title.get('_all_sources', ['unknown'])
                    logger.debug(f"Fuzzy title match found: {job_title} -> {candidate} from sources: {sources}")
        
        return best_match
    
    def normalize_education(self, institution: str, degree: str = None) -> Tuple[str, Optional[str]]:
        """
        Normalize education institution and degree using ALL unified datasets
        Returns: (normalized_institution, normalized_degree)
        """
        normalized_institution = institution
        normalized_degree = degree
        
        # Normalize institution using ALL unified datasets
        if institution and institution.strip():
            # Step 1: Try exact match in ALL unified datasets
            edu_lookup = self.loader.lookup_education(institution)
            if edu_lookup:
                for field in ['normalized_institution', 'institution']:
                    if edu_lookup.get(field):
                        normalized_institution = edu_lookup[field]
                        sources = edu_lookup.get('_all_sources', ['unknown'])
                        logger.debug(f"Institution normalized using unified datasets: {institution} -> {normalized_institution} from sources: {sources}")
                        break
            
            # Step 2: Apply pattern-based normalization
            if normalized_institution == institution:  # Only if no exact match found
                normalized_institution = self._apply_education_patterns(normalized_institution)
        
        # Normalize degree
        if degree and degree.strip():
            normalized_degree = self._normalize_degree(degree)
        
        return normalized_institution, normalized_degree
    
    def _apply_education_patterns(self, institution: str) -> str:
        """Apply education-specific normalization patterns"""
        normalized = institution
        
        # Remove common educational suffixes
        edu_suffixes = [
            r'\b(?:university|college|institute|institute\s+of\s+technology)\b',
            r'\b(?:school\s+of\s+(?:business|engineering|arts|science))\b',
        ]
        
        for suffix_pattern in edu_suffixes:
            normalized = re.sub(suffix_pattern, '', normalized, flags=re.IGNORECASE)
        
        # Clean up and capitalize
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        normalized = ' '.join(word.capitalize() for word in normalized.split())
        
        return normalized
    
    def _normalize_degree(self, degree: str) -> str:
        """Normalize degree names"""
        normalized = degree.strip()
        
        # Apply degree patterns
        for pattern in self.degree_patterns:
            matches = re.findall(pattern, normalized, re.IGNORECASE)
            if matches:
                # Keep the matched pattern and normalize case
                for match in matches:
                    normalized = re.sub(match, match.capitalize(), normalized, flags=re.IGNORECASE)
        
        return normalized
    
    def normalize_location(self, location: str) -> str:
        """
        Normalize location using ALL unified datasets
        No priority - uses best match from any source
        """
        if not location or not location.strip():
            return location
        
        normalized = location.strip()
        
        # Step 1: Try exact match in ALL unified datasets
        location_lookup = self.loader.lookup_location(normalized)
        if location_lookup:
            # Combine city, state, country if available
            parts = []
            for field in ['city', 'state', 'country']:
                value = location_lookup.get(field)
                if value:
                    parts.append(value)
            
            if parts:
                result = ', '.join(parts)
                sources = location_lookup.get('_all_sources', ['unknown'])
                logger.debug(f"Location normalized using unified datasets: {location} -> {result} from sources: {sources}")
                return result
        
        # Step 2: Apply pattern-based normalization
        normalized = self._apply_location_patterns(normalized)
        
        return normalized
    
    def _apply_location_patterns(self, location: str) -> str:
        """Apply location-specific normalization patterns"""
        normalized = location
        
        # Normalize country names
        country_mappings = {
            r'\b(?:usa|united\s+states)\b': 'United States',
            r'\b(?:uk|united\s+kingdom)\b': 'United Kingdom',
            r'\bindia\b': 'India',
        }
        
        for pattern, replacement in country_mappings.items():
            normalized = re.sub(pattern, replacement, normalized, flags=re.IGNORECASE)
        
        # Clean up formatting
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        
        # Ensure proper capitalization
        normalized = ', '.join(word.capitalize() for word in normalized.split(', '))
        
        return normalized
    
    def normalize_date(self, date_str: str) -> str:
        """Normalize date strings"""
        if not date_str or not date_str.strip():
            return date_str
        
        normalized = date_str.strip()
        
        # Common date format normalizations
        date_patterns = [
            (r'(\d{1,2})[/\-\.](\d{2,4})', r'\1/\2'),  # Normalize separators
            (r'(\w+)\s+(\d{4})', r'\1 \2'),  # Month Year format
            (r'present|current|till\s+date|now', 'Present'),  # Normalize present dates
        ]
        
        for pattern, replacement in date_patterns:
            normalized = re.sub(pattern, replacement, normalized, flags=re.IGNORECASE)
        
        return normalized
    
    def normalize_skill(self, skill_name: str) -> str:
        """
        Normalize skill names using ALL unified datasets
        No priority - uses best match from any source
        """
        if not skill_name or not skill_name.strip():
            return skill_name
        
        # Step 1: Try exact match in ALL unified datasets
        skill_lookup = self.loader.lookup_skill(skill_name)
        if skill_lookup:
            for field in ['name', 'skill_name']:
                if skill_lookup.get(field):
                    sources = skill_lookup.get('_all_sources', ['unknown'])
                    logger.debug(f"Skill normalized using unified datasets: {skill_name} -> {skill_lookup[field]} from sources: {sources}")
                    return skill_lookup[field]
        
        # Step 2: Apply pattern-based normalization
        normalized = skill_name.strip()
        normalized = re.sub(r'\s+', ' ', normalized)  # Normalize spaces
        normalized = normalized.capitalize()  # Capitalize properly
        
        return normalized
    
    def normalize_certification(self, cert_name: str) -> str:
        """
        Normalize certification names using ALL unified datasets
        No priority - uses best match from any source
        """
        if not cert_name or not cert_name.strip():
            return cert_name
        
        # Step 1: Try exact match in ALL unified datasets
        cert_lookup = self.loader.lookup_certification(cert_name)
        if cert_lookup:
            for field in ['name', 'certification']:
                if cert_lookup.get(field):
                    sources = cert_lookup.get('_all_sources', ['unknown'])
                    logger.debug(f"Certification normalized using unified datasets: {cert_name} -> {cert_lookup[field]} from sources: {sources}")
                    return cert_lookup[field]
        
        # Step 2: Apply basic normalization
        normalized = cert_name.strip()
        normalized = re.sub(r'\s+', ' ', normalized)  # Normalize spaces
        normalized = ' '.join(word.capitalize() for word in normalized.split())  # Capitalize properly
        
        return normalized
    
    def get_unified_normalization_stats(self) -> Dict[str, Any]:
        """Get comprehensive statistics about unified normalization performance"""
        dataset_stats = self.loader.get_unified_dataset_stats()
        
        return {
            'datasets_loaded': len(dataset_stats),
            'normalization_patterns': {
                'company_suffixes': len(self.company_suffixes),
                'title_prefixes': len(self.title_prefixes),
                'degree_patterns': len(self.degree_patterns),
                'location_patterns': len(self.location_patterns)
            },
            'dataset_stats': dataset_stats,
            'total_unified_entries': sum(stats.get('total_unique_entries', 0) for stats in dataset_stats.values())
        }

# Global instance
unified_normalizer = UnifiedNormalizer()
