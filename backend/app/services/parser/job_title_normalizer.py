"""
Job Title Normalizer with Seniority Detection and Category Classification
Provides intelligent job title normalization and classification
"""

import re
import logging
from typing import Dict, List, Tuple, Optional, Set
from rapidfuzz import fuzz, process

logger = logging.getLogger(__name__)

class JobTitleNormalizer:
    """
    Advanced job title normalizer with seniority detection,
    category classification, and fuzzy matching
    """
    
    def __init__(self, job_titles_data: Dict):
        self.job_titles_data = job_titles_data
        
        # Build search indexes
        self.title_index = self._build_title_index()
        self.category_index = self._build_category_index()
        
        # Seniority patterns and mappings
        self.seniority_patterns = self._build_seniority_patterns()
        self.seniority_mapping = self._build_seniority_mapping()
        
        # Department/function patterns
        self.department_patterns = self._build_department_patterns()
        
        # Common title variations and synonyms
        self.title_variations = self._build_title_variations()
        
        # Technical skill indicators
        self.technical_keywords = self._build_technical_keywords()
        
        logger.info(f"JobTitleNormalizer initialized with {len(job_titles_data)} job titles")
    
    def _build_title_index(self) -> List[str]:
        """Build searchable index of job titles"""
        return list(self.job_titles_data.keys())
    
    def _build_category_index(self) -> Dict[str, List[str]]:
        """Build index of job titles by category"""
        category_index = {}
        
        for title_key, title_data in self.job_titles_data.items():
            category = title_data.get('category', '').lower()
            if category:
                if category not in category_index:
                    category_index[category] = []
                category_index[category].append(title_key)
        
        return category_index
    
    def _build_seniority_patterns(self) -> Dict[str, str]:
        """Build patterns for detecting seniority levels"""
        return {
            'executive': r'\b(chief|c[ -]?[a-z]+o|vice president|vp|president|director|head|lead|principal|staff|fellow)\b',
            'senior': r'\b(senior|sr|sr\.|lead|principal|staff|head|chief|director|manager|supervisor)\b',
            'mid_level': r'\b(associate|mid|mid-level|experienced|professional)\b',
            'junior': r'\b(junior|jr|jr\.|associate|assistant|intern|trainee|entry|entry-level|graduate)\b',
            'contract': r'\b(contract|freelance|consultant|temporary|temp|contractor)\b',
            'internship': r'\b(intern|internship|trainee|co-op|cooperative)\b'
        }
    
    def _build_seniority_mapping(self) -> Dict[str, str]:
        """Build mapping for seniority level standardization"""
        return {
            'executive': 'Executive',
            'senior': 'Senior',
            'mid_level': 'Mid-Level',
            'junior': 'Junior',
            'contract': 'Contract',
            'internship': 'Intern'
        }
    
    def _build_department_patterns(self) -> Dict[str, List[str]]:
        """Build patterns for department/function detection"""
        return {
            'engineering': [
                'engineer', 'developer', 'programmer', 'software', 'technical', 'architect',
                'devops', 'sre', 'qa', 'test', 'quality', 'full stack', 'backend', 'frontend',
                'mobile', 'web', 'cloud', 'infrastructure', 'platform', 'systems'
            ],
            'product': [
                'product', 'product manager', 'pm', 'product owner', 'scrum', 'agile',
                'user experience', 'ux', 'product design', 'product strategy'
            ],
            'design': [
                'designer', 'design', 'ui', 'ux', 'graphic', 'visual', 'creative',
                'art', 'illustration', 'animation', 'web design', 'product design'
            ],
            'data': [
                'data', 'analytics', 'analyst', 'scientist', 'engineer', 'warehouse',
                'business intelligence', 'bi', 'machine learning', 'ml', 'ai', 'statistics'
            ],
            'marketing': [
                'marketing', 'digital', 'content', 'social media', 'seo', 'sem', 'ppc',
                'brand', 'communications', 'pr', 'public relations', 'growth', 'campaign'
            ],
            'sales': [
                'sales', 'account', 'business development', 'bd', 'revenue', 'customer',
                'client', 'partnership', 'regional', 'territory', 'inside', 'field'
            ],
            'finance': [
                'finance', 'financial', 'accounting', 'controller', 'cfo', 'treasury',
                'investment', 'banking', 'credit', 'risk', 'compliance', 'audit'
            ],
            'hr': [
                'human resources', 'hr', 'recruiter', 'recruiting', 'talent', 'people',
                'learning', 'training', 'development', 'compensation', 'benefits'
            ],
            'operations': [
                'operations', 'operational', 'supply chain', 'logistics', 'warehouse',
                'fulfillment', 'procurement', 'inventory', 'quality', 'process'
            ],
            'legal': [
                'legal', 'lawyer', 'attorney', 'counsel', 'paralegal', 'compliance',
                'contract', 'regulatory', 'intellectual property', 'ip'
            ],
            'healthcare': [
                'medical', 'doctor', 'physician', 'nurse', 'healthcare', 'clinical',
                'pharmacist', 'therapist', 'hospital', 'patient', 'health'
            ],
            'education': [
                'education', 'teacher', 'professor', 'academic', 'research', 'student',
                'university', 'college', 'school', 'learning', 'instruction'
            ]
        }
    
    def _build_title_variations(self) -> Dict[str, List[str]]:
        """Build common title variations and synonyms"""
        return {
            'software_engineer': ['swe', 'software developer', 'programmer', 'coder', 'software dev'],
            'data_scientist': ['data science', 'ds', 'data analyst', 'analytics engineer'],
            'product_manager': ['pm', 'product owner', 'product lead'],
            'ux_designer': ['user experience designer', 'ux designer', 'experience designer'],
            'ui_designer': ['user interface designer', 'ui designer', 'interface designer'],
            'devops_engineer': ['devops', 'site reliability engineer', 'sre', 'platform engineer'],
            'full_stack_developer': ['full stack', 'full stack engineer', 'full stack dev'],
            'backend_developer': ['backend', 'back end', 'server-side', 'backend eng'],
            'frontend_developer': ['frontend', 'front end', 'client-side', 'frontend eng'],
            'mobile_developer': ['mobile', 'ios developer', 'android developer', 'app developer'],
            'security_engineer': ['cybersecurity', 'infosec', 'information security', 'security analyst'],
            'qa_engineer': ['quality assurance', 'qa', 'test engineer', 'software tester'],
            'business_analyst': ['ba', 'business analyst', 'systems analyst'],
            'project_manager': ['pm', 'project lead', 'program manager'],
            'scrum_master': ['scrum master', 'agile coach', 'scrum coach']
        }
    
    def _build_technical_keywords(self) -> List[str]:
        """Build list of technical skill keywords"""
        return [
            'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'php', 'ruby', 'go', 'rust',
            'react', 'angular', 'vue', 'node', 'django', 'flask', 'spring', 'dotnet', 'laravel',
            'aws', 'azure', 'gcp', 'cloud', 'docker', 'kubernetes', 'terraform', 'ansible',
            'sql', 'nosql', 'mongodb', 'postgresql', 'mysql', 'redis', 'elasticsearch',
            'machine learning', 'ai', 'deep learning', 'nlp', 'computer vision', 'data science',
            'devops', 'ci/cd', 'git', 'jenkins', 'github', 'gitlab', 'agile', 'scrum',
            'microservices', 'api', 'rest', 'graphql', 'websockets', 'kafka', 'rabbitmq'
        ]
    
    def normalize_job_title(self, title: str, use_fuzzy: bool = True) -> Tuple[str, str, str, float]:
        """
        Normalize job title with seniority detection and category classification
        
        Args:
            title: Raw job title
            use_fuzzy: Whether to use fuzzy matching
            
        Returns:
            Tuple of (normalized_title, seniority, category, confidence_score)
        """
        if not title:
            return None, None, None, 0.0
        
        # Extract components
        cleaned_title, detected_seniority = self._extract_seniority(title)
        detected_department = self._detect_department(cleaned_title)
        
        # Try exact match first
        exact_result = self._exact_match(cleaned_title.lower())
        if exact_result:
            normalized_title = self._apply_seniority(exact_result['normalized'], detected_seniority)
            return normalized_title, detected_seniority, exact_result['category'], 1.0
        
        # Try fuzzy matching
        if use_fuzzy and self.title_index:
            fuzzy_result = self._fuzzy_match(cleaned_title)
            if fuzzy_result:
                normalized_title = self._apply_seniority(fuzzy_result['normalized'], detected_seniority)
                return normalized_title, detected_seniority, fuzzy_result['category'], fuzzy_result['confidence']
        
        # Try variation matching
        variation_result = self._variation_match(cleaned_title)
        if variation_result:
            normalized_title = self._apply_seniority(variation_result['normalized'], detected_seniority)
            return normalized_title, detected_seniority, variation_result['category'], variation_result['confidence']
        
        # Try department-based normalization
        if detected_department:
            dept_result = self._department_normalization(cleaned_title, detected_department)
            if dept_result:
                normalized_title = self._apply_seniority(dept_result['normalized'], detected_seniority)
                return normalized_title, detected_seniority, dept_result['category'], dept_result['confidence']
        
        # Fallback normalization
        normalized_title = self._fallback_normalization(cleaned_title, detected_seniority)
        category = self._infer_category(cleaned_title, detected_department)
        
        return normalized_title, detected_seniority, category, 0.5
    
    def _extract_seniority(self, title: str) -> Tuple[str, Optional[str]]:
        """Extract seniority level from job title"""
        original_title = title
        detected_seniority = None
        
        # Check for seniority patterns in order of precedence
        for seniority_level, pattern in self.seniority_patterns.items():
            matches = re.findall(pattern, title, re.IGNORECASE)
            if matches:
                detected_seniority = seniority_level
                # Remove seniority indicators from title
                title = re.sub(pattern, '', title, flags=re.IGNORECASE)
                break
        
        return title.strip(), detected_seniority
    
    def _detect_department(self, title: str) -> Optional[str]:
        """Detect department/function from job title"""
        title_lower = title.lower()
        
        department_scores = {}
        for department, keywords in self.department_patterns.items():
            score = 0
            for keyword in keywords:
                if keyword in title_lower:
                    score += len(keyword.split())  # Weight by keyword length
            department_scores[department] = score
        
        if not department_scores or max(department_scores.values()) == 0:
            return None
        
        # Return department with highest score
        detected_department = max(department_scores, key=department_scores.get)
        
        # Only return if we have reasonable confidence
        if department_scores[detected_department] >= 2:
            return detected_department
        
        return None
    
    def _exact_match(self, title_lower: str) -> Optional[Dict]:
        """Try exact match"""
        if title_lower in self.job_titles_data:
            title_data = self.job_titles_data[title_lower]
            return {
                'normalized': title_data['normalized'],
                'category': title_data['category'],
                'match_type': 'exact'
            }
        
        return None
    
    def _fuzzy_match(self, title: str) -> Optional[Dict]:
        """Try fuzzy matching"""
        strategies = [
            (fuzz.token_set_ratio, 'token_set'),
            (fuzz.token_sort_ratio, 'token_sort'),
            (fuzz.partial_ratio, 'partial'),
            (fuzz.ratio, 'simple')
        ]
        
        best_match = None
        best_score = 0
        
        for scorer, strategy_name in strategies:
            result = process.extractOne(
                title,
                self.title_index,
                scorer=scorer,
                score_cutoff=70
            )
            
            if result:
                match_name, score, _ = result
                if score > best_score:
                    best_score = score
                    title_data = self.job_titles_data[match_name]
                    best_match = {
                        'normalized': title_data['normalized'],
                        'category': title_data['category'],
                        'confidence': score / 100.0,
                        'match_type': f'fuzzy_{strategy_name}'
                    }
        
        return best_match
    
    def _variation_match(self, title: str) -> Optional[Dict]:
        """Try matching with title variations"""
        title_lower = title.lower()
        
        for canonical_title, variations in self.title_variations.items():
            for variation in variations:
                if variation in title_lower:
                    # Find the canonical title in our data
                    for title_key, title_data in self.job_titles_data.items():
                        if canonical_title.lower() in title_key.lower():
                            return {
                                'normalized': title_data['normalized'],
                                'category': title_data['category'],
                                'confidence': 0.85,
                                'match_type': 'variation'
                            }
        
        return None
    
    def _department_normalization(self, title: str, department: str) -> Optional[Dict]:
        """Normalize based on detected department"""
        # Try to find similar titles in the same department
        department_titles = self.category_index.get(department, [])
        
        if not department_titles:
            return None
        
        # Fuzzy match within department
        result = process.extractOne(
            title,
            department_titles,
            scorer=fuzz.token_set_ratio,
            score_cutoff=60
        )
        
        if result:
            match_name, score, _ = result
            title_data = self.job_titles_data[match_name]
            return {
                'normalized': title_data['normalized'],
                'category': title_data['category'],
                'confidence': score / 100.0 * 0.8,  # Lower confidence for dept-based match
                'match_type': 'department_based'
            }
        
        # Create normalized title based on department
        base_title = self._create_base_title(title, department)
        return {
            'normalized': base_title,
            'category': department.title(),
            'confidence': 0.6,
            'match_type': 'department_created'
        }
    
    def _create_base_title(self, title: str, department: str) -> str:
        """Create base title from detected department"""
        # Remove common words and keep core terms
        title_lower = title.lower()
        
        # Department-specific base titles
        department_bases = {
            'engineering': 'Engineer',
            'product': 'Product Manager',
            'design': 'Designer',
            'data': 'Data Analyst',
            'marketing': 'Marketing Manager',
            'sales': 'Sales Representative',
            'finance': 'Financial Analyst',
            'hr': 'HR Specialist',
            'operations': 'Operations Manager',
            'legal': 'Legal Counsel',
            'healthcare': 'Healthcare Professional',
            'education': 'Educator'
        }
        
        return department_bases.get(department, 'Professional')
    
    def _fallback_normalization(self, title: str, seniority: Optional[str]) -> str:
        """Fallback normalization when no match is found"""
        # Clean up the title
        title = re.sub(r'\s+', ' ', title).strip()
        
        # Capitalize properly
        title_words = title.split()
        capitalized_words = []
        
        for word in title_words:
            if word.upper() in ['CEO', 'CTO', 'CFO', 'COO', 'CIO', 'CSO', 'CMO']:
                capitalized_words.append(word.upper())
            elif word.lower() in ['and', 'of', 'the', 'in', 'for', 'with', 'at']:
                capitalized_words.append(word.lower())
            else:
                capitalized_words.append(word.title())
        
        normalized = ' '.join(capitalized_words)
        
        return self._apply_seniority(normalized, seniority)
    
    def _apply_seniority(self, title: str, seniority: Optional[str]) -> str:
        """Apply seniority prefix to normalized title"""
        if not seniority:
            return title
        
        prefix = self.seniority_mapping.get(seniority, seniority.title())
        
        # Avoid double prefixes
        if any(title.startswith(p) for p in ['Senior ', 'Junior ', 'Executive ', 'Mid-Level ', 'Contract ', 'Intern ']):
            return title
        
        return f"{prefix} {title}"
    
    def _infer_category(self, title: str, department: Optional[str]) -> str:
        """Infer category from title and department"""
        if department:
            return department.title()
        
        # Try to infer from title keywords
        title_lower = title.lower()
        
        category_keywords = {
            'Technology': ['engineer', 'developer', 'software', 'technical', 'architect', 'devops'],
            'Business': ['manager', 'analyst', 'consultant', 'specialist', 'coordinator'],
            'Design': ['designer', 'artist', 'creative', 'visual'],
            'Marketing': ['marketing', 'content', 'social', 'brand'],
            'Sales': ['sales', 'account', 'business', 'revenue'],
            'Finance': ['finance', 'financial', 'accounting', 'investment'],
            'Human Resources': ['hr', 'recruiter', 'talent', 'people'],
            'Operations': ['operations', 'supply', 'logistics', 'process'],
            'Legal': ['legal', 'lawyer', 'attorney', 'counsel'],
            'Healthcare': ['medical', 'doctor', 'nurse', 'health'],
            'Education': ['education', 'teacher', 'professor', 'academic'],
            'Service': ['support', 'service', 'customer', 'help'],
            'General': []
        }
        
        for category, keywords in category_keywords.items():
            for keyword in keywords:
                if keyword in title_lower:
                    return category
        
        return 'General'
    
    def find_similar_titles(self, title: str, limit: int = 10, threshold: float = 0.5) -> List[Tuple[str, float, str]]:
        """
        Find similar job titles
        
        Args:
            title: Reference job title
            limit: Maximum number of results
            threshold: Minimum similarity threshold
            
        Returns:
            List of (title, similarity_score, category) tuples
        """
        if not title or not self.title_index:
            return []
        
        # Get fuzzy matches
        results = process.extract(
            title,
            self.title_index,
            scorer=fuzz.token_set_ratio,
            limit=limit * 2
        )
        
        similar_titles = []
        for match_name, score, _ in results:
            if score >= threshold * 100:
                title_data = self.job_titles_data[match_name]
                similar_titles.append((
                    title_data['normalized'],
                    score / 100.0,
                    title_data['category']
                ))
        
        return similar_titles[:limit]
    
    def get_titles_by_category(self, category: str) -> List[str]:
        """Get all job titles in a specific category"""
        category_lower = category.lower()
        titles = []
        
        for title_key, title_data in self.job_titles_data.items():
            if title_data.get('category', '').lower() == category_lower:
                titles.append(title_data['normalized'])
        
        return titles
    
    def get_title_statistics(self) -> Dict:
        """Get statistics about loaded job titles"""
        stats = {
            'total_titles': len(self.job_titles_data),
            'by_category': {},
            'by_seniority': {
                'executive': 0,
                'senior': 0,
                'mid_level': 0,
                'junior': 0,
                'contract': 0,
                'internship': 0,
                'unspecified': 0
            }
        }
        
        # Count by category
        for title_data in self.job_titles_data.values():
            category = title_data.get('category', 'unknown')
            stats['by_category'][category] = stats['by_category'].get(category, 0) + 1
        
        # Analyze seniority distribution
        for title_key in self.job_titles_data.keys():
            _, seniority = self._extract_seniority(title_key)
            if seniority:
                stats['by_seniority'][seniority] += 1
            else:
                stats['by_seniority']['unspecified'] += 1
        
        return stats
    
    def validate_job_title(self, title: str) -> Dict:
        """
        Validate and analyze job title
        
        Args:
            title: Job title to validate
            
        Returns:
            Validation results with analysis
        """
        if not title:
            return {
                'valid': False,
                'errors': ['Empty job title'],
                'suggestions': [],
                'analysis': {}
            }
        
        # Normalize the title
        normalized_title, seniority, category, confidence = self.normalize_job_title(title)
        
        analysis = {
            'original_title': title,
            'normalized_title': normalized_title,
            'detected_seniority': seniority,
            'detected_category': category,
            'confidence_score': confidence,
            'word_count': len(title.split()),
            'has_numbers': bool(re.search(r'\d', title)),
            'has_all_caps': bool(re.search(r'^[A-Z\s]+$', title)),
            'has_abbreviations': bool(re.search(r'\b[A-Z]{2,}\b', title)),
            'detected_department': self._detect_department(title)
        }
        
        # Check for potential issues
        errors = []
        suggestions = []
        
        if analysis['word_count'] > 8:
            errors.append('Job title seems too long')
            suggestions.append('Consider using a more concise title')
        
        if analysis['has_numbers'] and not re.search(r'\b(3d|2d|4g|5g|level\s+\d|sr\s+\d|jr\s+\d)\b', title, re.IGNORECASE):
            errors.append('Job title contains numbers which may be unusual')
            suggestions.append('Verify if numbers are part of the actual job title')
        
        if analysis['has_all_caps']:
            errors.append('Job title is in all caps')
            suggestions.append('Consider using proper capitalization')
        
        if confidence < 0.6:
            errors.append('Low confidence in normalization')
            suggestions.append('Consider using a more standard job title format')
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'suggestions': suggestions,
            'analysis': analysis,
            'similar_titles': self.find_similar_titles(title, limit=5, threshold=0.7)
        }
