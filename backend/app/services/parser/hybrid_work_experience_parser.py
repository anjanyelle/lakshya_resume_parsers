"""
Unified Work Experience Parser - Uses ALL Datasets Simultaneously
Combines pattern matching, NER, and existing parser using all unified datasets
"""

import re
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime

from app.services.parser.utils.enhanced_dataset_loader import unified_loader
from app.services.parser.work_experience_parser import WorkExperienceParser, JobEntry

logger = logging.getLogger(__name__)

@dataclass(frozen=True)
class UnifiedJobEntry(JobEntry):
    """Extended JobEntry with unified dataset metadata"""
    sources_used: List[str] = None  # All sources that contributed
    confidence: float = 0.0
    normalized_company: str = ""
    normalized_title: str = ""
    pattern_matched: str = ""
    ner_entities_found: List[str] = None

class UnifiedWorkExperienceParser:
    """
    Unified work experience parser that uses ALL datasets simultaneously:
    1. Pattern matching (unified patterns)
    2. NER extraction (unified NER entities)
    3. Existing parser logic
    4. Combine results from ALL sources
    5. Merge intelligently (no priority)
    """
    
    def __init__(self):
        self.existing_parser = WorkExperienceParser()
        self.unified_loader = unified_loader
        self.patterns = self.unified_loader.get_patterns()
        self.ner_entities = self.unified_loader.get_ner_entities()
        
        # Load pattern templates
        self._compile_patterns()
        
        logger.info("Unified Work Experience Parser initialized")
        logger.info(f"Loaded {len(self.patterns)} unified patterns")
        logger.info(f"Loaded {len(self.ner_entities)} unified NER entities")
    
    def _compile_patterns(self):
        """Compile regex patterns from unified dataset"""
        self.compiled_patterns = []
        
        for pattern_str in self.patterns:
            try:
                # Convert pattern template to regex
                regex_pattern = self._template_to_regex(pattern_str)
                if regex_pattern:
                    self.compiled_patterns.append({
                        'template': pattern_str,
                        'regex': re.compile(regex_pattern, re.IGNORECASE),
                        'type': 'pattern'
                    })
            except Exception as e:
                logger.warning(f"Failed to compile pattern: {pattern_str} - {e}")
    
    def _template_to_regex(self, template: str) -> str:
        """Convert template pattern to regex"""
        # Replace placeholders with regex groups
        regex = template
        
        # Common replacements
        replacements = {
            '<jobTitle>': r'(?P<job_title>[^|,–—()]+?)',
            '<company>': r'(?P<company>[^|,–—()]+?)',
            '<location>': r'(?P<location>[^|,–—()]+?)',
            '<date>': r'(?P<date>[^|,–—()]+?)',
        }
        
        for placeholder, pattern in replacements.items():
            regex = regex.replace(placeholder, pattern)
        
        return regex
    
    def _apply_all_pattern_matching(self, text: str) -> List[UnifiedJobEntry]:
        """Apply ALL pattern matching using unified patterns"""
        if not text or not text.strip():
            return []
        
        text = text.strip()
        matches = []
        
        for pattern_info in self.compiled_patterns:
            match = pattern_info['regex'].search(text)
            if match:
                try:
                    job_entry = self._create_job_from_pattern_match(match, pattern_info)
                    if job_entry:
                        matches.append(job_entry)
                        logger.debug(f"Pattern matched: {pattern_info['template']}")
                except Exception as e:
                    logger.warning(f"Error processing pattern match: {e}")
                    continue
        
        return matches
    
    def _create_job_from_pattern_match(self, match: re.Match, pattern_info: Dict) -> UnifiedJobEntry:
        """Create UnifiedJobEntry from pattern match"""
        groups = match.groupdict()
        
        job_entry = UnifiedJobEntry()
        job_entry.sources_used = ['pattern']
        job_entry.pattern_matched = pattern_info['template']
        job_entry.confidence = 0.8  # Base confidence for pattern matches
        
        # Extract job title
        job_title = groups.get('job_title', '').strip()
        if job_title:
            # Normalize using unified datasets
            normalized_title = self.unified_loader.normalize_job_title(job_title)
            job_entry.title = normalized_title
            job_entry.normalized_title = normalized_title
            job_entry.confidence += 0.1
        
        # Extract company
        company = groups.get('company', '').strip()
        if company:
            # Normalize using unified datasets
            normalized_company = self.unified_loader.normalize_company_name(company)
            job_entry.company = normalized_company
            job_entry.normalized_company = normalized_company
            job_entry.confidence += 0.1
        
        # Extract location
        location = groups.get('location', '').strip()
        if location:
            job_entry.location = location
        
        # Extract date
        date = groups.get('date', '').strip()
        if date:
            job_entry.date_range = date
        
        # Set confidence cap
        job_entry.confidence = min(job_entry.confidence, 1.0)
        
        return job_entry
    
    def _apply_all_ner_extraction(self, text: str) -> List[UnifiedJobEntry]:
        """Apply ALL NER extraction using unified entities"""
        if not text or not text.strip():
            return []
        
        text = text.strip()
        job_entry = UnifiedJobEntry()
        job_entry.sources_used = ['ner']
        job_entry.confidence = 0.6  # Base confidence for NER
        job_entry.ner_entities_found = []
        
        found_entities = False
        
        # Lookup companies from ALL NER entities
        for entity in self.ner_entities.get('COMPANY', []):
            if entity.lower() in text.lower():
                normalized_company = self.unified_loader.normalize_company_name(entity)
                job_entry.company = normalized_company
                job_entry.normalized_company = normalized_company
                job_entry.ner_entities_found.append(entity)
                found_entities = True
                break
        
        # Lookup job titles from ALL NER entities
        for entity in self.ner_entities.get('JOB_TITLE', []):
            if entity.lower() in text.lower():
                normalized_title = self.unified_loader.normalize_job_title(entity)
                job_entry.title = normalized_title
                job_entry.normalized_title = normalized_title
                job_entry.ner_entities_found.append(entity)
                found_entities = True
                break
        
        # Lookup locations from ALL NER entities
        for entity in self.ner_entities.get('CITY', []):
            if entity.lower() in text.lower():
                job_entry.location = entity
                job_entry.ner_entities_found.append(entity)
                found_entities = True
                break
        
        if found_entities:
            logger.debug(f"NER extraction found entities: {job_entry.ner_entities_found}")
            return [job_entry]
        
        return []
    
    def _enhance_existing_with_unified_datasets(self, entry: JobEntry) -> UnifiedJobEntry:
        """Enhance existing parser entry with ALL unified datasets"""
        enhanced_entry = UnifiedJobEntry()
        enhanced_entry.sources_used = ['existing']
        
        # Copy existing data
        enhanced_entry.title = entry.title
        enhanced_entry.company = entry.company
        enhanced_entry.location = entry.location
        enhanced_entry.start_date = entry.start_date
        enhanced_entry.end_date = entry.end_date
        enhanced_entry.description = entry.description
        enhanced_entry.date_range = entry.date_range
        enhanced_entry.confidence = 0.9  # Base confidence for existing parser
        
        # Apply normalization from ALL unified datasets
        if entry.company:
            normalized_company = self.unified_loader.normalize_company_name(entry.company)
            if normalized_company != entry.company:
                enhanced_entry.normalized_company = normalized_company
                logger.debug(f"Company normalized: {entry.company} -> {normalized_company}")
        
        if entry.title:
            normalized_title = self.unified_loader.normalize_job_title(entry.title)
            if normalized_title != entry.title:
                enhanced_entry.normalized_title = normalized_title
                logger.debug(f"Job title normalized: {entry.title} -> {normalized_title}")
        
        return enhanced_entry
    
    def _merge_all_results_intelligently(self, all_results: List[UnifiedJobEntry]) -> List[UnifiedJobEntry]:
        """
        Merge results from ALL sources intelligently:
        - Combine information from multiple sources
        - Choose best values for each field
        - Track all sources used
        """
        if not all_results:
            return []
        
        # Group by company+title combinations
        grouped = {}
        
        for result in all_results:
            # Create grouping key
            company_key = (result.normalized_company or result.company or '').lower()
            title_key = (result.normalized_title or result.title or '').lower()
            
            if company_key and title_key:
                group_key = (company_key, title_key)
            elif company_key:
                group_key = (company_key, '')
            elif title_key:
                group_key = ('', title_key)
            else:
                continue  # Skip entries without company or title
            
            if group_key not in grouped:
                grouped[group_key] = []
            grouped[group_key].append(result)
        
        # Merge each group
        merged_results = []
        for group_key, entries in grouped.items():
            merged_entry = self._merge_entry_group(entries)
            if merged_entry:
                merged_results.append(merged_entry)
        
        # Sort by confidence
        merged_results.sort(key=lambda x: x.confidence, reverse=True)
        
        return merged_results
    
    def _merge_entry_group(self, entries: List[UnifiedJobEntry]) -> Optional[UnifiedJobEntry]:
        """Merge a group of entries for the same job"""
        if not entries:
            return None
        
        # Start with the highest confidence entry as base
        entries.sort(key=lambda x: x.confidence, reverse=True)
        base_entry = entries[0]
        
        # Create merged entry
        merged = UnifiedJobEntry()
        merged.sources_used = []
        merged.confidence = base_entry.confidence
        merged.ner_entities_found = []
        
        # Collect all unique sources
        for entry in entries:
            if entry.sources_used:
                for source in entry.sources_used:
                    if source not in merged.sources_used:
                        merged.sources_used.append(source)
        
        # Merge each field with best value selection
        merged.title = self._select_best_field(entries, 'title', 'normalized_title')
        merged.company = self._select_best_field(entries, 'company', 'normalized_company')
        merged.location = self._select_best_field(entries, 'location')
        merged.start_date = self._select_best_field(entries, 'start_date')
        merged.end_date = self._select_best_field(entries, 'end_date')
        merged.description = self._select_best_field(entries, 'description')
        merged.date_range = self._select_best_field(entries, 'date_range')
        
        # Set normalized values
        if merged.company:
            merged.normalized_company = self.unified_loader.normalize_company_name(merged.company)
        if merged.title:
            merged.normalized_title = self.unified_loader.normalize_job_title(merged.title)
        
        # Collect all NER entities found
        for entry in entries:
            if entry.ner_entities_found:
                for entity in entry.ner_entities_found:
                    if entity not in merged.ner_entities_found:
                        merged.ner_entities_found.append(entity)
        
        # Adjust confidence based on number of sources
        source_boost = min(len(merged.sources_used) * 0.05, 0.2)  # Max 20% boost
        merged.confidence = min(base_entry.confidence + source_boost, 1.0)
        
        return merged
    
    def _select_best_field(self, entries: List[UnifiedJobEntry], field_name: str, 
                          normalized_field: str = None) -> str:
        """Select the best value for a field from all entries"""
        candidates = []
        
        for entry in entries:
            # Check normalized field first
            if normalized_field and hasattr(entry, normalized_field):
                norm_value = getattr(entry, normalized_field, '')
                if norm_value:
                    candidates.append(('normalized', norm_value, entry.confidence))
            
            # Check regular field
            if hasattr(entry, field_name):
                value = getattr(entry, field_name, '')
                if value:
                    candidates.append(('regular', value, entry.confidence))
        
        if not candidates:
            return ""
        
        # Sort by priority: normalized > regular, then by confidence
        candidates.sort(key=lambda x: (x[0] != 'normalized', -x[2]))
        
        # Return the best candidate
        best = candidates[0]
        return best[1]
    
    def parse_experience_section(self, text: str, source_format: str = None) -> List[UnifiedJobEntry]:
        """
        Parse experience section using ALL datasets simultaneously:
        1. Apply pattern matching (ALL patterns)
        2. Apply NER extraction (ALL entities)
        3. Use existing parser logic
        4. Combine results from ALL sources
        5. Merge intelligently
        """
        logger.info(f"Parsing experience section with ALL unified datasets")
        
        all_results = []
        
        # Step 1: Apply ALL pattern matching
        pattern_results = self._apply_all_pattern_matching(text)
        all_results.extend(pattern_results)
        logger.info(f"Pattern matching found: {len(pattern_results)} entries")
        
        # Step 2: Apply ALL NER extraction
        ner_results = self._apply_all_ner_extraction(text)
        all_results.extend(ner_results)
        logger.info(f"NER extraction found: {len(ner_results)} entries")
        
        # Step 3: Use existing parser and enhance with unified datasets
        existing_entries = self.existing_parser.parse_experience_section(text, source_format)
        enhanced_existing = []
        for entry in existing_entries:
            enhanced_entry = self._enhance_existing_with_unified_datasets(entry)
            enhanced_existing.append(enhanced_entry)
        all_results.extend(enhanced_existing)
        logger.info(f"Enhanced existing parser: {len(enhanced_existing)} entries")
        
        # Step 4: Merge all results intelligently
        final_results = self._merge_all_results_intelligently(all_results)
        
        logger.info(f"Final unified entries: {len(final_results)}")
        
        # Log source usage statistics
        source_counts = {}
        for entry in final_results:
            for source in entry.sources_used:
                source_counts[source] = source_counts.get(source, 0) + 1
        logger.info(f"Source usage: {source_counts}")
        
        return final_results
    
    def get_unified_parsing_stats(self) -> Dict[str, Any]:
        """Get comprehensive statistics about unified parsing performance"""
        dataset_stats = self.unified_loader.get_unified_dataset_stats()
        
        return {
            'patterns_loaded': len(self.compiled_patterns),
            'ner_entities_loaded': len(self.ner_entities),
            'dataset_stats': dataset_stats,
            'unified_sources': {
                'companies': dataset_stats.get('companies', {}).get('source_type_counts', {}),
                'job_titles': dataset_stats.get('job_titles', {}).get('source_type_counts', {}),
                'skills': dataset_stats.get('skills', {}).get('source_type_counts', {}),
                'total_datasets_used': sum(len(stats.get('all_source_files', [])) for stats in dataset_stats.values())
            }
        }

# Global instance
unified_parser = UnifiedWorkExperienceParser()

from app.services.parser.work_experience_parser import JobEntry

logger = logging.getLogger(__name__)

@dataclass
class HybridParseResult:
    """Result from hybrid parsing"""
    jobs: List[JobEntry]
    confidence: float
    method_used: str

class HybridWorkExperienceParser:
    """Hybrid work experience parser combining multiple strategies"""
    
    def __init__(self):
        self.parsers = []
        self._initialize_parsers()
    
    def _initialize_parsers(self):
        """Initialize different parsing strategies in priority order"""
        self.parsers = []
        
        # 1. ML Parser (Highest priority for complex patterns)
        try:
            from app.services.parser.ml_work_experience_parser import MLWorkExperienceParser
            self.parsers.append(("ML", MLWorkExperienceParser()))
            logger.info("ML parser initialized")
        except ImportError:
            logger.warning("ML parser not available")
        
        # 2. Rule-based Parser (Standard patterns)
        try:
            from app.services.parser.work_experience_parser import WorkExperienceParser
            self.parsers.append(("Rule-based", WorkExperienceParser()))
            logger.info("Rule-based parser initialized")
        except ImportError:
            logger.warning("Rule-based parser not available")
        
        # 3. LLM Parser (Final fallback for edge cases)
        try:
            from app.services.llm_service import LLMParsingService
            self.parsers.append(("LLM", LLMParsingService()))
            logger.info("LLM parser initialized")
        except ImportError:
            logger.warning("LLM parser not available")
    
    def parse_work_experience(self, text: str) -> List[JobEntry]:
        """Parse work experience using hybrid approach (ML → Rule-based → LLM)"""
        logger.info("Starting hybrid work experience parsing")
        
        best_result = None
        best_confidence = 0.0
        method_used = "None"
        
        # Try each parser in priority order
        for method_name, parser in self.parsers:
            try:
                logger.info(f"Trying {method_name} parser...")
                
                if method_name == "ML":
                    jobs = self._parse_ml(text, parser)
                    method_confidence = 1.0  # Highest confidence for ML
                elif method_name == "Rule-based":
                    jobs = self._parse_rule_based(text, parser)
                    method_confidence = 0.8  # Medium confidence for rules
                elif method_name == "LLM":
                    jobs = self._parse_llm(text, parser)
                    method_confidence = 0.6  # Lowest confidence for LLM fallback
                else:
                    continue
                    
                if jobs:
                    base_confidence = self._calculate_confidence(jobs, text)
                    weighted_confidence = base_confidence * method_confidence
                    
                    logger.info(f"{method_name} parser: {len(jobs)} jobs, confidence: {weighted_confidence:.2f}")
                    
                    if weighted_confidence > best_confidence:
                        best_confidence = weighted_confidence
                        best_result = jobs
                        method_used = method_name
                        
            except Exception as e:
                logger.error(f"{method_name} parser failed: {e}")
                continue
        
        self.method_used = method_used
        logger.info(f"Selected {method_used} parser with confidence {best_confidence:.2f}")
        
        return best_result or []
    
    def _parse_ml(self, text: str, parser) -> List[JobEntry]:
        """Parse using ML strategy"""
        logger.debug("ML parser started")
        # For now, delegate to rule-based but mark as ML attempt
        # TODO: Implement actual ML model here
        return parser.parse_experience_section(text)
    
    def _parse_rule_based(self, text: str, parser) -> List[JobEntry]:
        """Parse using rule-based strategy"""
        logger.debug("Rule-based parser started")
        return parser.parse_experience_section(text)
    
    def _parse_llm(self, text: str, parser) -> List[JobEntry]:
        """Parse using LLM strategy"""
        logger.debug("LLM parser started")
        try:
            return parser._llm_fallback(text) if hasattr(parser, '_llm_fallback') else []
        except Exception:
            return []
    
    def parse_experience_section(self, text: str, source_format: str = None) -> List[JobEntry]:
        """Parse experience section - compatibility method for pipeline"""
        return self.parse_work_experience(text)
    
    @staticmethod
    def build_date_anchor_excerpt(text: str, *, context_lines: int = 5) -> str:
        """Build date anchor excerpt - compatibility method for pipeline"""
        try:
            # Import the original method for compatibility
            from app.services.parser.work_experience_parser import WorkExperienceParser
            return WorkExperienceParser.build_date_anchor_excerpt(text, context_lines=context_lines)
        except ImportError:
            # Fallback: return first few lines
            lines = text.split('\n')
            if len(lines) <= context_lines * 2:
                return text
            return '\n'.join(lines[:context_lines * 2])
    
    def _llm_parse(self, text: str, llm_service) -> List[JobEntry]:
        """LLM parsing implementation"""
        try:
            # Use LLM service to extract work experience
            llm_result = llm_service.extract_work_experience(text)
            if not llm_result:
                return []
            
            jobs = []
            for item in llm_result:
                if isinstance(item, dict):
                    job = JobEntry(
                        company=item.get("company"),
                        title=item.get("title") or item.get("job_title"),
                        start_date=self._parse_date(item.get("start_date")),
                        end_date=self._parse_date(item.get("end_date")),
                        location=item.get("location"),
                        description=item.get("description", ""),
                        is_current=item.get("end_date") in ["present", "current", None],
                        bullets=[],
                        duration_months=None,
                        client=item.get("client"),
                        employment_type=item.get("employment_type"),
                        confidence=0.6
                    )
                    jobs.append(job)
            
            return jobs
        except Exception as e:
            logger.error(f"LLM parsing failed: {e}")
            return []
    
    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse date string to datetime"""
        if not date_str:
            return None
        
        try:
            import dateparser
            return dateparser.parse(date_str)
        except Exception:
            return None
    
    def _calculate_confidence(self, jobs: List[JobEntry], original_text: str) -> float:
        """Calculate confidence score for parsed jobs"""
        if not jobs:
            return 0.0
        
        # Base confidence on number of jobs and completeness
        confidence = 0.5
        
        # More jobs = higher confidence
        if len(jobs) >= 2:
            confidence += 0.2
        elif len(jobs) >= 3:
            confidence += 0.3
        
        # Check for complete information
        complete_jobs = 0
        for job in jobs:
            if job.company and job.title and job.start_date:
                complete_jobs += 1
        
        if complete_jobs == len(jobs):
            confidence += 0.2
        elif complete_jobs > 0:
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def _rule_based_parse(self, text: str) -> List[JobEntry]:
        """Rule-based parsing implementation"""
        jobs = []
        
        # Split by common job separators
        job_patterns = [
            r'\n(?=[A-Z][a-z]+.*\d{4})',  # Company name followed by year
            r'\n(?=\d{1,2}/\d{4})',       # Date pattern
            r'\n(?=\w+.*Present)',         # Present/current
            r'\n(?=\w+.*\d{4}-\d{4})',    # Date range
        ]
        
        job_sections = [text]
        for pattern in job_patterns:
            new_sections = []
            for section in job_sections:
                new_sections.extend(re.split(pattern, section))
            job_sections = new_sections
        
        for section in job_sections:
            if not section.strip():
                continue
            
            job = self._parse_job_section(section.strip())
            if job:
                jobs.append(job)
        
        return jobs
    
    def _parse_job_section(self, section: str) -> Optional[JobEntry]:
        """Parse a single job section"""
        lines = section.split('\n')
        if not lines:
            return None
        
        # Extract information from lines
        company = ""
        title = ""
        location = ""
        start_date = None
        end_date = None
        description = ""
        
        # Find dates
        date_pattern = r'(\d{1,2}/\d{4}|\d{4}-\d{1,2}|\w+ \d{4}|\d{4}|\w+ \d{4} - \w+ \d{4}|\w+ \d{4} - Present|Present)'
        dates = []
        for line in lines:
            found_dates = re.findall(date_pattern, line)
            dates.extend(found_dates)
        
        # Extract company and title from first line
        first_line = lines[0].strip()
        
        # Remove dates from first line
        clean_line = re.sub(date_pattern, '', first_line).strip()
        
        # Look for common patterns
        if ' at ' in clean_line:
            parts = clean_line.split(' at ')
            title = parts[0].strip()
            company = parts[1].strip()
        elif '@' in clean_line:
            parts = clean_line.split('@')
            title = parts[0].strip()
            company = parts[1].strip()
        else:
            # Try to identify company and title
            words = clean_line.split()
            if len(words) >= 2:
                # Assume first word(s) are title, last is company
                title = ' '.join(words[:-1])
                company = words[-1]
        
        # Extract location
        for line in lines:
            if re.search(r', [A-Z]{2}|^[A-Z][a-z]+, [A-Z]{2}', line):
                location = line.strip()
                break
        
        # Parse dates
        if dates:
            start_date = self._parse_date(dates[0])
            if len(dates) > 1:
                end_date = self._parse_date(dates[1])
        
        # Extract description (everything after the first line that's not dates/location)
        description_lines = []
        for line in lines[1:]:
            if not re.search(date_pattern, line) and line.strip():
                description_lines.append(line.strip())
        
        description = '\n'.join(description_lines)
        
        # Clean up description
        description = re.sub(r'^\s*[•·]\s*', '- ', description, flags=re.MULTILINE)
        description = re.sub(r'^\s*\d+\.\s*', '- ', description, flags=re.MULTILINE)
        
        # Validate we have minimum required info
        if not title or not company:
            return None
        
        return JobEntry(
            company=company,
            title=title,
            location=location,
            start_date=start_date,
            end_date=end_date,
            description=description
        )
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse date string to datetime"""
        if not date_str or date_str.lower() in ['present', 'current', 'ongoing']:
            return None
        
        try:
            # Try different date formats
            formats = [
                '%m/%Y',
                '%Y-%m',
                '%B %Y',
                '%b %Y',
                '%Y',
                '%m-%Y',
                '%Y/%m',
                '%m/%d/%Y',
                '%Y-%m-%d'
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue
        except Exception:
            pass
        
        return None
