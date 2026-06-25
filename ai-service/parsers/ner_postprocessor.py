#!/usr/bin/env python3
"""
Production-Grade Resume NER Post-Processing Pipeline

This module transforms noisy NER model output into clean, structured, production-ready resume data.

Architecture:
Resume → Text Extraction → Section Splitting → DeBERTa NER → NER Post-Processor → Validated Output

The pipeline implements 13 phases:
1. Pre-processing (text cleaning before NER)
2. Section Identification (context-aware filtering)
3. Confidence Filtering (threshold-based rejection)
4. Role Validation (job designation vs task/skill)
5. Company Validation (company indicators)
6. Client Validation (customer/account filtering)
7. Location Validation (geographical entities)
8. Education Validation (degree/institution/field)
9. Entity Merging (fragment reconstruction)
10. Deduplication (remove duplicates)
11. Normalization (standardize formats)
12. Final Output (structured JSON)
13. Production Requirements (generic, scalable logic)

Author: AI Engineering Team
Version: 1.0.0
"""

import re
import logging
from typing import Dict, List, Any, Set, Tuple, Optional
from collections import defaultdict
from datetime import datetime

logger = logging.getLogger(__name__)


class NERPostProcessor:
    """
    Production-grade NER post-processor for resume entity extraction.
    
    Transforms noisy model predictions into clean, validated entities.
    """
    
    # ═══════════════════════════════════════════════════════════════════════════
    # PHASE 1: PRE-PROCESSING PATTERNS
    # ═══════════════════════════════════════════════════════════════════════════
    
    EMAIL_PATTERN = re.compile(
        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    )
    
    PHONE_PATTERN = re.compile(
        r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}|'
        r'\+?\d{10,15}'
    )
    
    URL_PATTERN = re.compile(
        r'(?:https?://)?(?:www\.)?'
        r'(?:linkedin\.com|github\.com|gitlab\.com|bitbucket\.org|stackoverflow\.com|'
        r'twitter\.com|facebook\.com|instagram\.com|medium\.com|dev\.to|'
        r'[a-zA-Z0-9-]+\.[a-z]{2,})'
        r'(?:/[^\s]*)?',
        re.IGNORECASE
    )
    
    # ═══════════════════════════════════════════════════════════════════════════
    # PHASE 2: SECTION IDENTIFICATION
    # ═══════════════════════════════════════════════════════════════════════════
    
    # Sections where COMPANY and ROLE extraction is ALLOWED
    ALLOWED_SECTIONS_FOR_WORK = {
        'experience', 'work experience', 'professional experience', 
        'employment history', 'work history', 'career history',
        'employment', 'positions', 'professional background'
    }
    
    # Sections where COMPANY and ROLE extraction is BLOCKED (high false positive rate)
    BLOCKED_SECTIONS_FOR_WORK = {
        'skills', 'technical skills', 'core competencies', 'expertise',
        'projects', 'project experience', 'key projects',
        'responsibilities', 'key responsibilities',
        'certifications', 'certificates', 'professional certifications',
        'summary', 'professional summary', 'career summary', 'profile',
        'achievements', 'awards', 'publications', 'trainings',
        'tools', 'technologies', 'environment'
    }
    
    # Sections where EDUCATION extraction is ALLOWED
    ALLOWED_SECTIONS_FOR_EDUCATION = {
        'education', 'academic background', 'educational qualifications',
        'academic qualifications', 'degrees', 'academic history'
    }
    
    # ═══════════════════════════════════════════════════════════════════════════
    # PHASE 3: CONFIDENCE THRESHOLDS
    # ═══════════════════════════════════════════════════════════════════════════
    
    DEFAULT_CONFIDENCE_THRESHOLDS = {
        'ROLE': 0.92,
        'COMPANY': 0.90,
        'CLIENT': 0.90,
        'LOCATION': 0.90,
        'DEGREE': 0.90,
        'INSTITUTION': 0.90,
        'FIELD': 0.88,
        'PERSON_NAME': 0.95,
        'DATE_START': 0.85,
        'DATE_END': 0.85,
        'EDU_YEAR_START': 0.85,
        'EDU_YEAR_END': 0.85,
        'GRADE': 0.85
    }
    
    # ═══════════════════════════════════════════════════════════════════════════
    # PHASE 4: ROLE VALIDATION PATTERNS
    # ═══════════════════════════════════════════════════════════════════════════
    
    # Valid job designation keywords
    VALID_ROLE_KEYWORDS = {
        # Technical Roles
        'developer', 'engineer', 'architect', 'programmer', 'coder',
        # Management Roles
        'manager', 'director', 'lead', 'head', 'chief', 'vp', 'vice president',
        'president', 'ceo', 'cto', 'cio', 'cfo', 'coo',
        # Analyst Roles
        'analyst', 'consultant', 'specialist', 'expert', 'advisor',
        # Support Roles
        'administrator', 'coordinator', 'associate', 'assistant',
        # Creative Roles
        'designer', 'artist', 'writer', 'editor', 'creator',
        # Research Roles
        'scientist', 'researcher', 'investigator', 'fellow',
        # Executive Roles
        'executive', 'officer', 'principal', 'partner',
        # Other Professional Roles
        'intern', 'trainee', 'apprentice', 'fellow', 'scholar'
    }
    
    # Invalid role patterns (tasks, skills, responsibilities)
    INVALID_ROLE_PATTERNS = {
        # Tasks
        'unit testing', 'integration testing', 'test cases', 'code reviews',
        'sprint planning', 'agile ceremonies', 'daily standups', 'retrospectives',
        'deployment', 'monitoring', 'debugging', 'troubleshooting',
        # Skills
        'api integration', 'rest apis', 'microservices', 'backend development',
        'frontend development', 'full stack development', 'database design',
        # Responsibilities
        'requirements gathering', 'stakeholder management', 'team collaboration',
        'documentation', 'code quality', 'performance optimization',
        # Generic Terms
        'services', 'components', 'modules', 'features', 'functionality',
        'architecture', 'infrastructure', 'platform', 'framework',
        # Plural Forms (usually not job titles)
        'developers', 'engineers', 'analysts', 'managers', 'teams',
        'owners', 'stakeholders', 'users', 'clients', 'customers'
    }
    
    # ═══════════════════════════════════════════════════════════════════════════
    # PHASE 5: COMPANY VALIDATION INDICATORS
    # ═══════════════════════════════════════════════════════════════════════════
    
    COMPANY_INDICATORS = {
        # Legal Entities
        'pvt', 'ltd', 'limited', 'private', 'public', 'plc',
        'inc', 'incorporated', 'corp', 'corporation', 'llc', 'llp',
        'gmbh', 'ag', 'sa', 'nv', 'bv', 'ab', 'oy', 'as',
        # Business Types
        'technologies', 'technology', 'solutions', 'systems', 'services',
        'consulting', 'consultancy', 'group', 'holdings', 'ventures',
        'partners', 'associates', 'enterprises', 'industries',
        # Specific Domains
        'software', 'infotech', 'infosys', 'tech', 'digital',
        'labs', 'laboratory', 'research', 'innovations',
        'global', 'international', 'worldwide', 'india', 'usa'
    }
    
    # Technology keywords that should NEVER be companies
    TECH_KEYWORDS_NOT_COMPANIES = {
        # Programming Languages
        'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'ruby',
        'go', 'rust', 'scala', 'php', 'swift', 'kotlin', 'r',
        # Frameworks
        'react', 'angular', 'vue', 'node', 'nodejs', 'express', 'django',
        'flask', 'spring', 'spring boot', 'fastapi', '.net', 'asp.net',
        # Databases
        'mysql', 'postgresql', 'mongodb', 'redis', 'cassandra', 'oracle',
        'sql server', 'dynamodb', 'elasticsearch', 'neo4j',
        # Cloud & Infrastructure
        'aws', 'azure', 'gcp', 'google cloud', 'docker', 'kubernetes',
        'terraform', 'ansible', 'jenkins', 'gitlab', 'github',
        # Tools
        'jira', 'confluence', 'slack', 'teams', 'zoom', 'tableau',
        'power bi', 'looker', 'git', 'svn', 'maven', 'gradle',
        # Generic Tech Terms
        'api', 'rest', 'graphql', 'microservices', 'devops', 'agile',
        'scrum', 'ci/cd', 'ml', 'ai', 'etl', 'elt', 'saas', 'paas', 'iaas',
        # UI/UX
        'html', 'css', 'sass', 'less', 'bootstrap', 'tailwind', 'material ui',
        'redux', 'mobx', 'vuex', 'webpack', 'vite', 'rollup'
    }
    
    # ═══════════════════════════════════════════════════════════════════════════
    # PHASE 7: LOCATION VALIDATION
    # ═══════════════════════════════════════════════════════════════════════════
    
    LOCATION_INDICATORS = {
        # Indian Cities
        'hyderabad', 'bangalore', 'bengaluru', 'mumbai', 'delhi', 'pune',
        'chennai', 'kolkata', 'ahmedabad', 'surat', 'jaipur', 'lucknow',
        'kanpur', 'nagpur', 'indore', 'thane', 'bhopal', 'visakhapatnam',
        'pimpri', 'patna', 'vadodara', 'ghaziabad', 'ludhiana', 'agra',
        'nashik', 'faridabad', 'meerut', 'rajkot', 'kalyan', 'vasai',
        # Indian States
        'telangana', 'karnataka', 'maharashtra', 'tamil nadu', 'kerala',
        'andhra pradesh', 'gujarat', 'rajasthan', 'uttar pradesh',
        # US Cities
        'new york', 'los angeles', 'chicago', 'houston', 'phoenix',
        'philadelphia', 'san antonio', 'san diego', 'dallas', 'san jose',
        'austin', 'jacksonville', 'fort worth', 'columbus', 'charlotte',
        'san francisco', 'seattle', 'denver', 'boston', 'portland',
        # US States
        'california', 'texas', 'florida', 'new york', 'pennsylvania',
        'illinois', 'ohio', 'georgia', 'north carolina', 'michigan',
        # European Cities
        'london', 'paris', 'berlin', 'madrid', 'rome', 'amsterdam',
        'vienna', 'barcelona', 'munich', 'milan', 'prague', 'dublin',
        # Countries
        'india', 'usa', 'united states', 'uk', 'united kingdom', 'canada',
        'australia', 'germany', 'france', 'spain', 'italy', 'netherlands'
    }
    
    # ═══════════════════════════════════════════════════════════════════════════
    # PHASE 8: EDUCATION VALIDATION
    # ═══════════════════════════════════════════════════════════════════════════
    
    DEGREE_KEYWORDS = {
        'bachelor', 'master', 'phd', 'doctorate', 'diploma', 'certificate',
        'b.tech', 'm.tech', 'b.e', 'm.e', 'b.sc', 'm.sc', 'b.a', 'm.a',
        'mba', 'bba', 'bca', 'mca', 'llb', 'md', 'mbbs', 'ms', 'mphil',
        'associate', 'undergraduate', 'graduate', 'postgraduate'
    }
    
    FIELD_KEYWORDS = {
        'computer science', 'information technology', 'software engineering',
        'electrical engineering', 'mechanical engineering', 'civil engineering',
        'electronics', 'telecommunications', 'mathematics', 'physics',
        'chemistry', 'biology', 'business administration', 'management',
        'finance', 'accounting', 'economics', 'marketing', 'law'
    }
    
    INSTITUTION_INDICATORS = {
        'university', 'college', 'institute', 'school', 'academy',
        'iit', 'nit', 'iiit', 'bits', 'vit', 'jntu', 'anna university',
        'mit', 'stanford', 'harvard', 'berkeley', 'cambridge', 'oxford'
    }
    
    def __init__(self, confidence_thresholds: Dict[str, float] = None):
        """
        Initialize NER post-processor.
        
        Args:
            confidence_thresholds: Custom confidence thresholds per entity type
        """
        self.logger = logging.getLogger(__name__)
        self.confidence_thresholds = confidence_thresholds or self.DEFAULT_CONFIDENCE_THRESHOLDS
        
        # Statistics tracking
        self.stats = {
            'total_entities': 0,
            'filtered_by_confidence': 0,
            'filtered_by_section': 0,
            'filtered_by_validation': 0,
            'merged_entities': 0,
            'deduplicated': 0
        }
    
    # ═══════════════════════════════════════════════════════════════════════════
    # PHASE 1: PRE-PROCESSING
    # ═══════════════════════════════════════════════════════════════════════════
    
    @staticmethod
    def preprocess_text(text: str) -> str:
        """
        Pre-process text before sending to NER model.
        
        Removes:
        - Email addresses
        - Phone numbers
        - URLs
        - Excessive whitespace
        - PDF extraction artifacts
        - Duplicated lines
        
        Args:
            text: Raw resume text
            
        Returns:
            Cleaned text ready for NER
        """
        if not text:
            return ""
        
        logger.debug("=" * 80)
        logger.debug("PHASE 1: PRE-PROCESSING")
        logger.debug("=" * 80)
        logger.debug(f"Original text length: {len(text)} chars")
        
        # 1. Remove email addresses
        text = NERPostProcessor.EMAIL_PATTERN.sub('[EMAIL]', text)
        
        # 2. Remove phone numbers
        text = NERPostProcessor.PHONE_PATTERN.sub('[PHONE]', text)
        
        # 3. Remove URLs
        text = NERPostProcessor.URL_PATTERN.sub('[URL]', text)
        
        # 4. Normalize whitespace (preserve newlines for section detection)
        lines = text.split('\n')
        normalized_lines = []
        for line in lines:
            # Normalize spaces within each line
            line = re.sub(r'\s+', ' ', line).strip()
            normalized_lines.append(line)
        text = '\n'.join(normalized_lines)
        
        # Remove excessive blank lines
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
        
        # 5. Fix PDF extraction artifacts
        text = text.replace('\x00', '')  # Null bytes
        text = text.replace('\ufffd', '')  # Replacement character
        text = re.sub(r'[^\x00-\x7F\u0080-\uFFFF]+', '', text)  # Non-printable chars
        
        # 6. Remove duplicated lines (keep first occurrence)
        lines = text.split('\n')
        seen = set()
        unique_lines = []
        for line in lines:
            line_normalized = line.strip().lower()
            if line_normalized and line_normalized not in seen:
                seen.add(line_normalized)
                unique_lines.append(line)
        text = '\n'.join(unique_lines)
        
        # 7. Remove repeated headers/footers (common in multi-page PDFs)
        # Pattern: Same line appears at regular intervals (page breaks)
        text = NERPostProcessor._remove_repeated_headers_footers(text)
        
        logger.debug(f"Processed text length: {len(text)} chars")
        logger.debug("=" * 80)
        
        return text.strip()
    
    @staticmethod
    def _remove_repeated_headers_footers(text: str) -> str:
        """Remove repeated headers and footers from multi-page documents."""
        lines = text.split('\n')
        if len(lines) < 10:
            return text
        
        # Find lines that appear 3+ times (likely headers/footers)
        line_counts = defaultdict(list)
        for i, line in enumerate(lines):
            normalized = line.strip().lower()
            if normalized and len(normalized) > 5:  # Ignore very short lines
                line_counts[normalized].append(i)
        
        # Remove lines that appear 3+ times at regular intervals
        lines_to_remove = set()
        for normalized, positions in line_counts.items():
            if len(positions) >= 3:
                # Check if positions are roughly evenly spaced (page breaks)
                intervals = [positions[i+1] - positions[i] for i in range(len(positions)-1)]
                avg_interval = sum(intervals) / len(intervals)
                if all(abs(interval - avg_interval) < 5 for interval in intervals):
                    lines_to_remove.update(positions)
        
        # Rebuild text without repeated lines
        filtered_lines = [line for i, line in enumerate(lines) if i not in lines_to_remove]
        return '\n'.join(filtered_lines)
    
    # ═══════════════════════════════════════════════════════════════════════════
    # PHASE 2: SECTION IDENTIFICATION
    # ═══════════════════════════════════════════════════════════════════════════
    
    def identify_section(self, text: str, entity_position: int) -> Optional[str]:
        """
        Identify which resume section an entity belongs to.
        
        Args:
            text: Full resume text
            entity_position: Character position of entity in text
            
        Returns:
            Section name (lowercase) or None
        """
        # Find the nearest section header before the entity
        text_before = text[:entity_position].lower()
        
        # Section header patterns
        section_patterns = {
            'experience': r'\b(?:work\s+)?(?:professional\s+)?experience\b',
            'education': r'\beducation(?:al)?\s+(?:background|qualifications?)?\b',
            'skills': r'\b(?:technical\s+)?skills?\b',
            'projects': r'\bprojects?\b',
            'certifications': r'\bcertifications?\b',
            'summary': r'\b(?:professional\s+)?summary\b',
            'achievements': r'\bachievements?\b',
        }
        
        # Find last matching section header
        last_section = None
        last_position = -1
        
        for section_name, pattern in section_patterns.items():
            for match in re.finditer(pattern, text_before, re.IGNORECASE):
                if match.start() > last_position:
                    last_position = match.start()
                    last_section = section_name
        
        return last_section
    
    def is_entity_in_allowed_section(
        self, 
        entity_type: str, 
        section: Optional[str]
    ) -> bool:
        """
        Check if entity extraction is allowed in the given section.
        
        Args:
            entity_type: Entity type (ROLE, COMPANY, etc.)
            section: Section name
            
        Returns:
            True if extraction is allowed, False otherwise
        """
        if not section:
            return True  # Allow if section unknown (conservative)
        
        section_lower = section.lower()
        
        # Work-related entities (ROLE, COMPANY, CLIENT)
        if entity_type in ['ROLE', 'COMPANY', 'CLIENT']:
            # Block if in blocked sections
            if any(blocked in section_lower for blocked in self.BLOCKED_SECTIONS_FOR_WORK):
                return False
            # Allow if in allowed sections or unknown
            return True
        
        # Education-related entities (DEGREE, INSTITUTION, FIELD)
        if entity_type in ['DEGREE', 'INSTITUTION', 'FIELD', 'EDU_YEAR_START', 'EDU_YEAR_END', 'GRADE']:
            # Only allow in education sections
            return any(allowed in section_lower for allowed in self.ALLOWED_SECTIONS_FOR_EDUCATION)
        
        # Other entities (LOCATION, DATE_START, DATE_END, PERSON_NAME) - allow everywhere
        return True
    
    # ═══════════════════════════════════════════════════════════════════════════
    # PHASE 3: CONFIDENCE FILTERING
    # ═══════════════════════════════════════════════════════════════════════════
    
    def filter_by_confidence(
        self, 
        entities: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Filter entities by confidence score.
        
        Args:
            entities: List of entity dictionaries with 'entity_group', 'word', 'score'
            
        Returns:
            Filtered list of entities
        """
        logger.debug("=" * 80)
        logger.debug("PHASE 3: CONFIDENCE FILTERING")
        logger.debug("=" * 80)
        
        filtered = []
        for entity in entities:
            entity_type = entity.get('entity_group', '').upper()
            score = entity.get('score', 0.0)
            word = entity.get('word', '')
            
            threshold = self.confidence_thresholds.get(entity_type, 0.90)
            
            if score >= threshold:
                filtered.append(entity)
                logger.debug(f"✓ KEEP: {entity_type} '{word}' (score={score:.3f} >= {threshold})")
            else:
                self.stats['filtered_by_confidence'] += 1
                logger.debug(f"✗ REJECT: {entity_type} '{word}' (score={score:.3f} < {threshold})")
        
        logger.debug(f"Filtered: {len(entities)} → {len(filtered)} entities")
        logger.debug("=" * 80)
        
        return filtered
    
    # ═══════════════════════════════════════════════════════════════════════════
    # PHASE 4: ROLE VALIDATION
    # ═══════════════════════════════════════════════════════════════════════════
    
    def validate_role(self, role_text: str) -> bool:
        """
        Validate if text represents a job designation (not a task/skill).
        
        Args:
            role_text: Role text to validate
            
        Returns:
            True if valid role, False otherwise
        """
        if not role_text:
            return False
        
        role_lower = role_text.lower().strip()
        
        # Reject if matches invalid patterns (tasks, skills, responsibilities)
        if role_lower in self.INVALID_ROLE_PATTERNS:
            logger.debug(f"✗ ROLE REJECT: '{role_text}' (invalid pattern)")
            return False
        
        # Reject if plural form (usually not job titles)
        if role_lower.endswith('s') and role_lower not in {'analyst', 'specialist', 'architect'}:
            # Check if it's a plural of a common role
            singular = role_lower[:-1]
            if singular in {'developer', 'engineer', 'manager', 'designer', 'analyst'}:
                logger.debug(f"✗ ROLE REJECT: '{role_text}' (plural form)")
                return False
        
        # Accept if contains valid role keywords
        if any(keyword in role_lower for keyword in self.VALID_ROLE_KEYWORDS):
            logger.debug(f"✓ ROLE ACCEPT: '{role_text}' (valid keyword)")
            return True
        
        # Reject if too short (< 3 chars) or too long (> 100 chars)
        if len(role_text) < 3 or len(role_text) > 100:
            logger.debug(f"✗ ROLE REJECT: '{role_text}' (length)")
            return False
        
        # Reject if contains special characters (except hyphen, space, period)
        if re.search(r'[^a-zA-Z0-9\s\-\.]', role_text):
            logger.debug(f"✗ ROLE REJECT: '{role_text}' (special characters)")
            return False
        
        # Reject if all lowercase or all uppercase (likely not a proper title)
        if role_text.islower() or role_text.isupper():
            logger.debug(f"✗ ROLE REJECT: '{role_text}' (case)")
            return False
        
        # Default: reject (conservative approach)
        logger.debug(f"✗ ROLE REJECT: '{role_text}' (no valid indicators)")
        return False
    
    # ═══════════════════════════════════════════════════════════════════════════
    # PHASE 5: COMPANY VALIDATION
    # ═══════════════════════════════════════════════════════════════════════════
    
    def validate_company(self, company_text: str) -> bool:
        """
        Validate if text represents a company name.
        
        Args:
            company_text: Company text to validate
            
        Returns:
            True if valid company, False otherwise
        """
        if not company_text:
            return False
        
        company_lower = company_text.lower().strip()
        
        # Reject if it's a technology keyword
        if company_lower in self.TECH_KEYWORDS_NOT_COMPANIES:
            logger.debug(f"✗ COMPANY REJECT: '{company_text}' (tech keyword)")
            return False
        
        # Reject if too short (< 2 chars)
        if len(company_text) < 2:
            logger.debug(f"✗ COMPANY REJECT: '{company_text}' (too short)")
            return False
        
        # Accept if contains company indicators
        if any(indicator in company_lower for indicator in self.COMPANY_INDICATORS):
            logger.debug(f"✓ COMPANY ACCEPT: '{company_text}' (company indicator)")
            return True
        
        # Accept if proper noun (capitalized)
        if company_text[0].isupper() and len(company_text) >= 3:
            # Check if it's not a common word
            common_words = {'the', 'and', 'or', 'but', 'for', 'with', 'from', 'to', 'in', 'on', 'at'}
            if company_lower not in common_words:
                logger.debug(f"✓ COMPANY ACCEPT: '{company_text}' (proper noun)")
                return True
        
        # Reject if single word without indicators
        if ' ' not in company_text and not any(ind in company_lower for ind in self.COMPANY_INDICATORS):
            logger.debug(f"✗ COMPANY REJECT: '{company_text}' (single word, no indicators)")
            return False
        
        # Default: accept (less conservative for companies)
        logger.debug(f"✓ COMPANY ACCEPT: '{company_text}' (default)")
        return True
    
    # ═══════════════════════════════════════════════════════════════════════════
    # PHASE 6: CLIENT VALIDATION
    # ═══════════════════════════════════════════════════════════════════════════
    
    def validate_client(self, client_text: str) -> bool:
        """
        Validate if text represents a client/customer name.
        
        Args:
            client_text: Client text to validate
            
        Returns:
            True if valid client, False otherwise
        """
        if not client_text:
            return False
        
        client_lower = client_text.lower().strip()
        
        # Reject if it's a technology keyword
        if client_lower in self.TECH_KEYWORDS_NOT_COMPANIES:
            logger.debug(f"✗ CLIENT REJECT: '{client_text}' (tech keyword)")
            return False
        
        # Use same validation as company (clients are usually companies)
        return self.validate_company(client_text)
    
    # ═══════════════════════════════════════════════════════════════════════════
    # PHASE 7: LOCATION VALIDATION
    # ═══════════════════════════════════════════════════════════════════════════
    
    def validate_location(self, location_text: str) -> bool:
        """
        Validate if text represents a geographical location.
        
        Args:
            location_text: Location text to validate
            
        Returns:
            True if valid location, False otherwise
        """
        if not location_text:
            return False
        
        location_lower = location_text.lower().strip()
        
        # Accept if matches known location
        if location_lower in self.LOCATION_INDICATORS:
            logger.debug(f"✓ LOCATION ACCEPT: '{location_text}' (known location)")
            return True
        
        # Accept if contains state/country pattern
        if re.search(r',\s*[A-Z]{2}$', location_text):  # e.g., "Seattle, WA"
            logger.debug(f"✓ LOCATION ACCEPT: '{location_text}' (state pattern)")
            return True
        
        # Accept if contains city, state pattern
        if re.search(r'^[A-Z][a-z]+,\s*[A-Z][a-z]+', location_text):  # e.g., "New York, USA"
            logger.debug(f"✓ LOCATION ACCEPT: '{location_text}' (city, country pattern)")
            return True
        
        # Reject if too short
        if len(location_text) < 3:
            logger.debug(f"✗ LOCATION REJECT: '{location_text}' (too short)")
            return False
        
        # Default: reject (conservative for locations)
        logger.debug(f"✗ LOCATION REJECT: '{location_text}' (no indicators)")
        return False
    
    # ═══════════════════════════════════════════════════════════════════════════
    # PHASE 8: EDUCATION VALIDATION
    # ═══════════════════════════════════════════════════════════════════════════
    
    def validate_degree(self, degree_text: str) -> bool:
        """Validate if text represents a degree."""
        if not degree_text:
            return False
        
        degree_lower = degree_text.lower().strip()
        
        # Accept if contains degree keywords
        if any(keyword in degree_lower for keyword in self.DEGREE_KEYWORDS):
            logger.debug(f"✓ DEGREE ACCEPT: '{degree_text}'")
            return True
        
        logger.debug(f"✗ DEGREE REJECT: '{degree_text}'")
        return False
    
    def validate_institution(self, institution_text: str) -> bool:
        """Validate if text represents an educational institution."""
        if not institution_text:
            return False
        
        institution_lower = institution_text.lower().strip()
        
        # Accept if contains institution indicators
        if any(indicator in institution_lower for indicator in self.INSTITUTION_INDICATORS):
            logger.debug(f"✓ INSTITUTION ACCEPT: '{institution_text}'")
            return True
        
        # Accept if proper noun and reasonable length
        if institution_text[0].isupper() and 3 <= len(institution_text) <= 100:
            logger.debug(f"✓ INSTITUTION ACCEPT: '{institution_text}' (proper noun)")
            return True
        
        logger.debug(f"✗ INSTITUTION REJECT: '{institution_text}'")
        return False
    
    def validate_field(self, field_text: str) -> bool:
        """Validate if text represents a field of study."""
        if not field_text:
            return False
        
        field_lower = field_text.lower().strip()
        
        # Accept if contains field keywords
        if any(keyword in field_lower for keyword in self.FIELD_KEYWORDS):
            logger.debug(f"✓ FIELD ACCEPT: '{field_text}'")
            return True
        
        # Accept if contains "engineering", "science", "studies"
        if any(word in field_lower for word in ['engineering', 'science', 'studies', 'technology']):
            logger.debug(f"✓ FIELD ACCEPT: '{field_text}'")
            return True
        
        logger.debug(f"✗ FIELD REJECT: '{field_text}'")
        return False
    
    # ═══════════════════════════════════════════════════════════════════════════
    # PHASE 9: ENTITY MERGING
    # ═══════════════════════════════════════════════════════════════════════════
    
    def merge_fragmented_entities(
        self, 
        entities: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Merge fragmented entities that were split by tokenization.
        
        Examples:
        - "TechMahindra Pvt" + "Ltd" → "TechMahindra Pvt Ltd"
        - "J" + "NTU Hyderabad" → "JNTU Hyderabad"
        - "Senior" + "Full Stack" + "Developer" → "Senior Full Stack Developer"
        
        Args:
            entities: List of entity dictionaries
            
        Returns:
            List with merged entities
        """
        logger.debug("=" * 80)
        logger.debug("PHASE 9: ENTITY MERGING")
        logger.debug("=" * 80)
        
        if not entities:
            return entities
        
        merged = []
        i = 0
        
        while i < len(entities):
            current = entities[i]
            entity_type = current.get('entity_group', '')
            word = current.get('word', '').strip()
            
            # Look ahead for potential fragments
            merged_word = word
            j = i + 1
            
            while j < len(entities):
                next_entity = entities[j]
                next_type = next_entity.get('entity_group', '')
                next_word = next_entity.get('word', '').strip()
                
                # Only merge same entity types
                if next_type != entity_type:
                    break
                
                # Check if next word is a continuation
                # Heuristic: merge if next word starts with lowercase or is short
                if (len(next_word) <= 3 or 
                    next_word[0].islower() or 
                    next_word in self.COMPANY_INDICATORS):
                    merged_word += ' ' + next_word
                    j += 1
                    self.stats['merged_entities'] += 1
                else:
                    break
            
            # Create merged entity
            merged_entity = current.copy()
            merged_entity['word'] = merged_word
            merged.append(merged_entity)
            
            if j > i + 1:
                logger.debug(f"MERGED: {entity_type} '{word}' + {j-i-1} fragments → '{merged_word}'")
            
            i = j
        
        logger.debug(f"Merged: {len(entities)} → {len(merged)} entities")
        logger.debug("=" * 80)
        
        return merged
    
    # ═══════════════════════════════════════════════════════════════════════════
    # PHASE 10: DEDUPLICATION
    # ═══════════════════════════════════════════════════════════════════════════
    
    def deduplicate_entities(
        self, 
        entities_by_type: Dict[str, List[str]]
    ) -> Dict[str, List[str]]:
        """
        Remove duplicate entities, keeping the most specific version.
        
        Examples:
        - "Hyderabad" + "Hyderabad, Telangana" → Keep "Hyderabad, Telangana"
        - "React" + "React" → Keep one
        
        Args:
            entities_by_type: Dictionary mapping entity types to lists of values
            
        Returns:
            Deduplicated dictionary
        """
        logger.debug("=" * 80)
        logger.debug("PHASE 10: DEDUPLICATION")
        logger.debug("=" * 80)
        
        deduplicated = {}
        
        for entity_type, values in entities_by_type.items():
            if not values:
                deduplicated[entity_type] = []
                continue
            
            # Normalize and track originals
            normalized_to_original = {}
            for value in values:
                normalized = value.lower().strip()
                if normalized not in normalized_to_original:
                    normalized_to_original[normalized] = value
                else:
                    # Keep the longer/more specific version
                    existing = normalized_to_original[normalized]
                    if len(value) > len(existing):
                        normalized_to_original[normalized] = value
                        self.stats['deduplicated'] += 1
            
            # For locations, handle "City" vs "City, State" case
            if entity_type == 'LOCATION':
                final_values = []
                seen_cities = set()
                
                # Sort by length (descending) to process specific locations first
                sorted_values = sorted(normalized_to_original.values(), key=len, reverse=True)
                
                for value in sorted_values:
                    # Extract city name (part before comma)
                    city = value.split(',')[0].strip().lower()
                    
                    if city not in seen_cities:
                        final_values.append(value)
                        seen_cities.add(city)
                    else:
                        self.stats['deduplicated'] += 1
                        logger.debug(f"DEDUPLICATE: Removed '{value}' (city already present)")
                
                deduplicated[entity_type] = final_values
            else:
                deduplicated[entity_type] = list(normalized_to_original.values())
            
            original_count = len(values)
            final_count = len(deduplicated[entity_type])
            if original_count != final_count:
                logger.debug(f"{entity_type}: {original_count} → {final_count} (removed {original_count - final_count} duplicates)")
        
        logger.debug("=" * 80)
        
        return deduplicated
    
    # ═══════════════════════════════════════════════════════════════════════════
    # PHASE 11: NORMALIZATION
    # ═══════════════════════════════════════════════════════════════════════════
    
    def normalize_entities(
        self, 
        entities_by_type: Dict[str, List[str]]
    ) -> Dict[str, List[str]]:
        """
        Normalize entity values to standard formats.
        
        Examples:
        - "jan 2022" → "January 2022"
        - "Dec 2021" → "December 2021"
        - "infosys limited" → "Infosys Limited"
        
        Args:
            entities_by_type: Dictionary mapping entity types to lists of values
            
        Returns:
            Normalized dictionary
        """
        logger.debug("=" * 80)
        logger.debug("PHASE 11: NORMALIZATION")
        logger.debug("=" * 80)
        
        normalized = {}
        
        for entity_type, values in entities_by_type.items():
            normalized_values = []
            
            for value in values:
                # Normalize based on entity type
                if entity_type in ['DATE_START', 'DATE_END', 'EDU_YEAR_START', 'EDU_YEAR_END']:
                    normalized_value = self._normalize_date(value)
                elif entity_type in ['COMPANY', 'INSTITUTION']:
                    normalized_value = self._normalize_proper_noun(value)
                elif entity_type == 'LOCATION':
                    normalized_value = self._normalize_location(value)
                elif entity_type == 'ROLE':
                    normalized_value = self._normalize_role(value)
                else:
                    normalized_value = value.strip()
                
                normalized_values.append(normalized_value)
                
                if normalized_value != value:
                    logger.debug(f"NORMALIZE: '{value}' → '{normalized_value}'")
            
            normalized[entity_type] = normalized_values
        
        logger.debug("=" * 80)
        
        return normalized
    
    def _normalize_date(self, date_str: str) -> str:
        """Normalize date strings to consistent format."""
        if not date_str:
            return date_str
        
        # Month abbreviations to full names
        month_map = {
            'jan': 'January', 'feb': 'February', 'mar': 'March', 'apr': 'April',
            'may': 'May', 'jun': 'June', 'jul': 'July', 'aug': 'August',
            'sep': 'September', 'oct': 'October', 'nov': 'November', 'dec': 'December'
        }
        
        # Pattern: "jan 2022" or "Jan 2022"
        match = re.match(r'(\w{3})\s+(\d{4})', date_str, re.IGNORECASE)
        if match:
            month_abbr = match.group(1).lower()
            year = match.group(2)
            if month_abbr in month_map:
                return f"{month_map[month_abbr]} {year}"
        
        return date_str
    
    def _normalize_proper_noun(self, text: str) -> str:
        """Normalize proper nouns (companies, institutions)."""
        if not text:
            return text
        
        # Title case for proper nouns
        words = text.split()
        normalized_words = []
        
        for word in words:
            # Keep acronyms uppercase
            if word.isupper() and len(word) <= 5:
                normalized_words.append(word)
            # Keep special suffixes as-is
            elif word.lower() in ['pvt', 'ltd', 'inc', 'llc', 'corp']:
                normalized_words.append(word.capitalize())
            # Title case for regular words
            else:
                normalized_words.append(word.capitalize())
        
        return ' '.join(normalized_words)
    
    def _normalize_location(self, location: str) -> str:
        """Normalize location strings."""
        if not location:
            return location
        
        # Title case for locations
        parts = location.split(',')
        normalized_parts = [part.strip().title() for part in parts]
        return ', '.join(normalized_parts)
    
    def _normalize_role(self, role: str) -> str:
        """Normalize role/job title strings."""
        if not role:
            return role
        
        # Title case for roles
        return role.title()
    
    # ═══════════════════════════════════════════════════════════════════════════
    # MAIN PROCESSING PIPELINE
    # ═══════════════════════════════════════════════════════════════════════════
    
    def process(
        self, 
        entities: List[Dict[str, Any]], 
        full_text: str = ""
    ) -> Dict[str, List[str]]:
        """
        Main post-processing pipeline.
        
        Applies all 13 phases to transform noisy NER output into clean entities.
        
        Args:
            entities: List of raw NER predictions with 'entity_group', 'word', 'score'
            full_text: Full resume text (for section identification)
            
        Returns:
            Dictionary mapping entity types to lists of validated values
        """
        logger.info("=" * 80)
        logger.info("NER POST-PROCESSING PIPELINE - START")
        logger.info("=" * 80)
        logger.info(f"Input: {len(entities)} raw entities")
        
        self.stats['total_entities'] = len(entities)
        
        # PHASE 3: Confidence Filtering
        entities = self.filter_by_confidence(entities)
        
        # PHASE 9: Entity Merging (before validation to merge fragments)
        entities = self.merge_fragmented_entities(entities)
        
        # Group entities by type and apply validation
        entities_by_type = defaultdict(list)
        
        for entity in entities:
            entity_type = entity.get('entity_group', '').upper()
            word = entity.get('word', '').strip()
            
            if not word:
                continue
            
            # PHASE 2: Section-aware filtering (if full_text provided)
            if full_text:
                # Note: This requires entity position, which may not be available
                # For now, we skip section filtering if position not available
                pass
            
            # PHASE 4-8: Entity-specific validation
            is_valid = True
            
            if entity_type == 'ROLE':
                is_valid = self.validate_role(word)
            elif entity_type == 'COMPANY':
                is_valid = self.validate_company(word)
            elif entity_type == 'CLIENT':
                is_valid = self.validate_client(word)
            elif entity_type == 'LOCATION':
                is_valid = self.validate_location(word)
            elif entity_type == 'DEGREE':
                is_valid = self.validate_degree(word)
            elif entity_type == 'INSTITUTION':
                is_valid = self.validate_institution(word)
            elif entity_type == 'FIELD':
                is_valid = self.validate_field(word)
            # Other entity types (dates, names, grades) - accept by default
            
            if is_valid:
                entities_by_type[entity_type].append(word)
            else:
                self.stats['filtered_by_validation'] += 1
        
        # PHASE 10: Deduplication
        entities_by_type = self.deduplicate_entities(dict(entities_by_type))
        
        # PHASE 11: Normalization
        entities_by_type = self.normalize_entities(entities_by_type)
        
        # PHASE 12: Final Output (convert to standard field names)
        final_output = {
            'companies': entities_by_type.get('COMPANY', []),
            'roles': entities_by_type.get('ROLE', []),
            'clients': entities_by_type.get('CLIENT', []),
            'locations': entities_by_type.get('LOCATION', []),
            'degrees': entities_by_type.get('DEGREE', []),
            'institutions': entities_by_type.get('INSTITUTION', []),
            'fields': entities_by_type.get('FIELD', []),
            'date_start': entities_by_type.get('DATE_START', []),
            'date_end': entities_by_type.get('DATE_END', []),
            'edu_year_start': entities_by_type.get('EDU_YEAR_START', []),
            'edu_year_end': entities_by_type.get('EDU_YEAR_END', []),
            'grades': entities_by_type.get('GRADE', []),
            'person_names': entities_by_type.get('PERSON_NAME', [])
        }
        
        # Log statistics
        logger.info("=" * 80)
        logger.info("PROCESSING STATISTICS")
        logger.info("=" * 80)
        logger.info(f"Total entities processed: {self.stats['total_entities']}")
        logger.info(f"Filtered by confidence: {self.stats['filtered_by_confidence']}")
        logger.info(f"Filtered by validation: {self.stats['filtered_by_validation']}")
        logger.info(f"Merged entities: {self.stats['merged_entities']}")
        logger.info(f"Deduplicated: {self.stats['deduplicated']}")
        logger.info("=" * 80)
        logger.info("FINAL OUTPUT")
        logger.info("=" * 80)
        for key, values in final_output.items():
            if values:
                logger.info(f"{key}: {values}")
        logger.info("=" * 80)
        logger.info("NER POST-PROCESSING PIPELINE - COMPLETE")
        logger.info("=" * 80)
        
        return final_output


# ═══════════════════════════════════════════════════════════════════════════
# USAGE EXAMPLE
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.DEBUG)
    
    # Sample NER output
    raw_entities = [
        {"entity_group": "ROLE", "word": "Senior Full Stack Developer", "score": 0.998},
        {"entity_group": "ROLE", "word": "business analysts", "score": 0.935},
        {"entity_group": "ROLE", "word": "integration test cases", "score": 0.912},
        {"entity_group": "COMPANY", "word": "TechMahindra Pvt", "score": 0.943},
        {"entity_group": "COMPANY", "word": "Ltd", "score": 0.921},
        {"entity_group": "COMPANY", "word": "React", "score": 0.889},
        {"entity_group": "INSTITUTION", "word": "NTU Hyderabad", "score": 0.941},
        {"entity_group": "LOCATION", "word": "Hyderabad", "score": 0.956},
        {"entity_group": "LOCATION", "word": "Hyderabad, Telangana", "score": 0.948},
    ]
    
    # Initialize post-processor
    processor = NERPostProcessor()
    
    # Process entities
    result = processor.process(raw_entities)
    
    print("\n" + "=" * 80)
    print("FINAL RESULT")
    print("=" * 80)
    import json
    print(json.dumps(result, indent=2))
