"""
Company Matcher with Advanced Fuzzy Matching and Industry Detection
Provides intelligent company name matching and classification
"""

import re
import logging
from typing import Dict, List, Tuple, Optional, Set
from rapidfuzz import fuzz, process
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)

class CompanyMatcher:
    """
    Advanced company name matching with fuzzy matching,
    industry detection, and confidence scoring
    """
    
    def __init__(self, companies_data: Dict):
        self.companies_data = companies_data
        
        # Build search indexes
        self.company_index = self._build_company_index()
        self.industry_index = self._build_industry_index()
        self.specialization_index = self._build_specialization_index()
        
        # Common company name patterns and variations
        self.variation_patterns = self._build_variation_patterns()
        
        # Industry keywords for classification
        self.industry_keywords = self._build_industry_keywords()
        
        logger.info(f"CompanyMatcher initialized with {len(companies_data)} companies")
    
    def _build_company_index(self) -> List[str]:
        """Build searchable index of company names"""
        return list(self.companies_data.keys())
    
    def _build_industry_index(self) -> Dict[str, List[str]]:
        """Build index of companies by industry"""
        industry_index = {}
        
        for company_key, company_data in self.companies_data.items():
            industry = company_data.get('industry', '').lower()
            if industry:
                if industry not in industry_index:
                    industry_index[industry] = []
                industry_index[industry].append(company_key)
        
        return industry_index
    
    def _build_specialization_index(self) -> Dict[str, List[str]]:
        """Build index of companies by specialization"""
        specialization_index = {}
        
        for company_key, company_data in self.companies_data.items():
            specialization = company_data.get('specialization', '').lower()
            if specialization:
                if specialization not in specialization_index:
                    specialization_index[specialization] = []
                specialization_index[specialization].append(company_key)
        
        return specialization_index
    
    def _build_variation_patterns(self) -> Dict[str, List[str]]:
        """Build common company name variation patterns"""
        return {
            'suffixes': [
                r'\s+(inc|llc|corp|corporation|ltd|limited|co|company|group|holdings|international|global|worldwide)$',
                r'\s+(technologies|technology|tech|solutions|systems|services|consulting|partners|associates|labs|laboratory)$',
                r'\s+(software|digital|online|internet|web|mobile|cloud|data|analytics|ai|machine learning)$',
                r'\s+(healthcare|medical|pharma|pharmaceutical|biotech|biotechnology|life sciences)$',
                r'\s+(financial|finance|banking|investment|insurance|fintech|payments)$',
                r'\.com$'
            ],
            'prefixes': [
                r'^the\s+',
                r'^new\s+',
                r'^american\s+',
                r'^united\s+',
                r'^national\s+',
                r'^global\s+',
                r'^international\s+'
            ],
            'separators': [
                r'[-_\.]',
                r'\s+and\s+',
                r'\s*&\s+',
                r'\s+\+\s+'
            ],
            'common_variations': {
                'tech': 'technology',
                'sys': 'systems',
                'sol': 'solutions',
                'corp': 'corporation',
                'intl': 'international',
                'fin': 'financial',
                'med': 'medical',
                'bio': 'biotechnology',
                'pharma': 'pharmaceutical'
            }
        }
    
    def _build_industry_keywords(self) -> Dict[str, List[str]]:
        """Build industry keyword mappings"""
        return {
            'technology': [
                'software', 'technology', 'tech', 'computer', 'digital', 'internet', 'web', 'mobile',
                'cloud', 'saas', 'paas', 'iaas', 'ai', 'artificial intelligence', 'machine learning',
                'data', 'analytics', 'cybersecurity', 'security', 'network', 'infrastructure',
                'development', 'programming', 'coding', 'api', 'platform', 'application'
            ],
            'healthcare': [
                'healthcare', 'medical', 'health', 'hospital', 'clinic', 'pharma', 'pharmaceutical',
                'biotech', 'biotechnology', 'life sciences', 'medical device', 'diagnostics',
                'telemedicine', 'health it', 'digital health', 'clinical', 'research'
            ],
            'finance': [
                'bank', 'banking', 'financial', 'finance', 'investment', 'insurance', 'fintech',
                'payments', 'credit', 'loan', 'mortgage', 'wealth', 'asset', 'trading',
                'securities', 'capital', 'venture', 'private equity', 'fund'
            ],
            'consulting': [
                'consulting', 'consultant', 'advisory', 'management', 'strategy', 'operations',
                'transformation', 'digital transformation', 'business consulting', 'it consulting'
            ],
            'retail': [
                'retail', 'ecommerce', 'e-commerce', 'shopping', 'store', 'marketplace',
                'consumer', 'fashion', 'apparel', 'grocery', 'food', 'beverage'
            ],
            'manufacturing': [
                'manufacturing', 'industrial', 'factory', 'production', 'machinery', 'equipment',
                'automotive', 'aerospace', 'electronics', 'components', 'supply chain'
            ],
            'energy': [
                'energy', 'oil', 'gas', 'petroleum', 'renewable', 'solar', 'wind', 'power',
                'electricity', 'utility', 'clean energy', 'sustainability'
            ],
            'education': [
                'education', 'learning', 'university', 'college', 'school', 'training',
                'online learning', 'edtech', 'educational', 'academic'
            ],
            'media': [
                'media', 'entertainment', 'publishing', 'broadcasting', 'streaming',
                'gaming', 'music', 'video', 'news', 'content', 'advertising'
            ],
            'transportation': [
                'transportation', 'logistics', 'shipping', 'delivery', 'freight', 'warehouse',
                'supply chain', 'fleet', 'automotive', 'aviation', 'railway', 'maritime'
            ]
        }
    
    def match_company(self, company_name: str, threshold: float = 0.7) -> Tuple[Optional[str], float, Dict]:
        """
        Match company name with confidence scoring
        
        Args:
            company_name: Company name to match
            threshold: Minimum confidence threshold
            
        Returns:
            Tuple of (matched_company, confidence_score, metadata)
        """
        if not company_name:
            return None, 0.0, {}
        
        # Clean and normalize input
        cleaned_name = self._clean_company_name(company_name)
        
        # Try exact match first
        exact_match = self._exact_match(cleaned_name)
        if exact_match:
            return exact_match['name'], 1.0, exact_match
        
        # Try fuzzy matching
        fuzzy_match = self._fuzzy_match(cleaned_name, threshold)
        if fuzzy_match:
            return fuzzy_match['name'], fuzzy_match['confidence'], fuzzy_match
        
        # Try partial matching
        partial_match = self._partial_match(cleaned_name, threshold * 0.8)
        if partial_match:
            return partial_match['name'], partial_match['confidence'], partial_match
        
        # Try industry-based matching
        industry_match = self._industry_based_match(cleaned_name)
        if industry_match:
            return industry_match['name'], industry_match['confidence'], industry_match
        
        return cleaned_name, 0.5, {'type': 'fallback', 'original': company_name}
    
    def _clean_company_name(self, name: str) -> str:
        """Clean company name for better matching"""
        # Remove common suffixes
        for suffix_pattern in self.variation_patterns['suffixes']:
            name = re.sub(suffix_pattern, '', name, flags=re.IGNORECASE)
        
        # Remove common prefixes
        for prefix_pattern in self.variation_patterns['prefixes']:
            name = re.sub(prefix_pattern, '', name, flags=re.IGNORECASE)
        
        # Normalize separators
        for separator_pattern in self.variation_patterns['separators']:
            name = re.sub(separator_pattern, ' ', name, flags=re.IGNORECASE)
        
        # Replace common variations
        for variation, replacement in self.variation_patterns['common_variations'].items():
            name = re.sub(rf'\b{variation}\b', replacement, name, flags=re.IGNORECASE)
        
        # Clean up extra whitespace and normalize case
        name = re.sub(r'\s+', ' ', name).strip()
        
        return name
    
    def _exact_match(self, cleaned_name: str) -> Optional[Dict]:
        """Try exact match"""
        name_lower = cleaned_name.lower()
        
        if name_lower in self.companies_data:
            company_data = self.companies_data[name_lower]
            return {
                'name': company_data.get('normalized_company', company_data['name']),
                'type': company_data.get('type', 'unknown'),
                'industry': company_data.get('industry', ''),
                'confidence': 1.0,
                'match_type': 'exact'
            }
        
        return None
    
    def _fuzzy_match(self, cleaned_name: str, threshold: float) -> Optional[Dict]:
        """Try fuzzy matching"""
        if not self.company_index:
            return None
        
        # Use multiple fuzzy matching strategies
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
                cleaned_name,
                self.company_index,
                scorer=scorer,
                score_cutoff=int(threshold * 100)
            )
            
            if result:
                match_name, score, _ = result
                if score > best_score:
                    best_score = score
                    company_data = self.companies_data[match_name]
                    best_match = {
                        'name': company_data.get('normalized_company', company_data['name']),
                        'type': company_data.get('type', 'unknown'),
                        'industry': company_data.get('industry', ''),
                        'confidence': score / 100.0,
                        'match_type': f'fuzzy_{strategy_name}'
                    }
        
        return best_match
    
    def _partial_match(self, cleaned_name: str, threshold: float) -> Optional[Dict]:
        """Try partial matching for substrings"""
        words = cleaned_name.split()
        if len(words) < 2:
            return None
        
        # Try matching with first 2-3 words
        for i in range(2, min(4, len(words) + 1)):
            partial_name = ' '.join(words[:i])
            result = self._fuzzy_match(partial_name, threshold)
            
            if result:
                result['match_type'] = f'partial_{i}words'
                return result
        
        return None
    
    def _industry_based_match(self, cleaned_name: str) -> Optional[Dict]:
        """Try industry-based matching"""
        detected_industry = self._detect_industry(cleaned_name)
        
        if not detected_industry:
            return None
        
        # Find companies in detected industry
        industry_companies = self.industry_index.get(detected_industry, [])
        
        if not industry_companies:
            return None
        
        # Try fuzzy matching within industry
        result = process.extractOne(
            cleaned_name,
            industry_companies,
            scorer=fuzz.token_set_ratio,
            score_cutoff=60
        )
        
        if result:
            match_name, score, _ = result
            company_data = self.companies_data[match_name]
            return {
                'name': company_data.get('normalized_company', company_data['name']),
                'type': company_data.get('type', 'unknown'),
                'industry': company_data.get('industry', ''),
                'confidence': score / 100.0 * 0.8,  # Lower confidence for industry-based match
                'match_type': 'industry_based',
                'detected_industry': detected_industry
            }
        
        return None
    
    def _detect_industry(self, company_name: str) -> Optional[str]:
        """Detect industry from company name"""
        name_lower = company_name.lower()
        
        industry_scores = {}
        for industry, keywords in self.industry_keywords.items():
            score = 0
            for keyword in keywords:
                if keyword in name_lower:
                    score += 1
            industry_scores[industry] = score
        
        if not industry_scores or max(industry_scores.values()) == 0:
            return None
        
        # Return industry with highest score
        detected_industry = max(industry_scores, key=industry_scores.get)
        
        # Only return if we have reasonable confidence
        if industry_scores[detected_industry] >= 1:
            return detected_industry
        
        return None
    
    def find_similar_companies(self, company_name: str, limit: int = 10, threshold: float = 0.5) -> List[Tuple[str, float, Dict]]:
        """
        Find similar companies
        
        Args:
            company_name: Reference company name
            limit: Maximum number of results
            threshold: Minimum similarity threshold
            
        Returns:
            List of (company_name, similarity_score, metadata) tuples
        """
        if not company_name or not self.company_index:
            return []
        
        cleaned_name = self._clean_company_name(company_name)
        
        # Get fuzzy matches
        results = process.extract(
            cleaned_name,
            self.company_index,
            scorer=fuzz.token_set_ratio,
            limit=limit * 2  # Get more results to filter
        )
        
        similar_companies = []
        for match_name, score, _ in results:
            if score >= threshold * 100:
                company_data = self.companies_data[match_name]
                similar_companies.append((
                    company_data.get('normalized_company', company_data['name']),
                    score / 100.0,
                    {
                        'type': company_data.get('type', 'unknown'),
                        'industry': company_data.get('industry', ''),
                        'specialization': company_data.get('specialization', '')
                    }
                ))
        
        return similar_companies[:limit]
    
    def get_companies_by_industry(self, industry: str) -> List[str]:
        """Get all companies in a specific industry"""
        industry_lower = industry.lower()
        companies = []
        
        for company_key, company_data in self.companies_data.items():
            if company_data.get('industry', '').lower() == industry_lower:
                companies.append(company_data.get('normalized_company', company_data['name']))
        
        return companies
    
    def get_companies_by_type(self, company_type: str) -> List[str]:
        """Get all companies of a specific type"""
        type_lower = company_type.lower()
        companies = []
        
        for company_key, company_data in self.companies_data.items():
            if company_data.get('type', '').lower() == type_lower:
                companies.append(company_data.get('normalized_company', company_data['name']))
        
        return companies
    
    def get_company_statistics(self) -> Dict:
        """Get statistics about loaded companies"""
        stats = {
            'total_companies': len(self.companies_data),
            'by_type': {},
            'by_industry': {},
            'by_specialization': {}
        }
        
        # Count by type
        for company_data in self.companies_data.values():
            company_type = company_data.get('type', 'unknown')
            stats['by_type'][company_type] = stats['by_type'].get(company_type, 0) + 1
        
        # Count by industry
        for company_data in self.companies_data.values():
            industry = company_data.get('industry', 'unknown')
            stats['by_industry'][industry] = stats['by_industry'].get(industry, 0) + 1
        
        # Count by specialization
        for company_data in self.companies_data.values():
            specialization = company_data.get('specialization', 'unknown')
            stats['by_specialization'][specialization] = stats['by_specialization'].get(specialization, 0) + 1
        
        return stats
    
    def validate_company_name(self, company_name: str) -> Dict:
        """
        Validate and analyze company name
        
        Args:
            company_name: Company name to validate
            
        Returns:
            Validation results with analysis
        """
        if not company_name:
            return {
                'valid': False,
                'errors': ['Empty company name'],
                'suggestions': [],
                'analysis': {}
            }
        
        analysis = {
            'original_name': company_name,
            'cleaned_name': self._clean_company_name(company_name),
            'word_count': len(company_name.split()),
            'has_suffixes': bool(re.search(r'\b(inc|llc|corp|ltd|co)\b', company_name, re.IGNORECASE)),
            'has_numbers': bool(re.search(r'\d', company_name)),
            'has_special_chars': bool(re.search(r'[^a-zA-Z0-9\s\-\.\&]', company_name)),
            'detected_industry': self._detect_industry(company_name)
        }
        
        # Check for potential issues
        errors = []
        suggestions = []
        
        if analysis['word_count'] > 5:
            errors.append('Company name seems too long')
            suggestions.append('Consider shortening the company name')
        
        if analysis['has_numbers'] and not re.search(r'\b(3m|ibm|at&t|7-11)\b', company_name, re.IGNORECASE):
            errors.append('Company name contains numbers which may be unusual')
            suggestions.append('Verify if numbers are part of the actual company name')
        
        if analysis['has_special_chars']:
            errors.append('Company name contains special characters')
            suggestions.append('Consider using standard characters only')
        
        # Try to find matches
        match_result = self.match_company(company_name, threshold=0.6)
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'suggestions': suggestions,
            'analysis': analysis,
            'best_match': match_result[0] if match_result[0] else None,
            'match_confidence': match_result[1] if match_result[0] else 0.0
        }
