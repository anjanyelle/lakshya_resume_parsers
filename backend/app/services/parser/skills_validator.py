"""
Skills Validator with Category Mapping and Confidence Scoring
Provides intelligent skill validation, categorization, and relationship analysis
"""

import re
import logging
from typing import Dict, List, Tuple, Optional, Set
from rapidfuzz import fuzz, process
from collections import defaultdict

logger = logging.getLogger(__name__)

class SkillsValidator:
    """
    Advanced skills validator with category mapping,
    confidence scoring, and skill relationship analysis
    """
    
    def __init__(self, skills_data: Dict):
        self.skills_data = skills_data
        
        # Build search indexes
        self.skill_index = self._build_skill_index()
        self.category_index = self._build_category_index()
        self.subcategory_index = self._build_subcategory_index()
        
        # Skill patterns and variations
        self.skill_variations = self._build_skill_variations()
        self.technical_patterns = self._build_technical_patterns()
        self.certification_patterns = self._build_certification_patterns()
        
        # Skill relationship mappings
        self.skill_relationships = self._build_skill_relationships()
        self.industry_skills = self._build_industry_skills()
        
        # Common skill combinations
        self.skill_combinations = self._build_skill_combinations()
        
        logger.info(f"SkillsValidator initialized with {len(skills_data)} skills")
    
    def _build_skill_index(self) -> List[str]:
        """Build searchable index of skill names"""
        return list(self.skills_data.keys())
    
    def _build_category_index(self) -> Dict[str, List[str]]:
        """Build index of skills by category"""
        category_index = {}
        
        for skill_key, skill_data in self.skills_data.items():
            category = skill_data.get('category', '').lower()
            if category:
                if category not in category_index:
                    category_index[category] = []
                category_index[category].append(skill_key)
        
        return category_index
    
    def _build_subcategory_index(self) -> Dict[str, List[str]]:
        """Build index of skills by subcategory"""
        subcategory_index = {}
        
        for skill_key, skill_data in self.skills_data.items():
            subcategory = skill_data.get('subcategory', '').lower()
            if subcategory:
                if subcategory not in subcategory_index:
                    subcategory_index[subcategory] = []
                subcategory_index[subcategory].append(skill_key)
        
        return subcategory_index
    
    def _build_skill_variations(self) -> Dict[str, List[str]]:
        """Build common skill variations and synonyms"""
        return {
            'javascript': ['js', 'javascript', 'ecmascript', 'es6', 'es5'],
            'typescript': ['ts', 'typescript', 'ts'],
            'python': ['python', 'py', 'python3', 'python 3'],
            'java': ['java', 'jvm', 'jdk', 'jre'],
            'c++': ['c++', 'cpp', 'c plus plus'],
            'c#': ['c#', 'csharp', 'c sharp', '.net'],
            'sql': ['sql', 'structured query language', 'mysql', 'postgresql', 'postgresql'],
            'html': ['html', 'html5', 'hyperlink text markup language'],
            'css': ['css', 'css3', 'cascading style sheets'],
            'react': ['react', 'reactjs', 'react.js', 'reactjs'],
            'angular': ['angular', 'angularjs', 'angular.js', 'angular 2'],
            'vue': ['vue', 'vuejs', 'vue.js', 'vuejs'],
            'node': ['node', 'nodejs', 'node.js', 'nodejs'],
            'aws': ['aws', 'amazon web services', 'amazon cloud'],
            'azure': ['azure', 'microsoft azure', 'ms azure'],
            'docker': ['docker', 'docker container', 'containerization'],
            'kubernetes': ['kubernetes', 'k8s', 'k8s', 'kube'],
            'git': ['git', 'git version control', 'git scm'],
            'machine learning': ['machine learning', 'ml', 'machine learning'],
            'artificial intelligence': ['artificial intelligence', 'ai', 'artificial intelligence'],
            'deep learning': ['deep learning', 'dl', 'deep learning'],
            'data science': ['data science', 'ds', 'data science'],
            'business intelligence': ['business intelligence', 'bi', 'business intelligence'],
            'user experience': ['user experience', 'ux', 'user experience'],
            'user interface': ['user interface', 'ui', 'user interface'],
            'quality assurance': ['quality assurance', 'qa', 'quality assurance'],
            'continuous integration': ['continuous integration', 'ci', 'continuous integration'],
            'continuous deployment': ['continuous deployment', 'cd', 'continuous deployment'],
            'devops': ['devops', 'development operations', 'devops'],
            'agile': ['agile', 'agile methodology', 'scrum', 'kanban'],
            'project management': ['project management', 'pm', 'pmp', 'project management'],
            'customer relationship management': ['customer relationship management', 'crm', 'crm'],
            'enterprise resource planning': ['enterprise resource planning', 'erp', 'erp'],
            'content management system': ['content management system', 'cms', 'cms']
        }
    
    def _build_technical_patterns(self) -> Dict[str, str]:
        """Build patterns for identifying technical skills"""
        return {
            'programming_languages': r'\b(python|java|javascript|typescript|c\+\+|c#|php|ruby|go|rust|swift|kotlin|scala|perl|bash|powershell|sql|r|matlab|lua|dart|elixir|haskell|f#|objective-c|vb\.net)\b',
            'web_technologies': r'\b(html|html5|css|css3|sass|less|bootstrap|tailwind|jquery|ajax|json|xml|rest|soap|graphql|websockets|http|https)\b',
            'frameworks': r'\b(react|angular|vue|django|flask|spring|laravel|rails|express|fastapi|asp\.net|next|nuxt|gatsby|ember|backbone|svelte|solid)\b',
            'databases': r'\b(mysql|postgresql|mongodb|sqlite|oracle|sql server|cassandra|redis|elasticsearch|dynamodb|firebase|supabase|cockroachdb|neo4j|influxdb)\b',
            'cloud_platforms': r'\b(aws|azure|gcp|google cloud|heroku|digitalocean|vultr|linode|alibaba cloud|ibm cloud|oracle cloud)\b',
            'devops_tools': r'\b(docker|kubernetes|jenkins|gitlab ci|github actions|circleci|travis ci|bamboo|terraform|ansible|puppet|chef|saltstack|vagrant)\b',
            'mobile_development': r'\b(ios|android|react native|flutter|swift|kotlin|xamarin|cordova|ionic|phonegap|native script)\b',
            'data_science': r'\b(pandas|numpy|scipy|matplotlib|seaborn|plotly|jupyter|tensorflow|pytorch|keras|scikit-learn|spark|hadoop|mapreduce)\b',
            'testing': r'\b(jest|mocha|jasmine|karma|cypress|playwright|selenium|webdriver|pytest|unittest|rspec|minitest)\b',
            'version_control': r'\b(git|svn|mercurial|bitbucket|github|gitlab|sourceforge|gitkraken|sourcetree)\b',
            'api_protocols': r'\b(rest|soap|graphql|grpc|websockets|mqtt|amqp|protobuf|openapi|swagger)\b',
            'monitoring': r'\b(prometheus|grafana|datadog|new relic|splunk|elk|elasticsearch|logstash|kibana|sentry|bugsnag)\b',
            'security': r'\b(owasp|ssl|tls|oauth|jwt|rbac|acl|encryption|firewall|ids|ips|siem|penetration testing)\b'
        }
    
    def _build_certification_patterns(self) -> Dict[str, str]:
        """Build patterns for identifying certifications"""
        return {
            'aws_certifications': r'\b(aws certified solutions architect|aws certified developer|aws certified sysops|aws certified devops|aws certified data analytics)\b',
            'microsoft_certifications': r'\b(microsoft certified professional|mcp|microsoft certified solutions expert|mcse|microsoft certified azure|azure administrator)\b',
            'google_certifications': r'\b(google certified professional cloud architect|gcp|google certified associate cloud engineer|google certified data engineer)\b',
            'security_certifications': r'\b(cissp|cisa|cism|ceh|compTIA security\+|oscp|giac|iso 27001)\b',
            'project_management': r'\b(pmp|prince2|agile certified practitioner|scrum master|certified associate in project management)\b',
            'itil': r'\b(itil foundation|itil practitioner|itil expert|itil master)\b',
            'database_certifications': r'\b(oracle certified professional|mysql certified|mongodb certified|sql server certified)\b',
            'programming_certifications': r'\b(java certified programmer|python certified|microsoft certified solutions developer)\b'
        }
    
    def _build_skill_relationships(self) -> Dict[str, List[str]]:
        """Build skill relationship mappings"""
        return {
            'javascript': ['react', 'node', 'angular', 'vue', 'typescript', 'html', 'css'],
            'python': ['django', 'flask', 'pandas', 'numpy', 'tensorflow', 'pytorch', 'scikit-learn'],
            'java': ['spring', 'maven', 'gradle', 'junit', 'hibernate', 'jvm'],
            'react': ['javascript', 'typescript', 'html', 'css', 'redux', 'webpack'],
            'docker': ['kubernetes', 'containerization', 'devops', 'microservices'],
            'kubernetes': ['docker', 'devops', 'microservices', 'helm', 'istio'],
            'aws': ['cloud computing', 'devops', 'lambda', 'ec2', 's3', 'rds'],
            'machine learning': ['python', 'tensorflow', 'pytorch', 'scikit-learn', 'pandas'],
            'data science': ['python', 'r', 'sql', 'pandas', 'numpy', 'statistics'],
            'devops': ['docker', 'kubernetes', 'ci/cd', 'jenkins', 'git', 'linux'],
            'full stack': ['javascript', 'python', 'html', 'css', 'sql', 'react', 'node'],
            'mobile': ['ios', 'android', 'react native', 'flutter', 'swift', 'kotlin']
        }
    
    def _build_industry_skills(self) -> Dict[str, List[str]]:
        """Build industry-specific skill mappings"""
        return {
            'technology': [
                'programming', 'software development', 'web development', 'mobile development',
                'cloud computing', 'devops', 'cybersecurity', 'data science', 'ai/ml',
                'database management', 'network administration', 'system administration'
            ],
            'finance': [
                'financial analysis', 'accounting', 'risk management', 'investment banking',
                'financial modeling', 'compliance', 'trading', 'fintech', 'blockchain'
            ],
            'healthcare': [
                'medical terminology', 'healthcare it', 'electronic health records', 'hipaa',
                'medical billing', 'clinical research', 'pharmaceutical', 'biotechnology'
            ],
            'marketing': [
                'digital marketing', 'seo', 'sem', 'content marketing', 'social media',
                'analytics', 'branding', 'market research', 'email marketing', 'crm'
            ],
            'sales': [
                'salesforce', 'crm', 'negotiation', 'business development', 'account management',
                'lead generation', 'customer relationship management', 'sales strategy'
            ],
            'consulting': [
                'management consulting', 'strategy consulting', 'business analysis',
                'process improvement', 'change management', 'stakeholder management'
            ],
            'education': [
                'curriculum development', 'educational technology', 'online learning',
                'instructional design', 'academic research', 'student management'
            ],
            'legal': [
                'legal research', 'contract management', 'compliance', 'regulatory affairs',
                'intellectual property', 'corporate law', 'litigation'
            ],
            'manufacturing': [
                'quality control', 'supply chain management', 'lean manufacturing',
                'six sigma', 'production planning', 'inventory management', 'automation'
            ],
            'retail': [
                'inventory management', 'point of sale', 'merchandising', 'customer service',
                'e-commerce', 'supply chain', 'store management', 'visual merchandising'
            ]
        }
    
    def _build_skill_combinations(self) -> Dict[str, List[str]]:
        """Build common skill combinations"""
        return {
            'full_stack_developer': ['javascript', 'html', 'css', 'react', 'node', 'sql'],
            'data_scientist': ['python', 'pandas', 'numpy', 'machine learning', 'statistics', 'sql'],
            'devops_engineer': ['docker', 'kubernetes', 'ci/cd', 'linux', 'cloud computing', 'automation'],
            'mobile_developer': ['react native', 'flutter', 'ios', 'android', 'mobile ui'],
            'backend_developer': ['python', 'java', 'node', 'sql', 'api', 'microservices'],
            'frontend_developer': ['javascript', 'react', 'vue', 'angular', 'html', 'css'],
            'cloud_architect': ['aws', 'azure', 'gcp', 'devops', 'security', 'architecture'],
            'cybersecurity_analyst': ['security', 'network security', 'risk assessment', 'compliance'],
            'product_manager': ['product strategy', 'user research', 'agile', 'analytics', 'stakeholder management'],
            'ux_designer': ['user research', 'wireframing', 'prototyping', 'usability testing', 'design tools']
        }
    
    def validate_skill(self, skill: str, use_fuzzy: bool = True) -> Tuple[bool, Dict, float]:
        """
        Validate skill with confidence scoring
        
        Args:
            skill: Skill name to validate
            use_fuzzy: Whether to use fuzzy matching
            
        Returns:
            Tuple of (is_valid, skill_data, confidence_score)
        """
        if not skill:
            return False, {}, 0.0
        
        skill_lower = skill.strip().lower()
        
        # Exact match first
        if skill_lower in self.skills_data:
            return True, self.skills_data[skill_lower], 1.0
        
        # Try variation matching
        variation_result = self._variation_match(skill_lower)
        if variation_result:
            return True, variation_result['data'], variation_result['confidence']
        
        # Try pattern matching for technical skills
        pattern_result = self._pattern_match(skill)
        if pattern_result:
            return True, pattern_result['data'], pattern_result['confidence']
        
        # Try fuzzy matching
        if use_fuzzy and self.skill_index:
            fuzzy_result = self._fuzzy_match(skill)
            if fuzzy_result:
                return True, fuzzy_result['data'], fuzzy_result['confidence']
        
        # Try partial matching
        partial_result = self._partial_match(skill)
        if partial_result:
            return True, partial_result['data'], partial_result['confidence']
        
        return False, {}, 0.0
    
    def _variation_match(self, skill_lower: str) -> Optional[Dict]:
        """Try matching with skill variations"""
        for canonical_skill, variations in self.skill_variations.items():
            for variation in variations:
                if variation in skill_lower or skill_lower in variation:
                    # Find the canonical skill in our data
                    for skill_key, skill_data in self.skills_data.items():
                        if canonical_skill.lower() in skill_key.lower():
                            return {
                                'data': skill_data,
                                'confidence': 0.9,
                                'match_type': 'variation'
                            }
        
        return None
    
    def _pattern_match(self, skill: str) -> Optional[Dict]:
        """Try matching with technical patterns"""
        skill_lower = skill.lower()
        
        for pattern_type, pattern in self.technical_patterns.items():
            if re.search(pattern, skill_lower):
                # Create skill data for pattern match
                category = self._infer_category_from_pattern(pattern_type)
                return {
                    'data': {
                        'category': category,
                        'subcategory': pattern_type,
                        'level': 'Intermediate'
                    },
                    'confidence': 0.8,
                    'match_type': 'pattern'
                }
        
        return None
    
    def _infer_category_from_pattern(self, pattern_type: str) -> str:
        """Infer category from pattern type"""
        category_mapping = {
            'programming_languages': 'Programming',
            'web_technologies': 'Web Development',
            'frameworks': 'Web Development',
            'databases': 'Database',
            'cloud_platforms': 'Cloud Computing',
            'devops_tools': 'DevOps',
            'mobile_development': 'Mobile Development',
            'data_science': 'Data Science',
            'testing': 'Testing',
            'version_control': 'Version Control',
            'api_protocols': 'API Development',
            'monitoring': 'Monitoring',
            'security': 'Security'
        }
        
        return category_mapping.get(pattern_type, 'Technical')
    
    def _fuzzy_match(self, skill: str) -> Optional[Dict]:
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
                skill,
                self.skill_index,
                scorer=scorer,
                score_cutoff=75
            )
            
            if result:
                match_name, score, _ = result
                if score > best_score:
                    best_score = score
                    skill_data = self.skills_data[match_name]
                    best_match = {
                        'data': skill_data,
                        'confidence': score / 100.0,
                        'match_type': f'fuzzy_{strategy_name}'
                    }
        
        return best_match
    
    def _partial_match(self, skill: str) -> Optional[Dict]:
        """Try partial matching for skill substrings"""
        words = skill.split()
        if len(words) < 2:
            return None
        
        # Try matching with first 2-3 words
        for i in range(2, min(4, len(words) + 1)):
            partial_skill = ' '.join(words[:i])
            result = self._fuzzy_match(partial_skill)
            
            if result:
                result['match_type'] = f'partial_{i}words'
                return result
        
        return None
    
    def categorize_skills(self, skills: List[str]) -> Dict[str, List[Tuple[str, float]]]:
        """
        Categorize a list of skills
        
        Args:
            skills: List of skill names
            
        Returns:
            Dictionary mapping categories to list of (skill, confidence) tuples
        """
        categorized = defaultdict(list)
        
        for skill in skills:
            is_valid, skill_data, confidence = self.validate_skill(skill)
            if is_valid:
                category = skill_data.get('category', 'General')
                categorized[category].append((skill, confidence))
        
        return dict(categorized)
    
    def find_related_skills(self, skill: str, limit: int = 10) -> List[Tuple[str, float]]:
        """
        Find related skills based on relationships
        
        Args:
            skill: Reference skill
            limit: Maximum number of results
            
        Returns:
            List of (related_skill, relevance_score) tuples
        """
        skill_lower = skill.lower()
        related_skills = []
        
        # Check direct relationships
        for related_skill, connections in self.skill_relationships.items():
            if skill_lower in connections or related_skill.lower() in connections:
                # Calculate relevance based on connection strength
                relevance = 0.8 if skill_lower in connections else 0.6
                related_skills.append((related_skill, relevance))
        
        # Check category-based relationships
        is_valid, skill_data, _ = self.validate_skill(skill, use_fuzzy=False)
        if is_valid:
            category = skill_data.get('category', '').lower()
            if category in self.category_index:
                category_skills = self.category_index[category]
                for category_skill in category_skills[:limit]:
                    if category_skill != skill_lower:
                        related_skills.append((category_skill, 0.5))
        
        # Sort by relevance and limit results
        related_skills.sort(key=lambda x: x[1], reverse=True)
        return related_skills[:limit]
    
    def detect_skill_combinations(self, skills: List[str]) -> List[Tuple[str, float, List[str]]]:
        """
        Detect common skill combinations
        
        Args:
            skills: List of skills to analyze
            
        Returns:
            List of (combination_name, confidence, matching_skills) tuples
        """
        skill_set = set(skill.lower() for skill in skills)
        detected_combinations = []
        
        for combo_name, combo_skills in self.skill_combinations.items():
            combo_set = set(skill.lower() for skill in combo_skills)
            
            # Calculate overlap
            overlap = skill_set.intersection(combo_set)
            if overlap:
                confidence = len(overlap) / len(combo_set)
                if confidence >= 0.5:  # At least 50% of skills match
                    detected_combinations.append((combo_name, confidence, list(overlap)))
        
        # Sort by confidence
        detected_combinations.sort(key=lambda x: x[1], reverse=True)
        return detected_combinations
    
    def infer_industry_from_skills(self, skills: List[str]) -> Tuple[Optional[str], float]:
        """
        Infer industry from skill set
        
        Args:
            skills: List of skills
            
        Returns:
            Tuple of (industry, confidence_score)
        """
        industry_scores = {}
        
        for industry, industry_skills in self.industry_skills.items():
            skill_set = set(skill.lower() for skill in skills)
            industry_set = set(skill.lower() for skill in industry_skills)
            
            overlap = skill_set.intersection(industry_set)
            if overlap:
                score = len(overlap) / len(industry_set)
                industry_scores[industry] = score
        
        if not industry_scores:
            return None, 0.0
        
        # Return industry with highest score
        best_industry = max(industry_scores, key=industry_scores.get)
        confidence = industry_scores[best_industry]
        
        # Only return if we have reasonable confidence
        if confidence >= 0.3:
            return best_industry, confidence
        
        return None, 0.0
    
    def validate_certification(self, cert: str) -> Tuple[bool, str, float]:
        """
        Validate certification name
        
        Args:
            cert: Certification name to validate
            
        Returns:
            Tuple of (is_valid, normalized_cert, confidence_score)
        """
        if not cert:
            return False, "", 0.0
        
        cert_lower = cert.lower()
        
        # Check certification patterns
        for cert_type, pattern in self.certification_patterns.items():
            if re.search(pattern, cert_lower):
                return True, cert.strip(), 0.9
        
        # Try fuzzy matching with known certifications
        is_valid, skill_data, confidence = self.validate_skill(cert)
        if is_valid and skill_data.get('category') == 'Certification':
            return True, skill_data.get('subcategory', cert.strip()), confidence
        
        return False, cert.strip(), 0.0
    
    def get_skill_statistics(self) -> Dict:
        """Get statistics about loaded skills"""
        stats = {
            'total_skills': len(self.skills_data),
            'by_category': {},
            'by_subcategory': {},
            'by_level': {
                'Expert': 0,
                'Advanced': 0,
                'Intermediate': 0,
                'Beginner': 0,
                'Unspecified': 0
            }
        }
        
        # Count by category
        for skill_data in self.skills_data.values():
            category = skill_data.get('category', 'unknown')
            stats['by_category'][category] = stats['by_category'].get(category, 0) + 1
        
        # Count by subcategory
        for skill_data in self.skills_data.values():
            subcategory = skill_data.get('subcategory', 'unknown')
            stats['by_subcategory'][subcategory] = stats['by_subcategory'].get(subcategory, 0) + 1
        
        # Count by level
        for skill_data in self.skills_data.values():
            level = skill_data.get('level', 'unspecified')
            if level in stats['by_level']:
                stats['by_level'][level] += 1
            else:
                stats['by_level']['Unspecified'] += 1
        
        return stats
    
    def analyze_skill_profile(self, skills: List[str]) -> Dict:
        """
        Analyze a skill profile
        
        Args:
            skills: List of skills to analyze
            
        Returns:
            Comprehensive skill profile analysis
        """
        # Validate all skills
        validated_skills = []
        invalid_skills = []
        
        for skill in skills:
            is_valid, skill_data, confidence = self.validate_skill(skill)
            if is_valid:
                validated_skills.append({
                    'name': skill,
                    'data': skill_data,
                    'confidence': confidence
                })
            else:
                invalid_skills.append(skill)
        
        # Categorize skills
        categorized = self.categorize_skills(skills)
        
        # Find related skills
        related_skills = {}
        for skill in validated_skills:
            related = self.find_related_skills(skill['name'], limit=5)
            related_skills[skill['name']] = related
        
        # Detect combinations
        combinations = self.detect_skill_combinations(skills)
        
        # Infer industry
        industry, industry_confidence = self.infer_industry_from_skills(skills)
        
        # Calculate skill diversity
        categories_count = len(categorized)
        total_validated = len(validated_skills)
        
        # Identify top categories
        top_categories = sorted(
            categorized.items(),
            key=lambda x: len(x[1]),
            reverse=True
        )[:5]
        
        return {
            'total_skills': len(skills),
            'validated_skills': total_validated,
            'invalid_skills': len(invalid_skills),
            'validation_rate': total_validated / len(skills) if skills else 0,
            'categories': categorized,
            'top_categories': [(cat, len(skills_list)) for cat, skills_list in top_categories],
            'category_diversity': categories_count,
            'related_skills': related_skills,
            'skill_combinations': combinations,
            'inferred_industry': industry,
            'industry_confidence': industry_confidence,
            'invalid_skill_list': invalid_skills
        }
