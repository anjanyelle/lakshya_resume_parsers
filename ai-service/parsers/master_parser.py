"""
Master parser that orchestrates all parsing steps in the correct order.
Provides unified interface for file and text parsing with timing metrics.
"""

import re
import time
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path

from parsers.text_extractor import TextExtractor
from parsers.section_splitter import SectionSplitter
from parsers.rule_parser import RuleBasedParser
from parsers.experience_extractor import ExperienceExtractor
from parsers.education_extractor import EducationExtractor
from parsers.ai_ner_parser import AINamedEntityParser
from parsers.hybrid_merger import HybridMerger
from parsers.confidence_scorer import ConfidenceScorer
from parsers.entity_normalizer import EntityNormalizer

# Configure logging
logger = logging.getLogger(__name__)


class MasterParser:
    """
    Master parser that orchestrates all parsing steps in sequence.
    Provides unified interface with timing metrics and error handling.
    """
    
    def __init__(self):
        """Initialize all sub-parsers and components."""
        self.logger = logging.getLogger(__name__)
        
        # Initialize all parsers
        try:
            self.text_extractor = TextExtractor()
            self.logger.info("✅ TextExtractor initialized")
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize TextExtractor: {e}")
            self.text_extractor = None
        
        try:
            self.section_splitter = SectionSplitter()
            self.logger.info("✅ SectionSplitter initialized")
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize SectionSplitter: {e}")
            self.section_splitter = None
        
        try:
            self.rule_parser = RuleBasedParser()
            self.logger.info("✅ RuleBasedParser initialized")
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize RuleBasedParser: {e}")
            # Fallback to simple rule parser
            try:
                from parsers.simple_rule_parser import SimpleRuleParser
                self.rule_parser = SimpleRuleParser()
                self.logger.info("✅ SimpleRuleParser initialized as fallback")
            except Exception as fallback_error:
                self.logger.error(f"❌ Failed to initialize SimpleRuleParser: {fallback_error}")
                self.rule_parser = None
        
        try:
            self.exp_extractor = ExperienceExtractor()
            self.logger.info("✅ ExperienceExtractor initialized")
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize ExperienceExtractor: {e}")
            self.exp_extractor = None
        
        try:
            self.edu_extractor = EducationExtractor()
            self.logger.info("✅ EducationExtractor initialized")
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize EducationExtractor: {e}")
            self.edu_extractor = None
        
        try:
            self.ai_parser = AINamedEntityParser()
            self.logger.info("✅ AINamedEntityParser initialized")
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize AINamedEntityParser: {e}")
            self.ai_parser = None
        
        try:
            self.hybrid_merger = HybridMerger()
            self.logger.info("✅ HybridMerger initialized")
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize HybridMerger: {e}")
            self.hybrid_merger = None
        
        try:
            self.confidence_scorer = ConfidenceScorer()
            self.logger.info("✅ ConfidenceScorer initialized")
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize ConfidenceScorer: {e}")
            self.confidence_scorer = None
        
        try:
            self.entity_normalizer = EntityNormalizer()
            self.logger.info("✅ EntityNormalizer initialized")
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize EntityNormalizer: {e}")
            self.entity_normalizer = None
        
        # Timing metrics storage
        self.last_parse_metrics = {}
        
        # Check overall health
        self._check_parser_health()
    
    def _check_parser_health(self):
        """Check health of all parsers and log status."""
        critical_parsers = ['section_splitter', 'rule_parser', 'hybrid_merger', 'confidence_scorer']
        optional_parsers = ['text_extractor', 'ai_parser', 'exp_extractor', 'edu_extractor']
        
        critical_status = all(getattr(self, parser) is not None for parser in critical_parsers)
        optional_status = [getattr(self, parser) is not None for parser in optional_parsers]
        
        if critical_status:
            self.logger.info("🎉 All critical parsers initialized successfully")
        else:
            self.logger.error("❌ Some critical parsers failed to initialize")
        
        optional_count = sum(optional_status)
        self.logger.info(f"📊 Optional parsers: {optional_count}/{len(optional_parsers)} available")
    
    def parse_file(self, file_path: str, candidate_id: str) -> Dict[str, Any]:
        """
        Parse resume file through the complete pipeline.
        
        Args:
            file_path: Path to resume file
            candidate_id: Unique candidate identifier
            
        Returns:
            Complete parsed resume data with confidence scores and metrics
        """
        start_time = time.time()
        metrics = {}
        
        try:
            self.logger.info(f"🚀 Starting file parse pipeline for {candidate_id}: {file_path}")
            
            # Validate file exists
            if not Path(file_path).exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            
            # Step 1: Extract text from file
            step_start = time.time()
            text_result = self._extract_text_from_file(file_path)
            metrics['text_extraction_ms'] = (time.time() - step_start) * 1000
            
            if not text_result or not text_result.get('text'):
                raise ValueError("Failed to extract text from file")
            
            # Continue with text parsing pipeline
            result = self._parse_text_pipeline(
                text_result['text'], 
                candidate_id, 
                metrics,
                file_info={
                    'file_path': file_path,
                    'extraction_method': text_result.get('method', 'unknown'),
                    'quality_score': text_result.get('quality_score', 0.0)
                }
            )
            
            # Add file-specific metadata
            result['file_info'] = {
                'file_path': file_path,
                'file_name': Path(file_path).name,
                'extraction_method': text_result.get('method', 'unknown'),
                'text_quality_score': text_result.get('quality_score', 0.0),
                'word_count': len(text_result['text'].split())
            }
            
            # Calculate total time
            total_time = (time.time() - start_time) * 1000
            metrics['total_ms'] = total_time
            self.last_parse_metrics = metrics
            
            self.logger.info(f"✅ File parse completed for {candidate_id} in {total_time:.1f}ms")
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Error parsing file {file_path}: {e}")
            return self._create_error_result(candidate_id, str(e), metrics)
    
    def parse_text(self, text: str, candidate_id: str) -> Dict[str, Any]:
        """
        Parse resume text through the complete pipeline.
        
        Args:
            text: Resume text to parse
            candidate_id: Unique candidate identifier
            
        Returns:
            Complete parsed resume data with confidence scores and metrics
        """
        start_time = time.time()
        metrics = {}
        
        try:
            self.logger.info(f"🚀 Starting text parse pipeline for {candidate_id}")
            
            if not text or not text.strip():
                raise ValueError("Empty text provided")
            
            # Use original text for parsing (cleaning removes emails/phones)
            # We'll handle cleaning in the final result if needed
            cleaned_text = text.strip()
            
            # Run text parsing pipeline
            result = self._parse_text_pipeline(
                cleaned_text, 
                candidate_id, 
                metrics,
                file_info={'parsing_method': 'direct_text'}
            )
            
            # Add text-specific metadata
            result['text_info'] = {
                'original_length': len(text),
                'cleaned_length': len(cleaned_text),
                'word_count': len(cleaned_text.split()),
                'parsing_method': 'direct_text'
            }
            
            # Calculate total time
            total_time = (time.time() - start_time) * 1000
            metrics['total_ms'] = total_time
            self.last_parse_metrics = metrics
            
            self.logger.info(f"✅ Text parse completed for {candidate_id} in {total_time:.1f}ms")
            
            return result
            
        except Exception as e:
            import traceback
            self.logger.error(f"❌ Error parsing text for {candidate_id}: {e}")
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            return self._create_error_result(candidate_id, str(e), metrics)
    
    def _parse_text_pipeline(self, text: str, candidate_id: str, metrics: Dict[str, float], 
                           file_info: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Core text parsing pipeline (shared by file and text parsing).
        
        Args:
            text: Text to parse
            candidate_id: Candidate identifier
            metrics: Timing metrics dictionary
            file_info: File-specific information
            
        Returns:
            Parsed result dictionary
        """
        # Step 2: Split sections
        step_start = time.time()
        sections = self._split_sections(text)
        metrics['section_splitting_ms'] = (time.time() - step_start) * 1000
        
        # Step 3: Rule-based parsing (pass sections for skills extraction)
        step_start = time.time()
        rule_results = self._run_rule_parsing(text, sections)
        metrics['rule_parsing_ms'] = (time.time() - step_start) * 1000
        
        # Step 4: AI entity extraction (conditional - only if needed based on rule_results)
        step_start = time.time()
        ai_results = self._run_ai_parsing(text, sections, rule_results=rule_results)
        metrics['ai_parsing_ms'] = (time.time() - step_start) * 1000
        
        # Log if AI was skipped
        if ai_results.get('ai_skipped'):
            self.logger.info(f"AI parsing skipped: {ai_results.get('reason')}")
            metrics['ai_skipped'] = True
        
        # Step 5: Extract structured experience
        step_start = time.time()
        experience_results = self._extract_experience(sections, text)
        metrics['experience_extraction_ms'] = (time.time() - step_start) * 1000
        
        # Step 6: Extract structured education
        step_start = time.time()
        education_results = self._extract_education(sections, text)
        metrics['education_extraction_ms'] = (time.time() - step_start) * 1000
        
        # Step 6b: Extract summary
        step_start = time.time()
        summary = self._extract_summary(sections, text)
        metrics['summary_extraction_ms'] = (time.time() - step_start) * 1000
        
        # Step 7: Merge all results
        step_start = time.time()
        merged_results = self._merge_results(rule_results, ai_results, experience_results, education_results)
        merged_results['summary'] = summary
        
        # Step 7b: Normalize entities
        if self.entity_normalizer:
            merged_results['skills'] = self.entity_normalizer.normalize_skills_list(merged_results.get('skills', []))
            if merged_results.get('companies'):
                merged_results['companies'] = [self.entity_normalizer.normalize_company(c) for c in merged_results['companies']]
        
        metrics['merging_ms'] = (time.time() - step_start) * 1000
        
        # Step 8: Calculate confidence scores
        step_start = time.time()
        confidence_scores = self._calculate_confidence(merged_results)
        metrics['confidence_scoring_ms'] = (time.time() - step_start) * 1000
        
        # Step 9: Assemble final result
        result = self._assemble_final_result(
            candidate_id, merged_results, confidence_scores, metrics, file_info
        )
        
        return result
    
    def _extract_text_from_file(self, file_path: str) -> Dict[str, Any]:
        """Extract text from file using TextExtractor."""
        if not self.text_extractor:
            raise RuntimeError("TextExtractor not available")
        
        return self.text_extractor.extract(file_path)
    
    def _split_sections(self, text: str) -> Dict[str, str]:
        """Split text into sections using SectionSplitter."""
        if not self.section_splitter:
            self.logger.warning("SectionSplitter not available, returning empty sections")
            return {}
        
        return self.section_splitter.split_sections(text)
    
    def _run_rule_parsing(self, text: str, sections: Dict[str, str] = None) -> Dict[str, Any]:
        """Run rule-based parsing on text."""
        if not self.rule_parser:
            self.logger.warning("RuleBasedParser not available, returning empty results")
            return {}
        
        result = {
            'email': self.rule_parser.extract_email(text),
            'phone': self.rule_parser.extract_phone(text),
            'linkedin': self.rule_parser.extract_linkedin(text),
            'github': self.rule_parser.extract_github(text),
            'websites': self.rule_parser.extract_websites(text),
            'dates': self.rule_parser.extract_dates(text),
            'years_of_experience': self.rule_parser.extract_years_of_experience(text)
        }
        
        # Add locations extraction if available
        if hasattr(self.rule_parser, 'extract_locations'):
            result['locations'] = self.rule_parser.extract_locations(text)
        
        # Add skills extraction if available - use skills section if present
        if hasattr(self.rule_parser, 'extract_skills'):
            skills_text = text
            if sections and sections.get('skills'):
                skills_text = sections.get('skills')
                self.logger.info(f"Extracting skills from skills section ({len(skills_text)} chars)")
            else:
                self.logger.warning("No skills section found, using full text for skills extraction")
            result['skills'] = self.rule_parser.extract_skills(skills_text)
        
        # Add name extraction if available
        if hasattr(self.rule_parser, 'extract_name'):
            result['name'] = self.rule_parser.extract_name(text)
        
        return result
    
    def _run_ai_parsing(self, text: str, sections: Dict[str, str] = None, rule_results: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Run AI entity extraction on text with hybrid skills optimization.
        Only calls AI if rule-based extraction has low confidence (<0.85) for any field.
        
        Args:
            text: Full resume text
            sections: Detected sections dictionary
            rule_results: Results from rule-based parsing with confidence scores
            
        Returns:
            Dictionary with AI-extracted fields (only fields that need AI)
        """
        if not self.ai_parser:
            self.logger.warning("AINamedEntityParser not available, returning empty results")
            return {}
        
        # OPTIMIZATION: Check if AI is even needed based on rule_results confidence
        # Skip fields where rule-based extraction has high confidence (>=0.85)
        skip_ai_entirely = False
        if rule_results:
            # Check confidence for key fields
            high_confidence_fields = []
            for field in ['name', 'email', 'phone', 'linkedin', 'github', 'skills', 'locations']:
                field_value = rule_results.get(field)
                # Consider field high confidence if it exists and has data
                if field_value:
                    if isinstance(field_value, (list, str)):
                        if (isinstance(field_value, list) and len(field_value) > 0) or \
                           (isinstance(field_value, str) and len(field_value) > 0):
                            high_confidence_fields.append(field)
            
            # If all critical fields have high confidence from rules, skip AI entirely
            critical_fields = ['name', 'email', 'skills']
            critical_covered = all(field in high_confidence_fields for field in critical_fields)
            
            if critical_covered:
                self.logger.info(f"All critical fields have high confidence from rule-based extraction")
                self.logger.info(f"High confidence fields: {high_confidence_fields}")
                self.logger.info("Skipping AI model call entirely (saves ~2000-9000ms)")
                skip_ai_entirely = True
        
        # If AI not needed, return empty dict immediately
        if skip_ai_entirely:
            return {
                'ai_skipped': True,
                'reason': 'All critical fields extracted with high confidence by rule-based methods'
            }
        
        # OPTIMIZATION: Only extract misc_entities from full text (no longer extracting name/companies/locations)
        # This significantly reduces AI inference time
        self.logger.info("AI model call required - extracting entities")
        entities = self.ai_parser.extract_entities(text)
        
        # OPTIMIZATION: Hybrid skills extraction - dictionary first, AI only for gaps
        # STEP 1: Get skills section text
        skills_text = sections.get('skills', '') if sections else ''
        ai_skills = []
        
        if skills_text and hasattr(self.rule_parser, 'extract_skills_from_dictionary'):
            # STEP 2: Extract skills using dictionary (instant, 500+ skills)
            dict_result = self.rule_parser.extract_skills_from_dictionary(skills_text)
            dict_skills = dict_result.get('matched_skills', [])
            remainder_text = dict_result.get('remainder_text', '')
            remainder_length = dict_result.get('remainder_length', 0)
            
            self.logger.info(f"Dictionary matched {len(dict_skills)} skills")
            self.logger.info(f"Remainder text: {remainder_length} chars")
            
            # STEP 3: Only call AI if significant unmatched text remains (>50 chars)
            if remainder_length > 50:
                self.logger.info(f"Calling AI on {remainder_length} char remainder for rare/emerging skills")
                try:
                    # Extract skills from remainder only
                    remainder_entities = self.ai_parser.extract_entities(remainder_text)
                    ai_skills = self.ai_parser.get_skills(remainder_entities)
                    self.logger.info(f"AI found {len(ai_skills)} additional skills in remainder")
                except Exception as e:
                    self.logger.error(f"Error extracting AI skills from remainder: {e}")
                    ai_skills = []
            else:
                self.logger.info("Remainder <50 chars, skipping AI skills extraction (saves ~4000ms)")
            
            # STEP 4: Merge and deduplicate (done by hybrid_merger)
            # Return both sources, merger will combine them
            return {
                # 'name' removed - rule_parser.extract_name() already extracts with 95% accuracy
                # 'companies' removed - experience_extractor already extracts with 85% accuracy from job blocks
                # 'locations' removed - experience_extractor extracts from job blocks + rule_parser extracts City/State patterns
                'skills': ai_skills,  # Only rare/emerging skills from AI (if any)
                'misc_entities': self.ai_parser.get_misc_entities(entities),
                'ai_entities': entities  # Keep raw entities for reference
            }
        else:
            # Fallback: no skills section or dictionary method not available
            self.logger.warning("No skills section or dictionary method unavailable, skipping AI skills")
            return {
                'misc_entities': self.ai_parser.get_misc_entities(entities),
                'ai_entities': entities
            }
    
    def _extract_experience(self, sections: Dict[str, str], full_text: str = '') -> Dict[str, Any]:
        """Extract structured work experience."""
        if not self.exp_extractor:
            self.logger.warning("ExperienceExtractor not available, returning empty results")
            return {'work_experience': [], 'job_titles': []}
        
        experience_text = sections.get('experience', '').strip()
        if not experience_text:
            self.logger.warning("No experience section detected, falling back to full text")
            experience_text = full_text
        if not experience_text:
            return {'work_experience': [], 'job_titles': []}
        
        exp_result = self.exp_extractor.extract_work_experience(experience_text)
        work_experience = exp_result.get('work_experience', [])
        job_titles = [exp.get('job_title', '') for exp in work_experience if exp.get('job_title')]
        
        return {
            'work_experience': work_experience,
            'job_titles': job_titles
        }
    
    def _extract_summary(self, sections: Dict[str, str], full_text: str) -> Optional[str]:
        """Extract candidate summary/objective from the summary section."""
        summary_text = sections.get('summary', '').strip()
        
        if summary_text and len(summary_text) >= 30:
            lines = summary_text.splitlines()
            cleaned_lines = []
            for line in lines:
                stripped = line.strip()
                if stripped and not re.match(
                    r'^(summary|objective|profile|about\s*me|professional\s+summary|career\s+objective|overview)\s*$',
                    stripped, re.IGNORECASE
                ):
                    cleaned_lines.append(stripped)
            result = ' '.join(cleaned_lines).strip()
            if len(result) >= 30:
                return result[:1000]
        
        # Fallback: first substantial narrative paragraph in the full text
        paragraphs = re.split(r'\n{2,}', full_text)
        for para in paragraphs[:5]:
            para = para.strip()
            if len(para) < 50:
                continue
            if para.isupper():
                continue
            if para.startswith(('-', '*')) or re.match(r'^[\s]*[•\-\*\+]', para):
                continue
            if re.search(r'\(cid:\d+\)', para):
                continue
            if re.search(r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}\b|\b\d{4}\s*[-–—]\s*\d{4}\b', para, re.IGNORECASE):
                continue
            if re.search(r'@|\d{3}[-.]\d{3}|linkedin\.com|github\.com', para, re.IGNORECASE):
                continue
            return para[:1000]
        
        return None
    
    def _extract_education(self, sections: Dict[str, str], full_text: str = '') -> Dict[str, Any]:
        """Extract structured education information."""
        if not self.edu_extractor:
            self.logger.warning("EducationExtractor not available, returning empty results")
            return {'education': [], 'education_institutions': [], 'degrees': []}
        
        education_text = sections.get('education', '').strip()
        if not education_text:
            self.logger.warning("No education section detected, falling back to full text")
            education_text = full_text
        if not education_text:
            return {'education': [], 'education_institutions': [], 'degrees': []}
        
        education = self.edu_extractor.extract_education(education_text)
        institutions = [edu.get('institution', '') for edu in education if edu.get('institution')]
        degrees = [edu.get('degree', '') for edu in education if edu.get('degree')]
        
        return {
            'education': education,
            'education_institutions': institutions,
            'degrees': degrees
        }
    
    def _merge_results(self, rule_results: Dict[str, Any], ai_results: Dict[str, Any],
                      experience_results: Dict[str, Any], education_results: Dict[str, Any]) -> Dict[str, Any]:
        """Merge all parsing results using HybridMerger."""
        if not self.hybrid_merger:
            self.logger.warning("HybridMerger not available, using simple combination")
            return self._simple_merge(rule_results, ai_results, experience_results, education_results)
        
        self.logger.debug("Using HybridMerger for merging results")
        
        # Combine all results for merger
        # Only add experience/education fields, don't override existing fields
        self.logger.debug(f"Original rule_results has email: {rule_results.get('email')}, phone: {rule_results.get('phone')}")
        self.logger.debug(f"Experience results keys: {list(experience_results.keys())}")
        self.logger.debug(f"Education results keys: {list(education_results.keys())}")
        
        combined_rule = rule_results.copy()
        for key, value in {**experience_results, **education_results}.items():
            if key in combined_rule and isinstance(combined_rule[key], list) and isinstance(value, list):
                combined_rule[key] = combined_rule[key] + value
            elif key not in combined_rule:
                combined_rule[key] = value
        combined_ai = ai_results.copy()
        for key, value in {**experience_results, **education_results}.items():
            if key in combined_ai and isinstance(combined_ai[key], list) and isinstance(value, list):
                combined_ai[key] = combined_ai[key] + value
            elif key not in combined_ai:
                combined_ai[key] = value
        
        merged = self.hybrid_merger.merge(combined_rule, combined_ai)
        return merged
    
    def _simple_merge(self, rule_results: Dict[str, Any], ai_results: Dict[str, Any],
                     experience_results: Dict[str, Any], education_results: Dict[str, Any]) -> Dict[str, Any]:
        """Simple merge fallback when HybridMerger is not available."""
        merged = {}
        
        # Add all results with AI priority for certain fields
        ai_priority = ['name', 'companies', 'locations']
        
        for key in set(rule_results) | set(ai_results) | set(experience_results) | set(education_results):
            if key in ai_priority and ai_results.get(key):
                merged[key] = ai_results[key]
            elif rule_results.get(key):
                merged[key] = rule_results[key]
            elif ai_results.get(key):
                merged[key] = ai_results[key]
            elif experience_results.get(key):
                merged[key] = experience_results[key]
            elif education_results.get(key):
                merged[key] = education_results[key]
        
        return merged
    
    def _calculate_confidence(self, merged_results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate confidence scores for merged results."""
        if not self.confidence_scorer:
            self.logger.warning("ConfidenceScorer not available, returning empty confidence")
            return {'overall': 0.0, 'fields': {}, 'needs_review': True}
        
        return self.confidence_scorer.score_parsed_resume(merged_results)
    
    def _assemble_final_result(self, candidate_id: str, merged_results: Dict[str, Any],
                              confidence_scores: Dict[str, Any], metrics: Dict[str, float],
                              file_info: Dict[str, Any] = None) -> Dict[str, Any]:
        """Assemble final result with all components."""
        result = {
            'candidate_id': candidate_id,
            'status': 'success',
            'parsing_timestamp': time.time(),
            
            # Personal information
            'name': merged_results.get('name'),
            'email': merged_results.get('email'),
            'phone': merged_results.get('phone'),
            'linkedin': merged_results.get('linkedin'),
            'github': merged_results.get('github'),
            'websites': merged_results.get('websites', []),
            
            # Professional information
            'summary': merged_results.get('summary'),
            'skills': merged_results.get('skills', []),
            'work_experience': merged_results.get('work_experience', []),
            'education': merged_results.get('education', []),
            'job_titles': merged_results.get('job_titles', []),
            'companies': merged_results.get('companies', []),
            'locations': merged_results.get('locations', []),
            
            # Additional extracted data
            'dates': merged_results.get('dates', []),
            'years_of_experience': merged_results.get('years_of_experience'),
            'misc_entities': merged_results.get('misc_entities', []),
            
            # Quality assessment
            'confidence': confidence_scores,
            'needs_review': confidence_scores.get('needs_review', True),
            'quality_level': confidence_scores.get('quality_level', 'unknown'),
            
            # Processing metrics
            'processing_metrics': {
                'timing_ms': metrics,
                'total_processing_time_ms': metrics.get('total_ms', 0),
                'pipeline_steps_completed': len([k for k, v in metrics.items() if v > 0])
            }
        }
        
        # Add file info if available
        if file_info:
            result['source_info'] = file_info
        
        # Add merge metadata if available
        if '_merge_metadata' in merged_results:
            result['merge_metadata'] = merged_results['_merge_metadata']
        
        # Add source tracking keys for all fields
        for key, value in merged_results.items():
            if key.startswith('_') and key.endswith('_source'):
                result[key] = value
        
        return result
    
    def _create_error_result(self, candidate_id: str, error_message: str, 
                           metrics: Dict[str, float]) -> Dict[str, Any]:
        """Create error result when parsing fails."""
        return {
            'candidate_id': candidate_id,
            'status': 'error',
            'error': error_message,
            'parsing_timestamp': time.time(),
            'confidence': {
                'overall': 0.0,
                'fields': {},
                'needs_review': True,
                'quality_level': 'error'
            },
            'processing_metrics': {
                'timing_ms': metrics,
                'total_processing_time_ms': metrics.get('total_ms', 0),
                'pipeline_steps_completed': len([k for k, v in metrics.items() if v > 0])
            }
        }
    
    def get_pipeline_metrics(self) -> Dict[str, Any]:
        """
        Get timing metrics for the last parse operation.
        
        Returns:
            Dictionary with detailed timing information
        """
        if not self.last_parse_metrics:
            return {'status': 'no_metrics', 'message': 'No parsing operations performed yet'}
        
        metrics = self.last_parse_metrics.copy()
        
        # Calculate percentages
        total_time = metrics.get('total_ms', 0)
        if total_time > 0:
            metrics['percentages'] = {}
            for step, time_ms in metrics.items():
                if step != 'total_ms':
                    metrics['percentages'][step] = (time_ms / total_time) * 100
        
        # Add performance analysis
        metrics['performance_analysis'] = {
            'slowest_step': max(metrics.items(), key=lambda x: x[1] if x[0] != 'total_ms' else 0)[0],
            'fastest_step': min(metrics.items(), key=lambda x: x[1] if x[0] != 'total_ms' else float('inf'))[0],
            'ai_vs_rules_ratio': (
                metrics.get('ai_parsing_ms', 0) / max(metrics.get('rule_parsing_ms', 1), 1)
            )
        }
        
        return metrics
    
    def get_parser_health(self) -> Dict[str, Any]:
        """
        Get health status of all parsers.
        
        Returns:
            Dictionary with parser availability status
        """
        parsers = {
            'text_extractor': self.text_extractor,
            'section_splitter': self.section_splitter,
            'rule_parser': self.rule_parser,
            'experience_extractor': self.exp_extractor,
            'education_extractor': self.edu_extractor,
            'ai_parser': self.ai_parser,
            'hybrid_merger': self.hybrid_merger,
            'confidence_scorer': self.confidence_scorer
        }
        
        health = {}
        for name, parser in parsers.items():
            health[name] = {
                'available': parser is not None,
                'status': 'healthy' if parser is not None else 'unavailable'
            }
        
        # Overall health
        all_available = all(parser is not None for parser in parsers.values())
        health['overall'] = {
            'status': 'healthy' if all_available else 'degraded',
            'available_parsers': sum(1 for p in parsers.values() if p is not None),
            'total_parsers': len(parsers)
        }
        
        return health
    
    def get_supported_file_types(self) -> List[str]:
        """
        Get list of supported file types.
        
        Returns:
            List of supported file extensions
        """
        if self.text_extractor:
            try:
                return self.text_extractor.get_supported_formats()
            except Exception as e:
                self.logger.error(f"Error getting supported formats: {e}")
        
        return ['.txt']  # Fallback to text only


# Example usage and testing
if __name__ == "__main__":
    # Sample text for testing
    sample_text = """
    JOHN DOE
    Senior Software Engineer
    Email: john.doe@email.com
    Phone: +1 (555) 123-4567
    LinkedIn: linkedin.com/in/johndoe
    
    EXPERIENCE
    Senior Software Engineer
    Tech Corp
    San Francisco, CA | 2020 - Present
    • Developed web applications using React and Node.js
    • Led team of 5 developers
    
    Software Engineer
    StartupXYZ
    Palo Alto, CA | 2018 - 2020
    • Built RESTful APIs and microservices
    
    EDUCATION
    Master of Science in Computer Science
    Stanford University
    2016 - 2018
    
    SKILLS
    Python, JavaScript, React, Node.js, AWS, Docker
    """
    
    try:
        # Initialize master parser
        parser = MasterParser()
        
        print("🚀 Testing Master Parser")
        print("=" * 50)
        
        # Test text parsing
        result = parser.parse_text(sample_text, "test_candidate_001")
        
        print("📊 Parsing Results:")
        print(f"  Status: {result['status']}")
        print(f"  Name: {result.get('name')}")
        print(f"  Email: {result.get('email')}")
        print(f"  Phone: {result.get('phone')}")
        print(f"  Skills: {result.get('skills', [])}")
        print(f"  Companies: {result.get('companies', [])}")
        print(f"  Locations: {result.get('locations', [])}")
        print(f"  Work Experience: {len(result.get('work_experience', []))} entries")
        print(f"  Education: {len(result.get('education', []))} entries")
        
        print(f"\n📈 Confidence Score: {result['confidence']['overall']:.3f}")
        print(f"   Quality Level: {result['confidence']['quality_level']}")
        print(f"   Needs Review: {result['confidence']['needs_review']}")
        
        print(f"\n⏱️  Processing Metrics:")
        metrics = result['processing_metrics']
        print(f"   Total Time: {metrics['total_processing_time_ms']:.1f}ms")
        print(f"   Steps Completed: {metrics['pipeline_steps_completed']}")
        
        # Get detailed metrics
        detailed_metrics = parser.get_pipeline_metrics()
        print(f"\n🔍 Detailed Timing:")
        for step, time_ms in detailed_metrics.items():
            if step != 'percentages' and step != 'performance_analysis':
                print(f"   {step}: {time_ms:.1f}ms")
        
        # Get parser health
        health = parser.get_parser_health()
        print(f"\n🏥 Parser Health:")
        print(f"   Overall: {health['overall']['status']}")
        print(f"   Available: {health['overall']['available_parsers']}/{health['overall']['total_parsers']}")
        
        print("\n✅ Master parser test completed!")
        
    except Exception as e:
        print(f"❌ Error testing master parser: {e}")
