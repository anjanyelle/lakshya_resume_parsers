#!/usr/bin/env python3
"""
Integrated NER Pipeline - Combines DeBERTa NER with Production Post-Processing

This module provides a complete end-to-end NER pipeline:
1. Text Pre-processing (cleaning, normalization)
2. DeBERTa NER Model Inference
3. Production-Grade Post-Processing (13-phase pipeline)
4. Structured Output Generation

Usage:
    from parsers.integrated_ner_pipeline import IntegratedNERPipeline
    
    pipeline = IntegratedNERPipeline()
    result = pipeline.extract_entities(resume_text)
    
    # Access structured entities
    companies = result['companies']
    roles = result['roles']
    education = result['education']

Author: AI Engineering Team
Version: 1.0.0
"""

import logging
from typing import Dict, List, Any, Optional
from pathlib import Path

from parsers.ner_postprocessor import NERPostProcessor
from parsers.deberta_ner_parser import DeBERTaNerParser

logger = logging.getLogger(__name__)


class IntegratedNERPipeline:
    """
    Complete NER pipeline integrating DeBERTa model with production post-processing.
    
    Pipeline Flow:
    1. Pre-process text (remove PII, normalize)
    2. Run DeBERTa NER model
    3. Post-process predictions (validate, merge, deduplicate)
    4. Return structured output
    """
    
    def __init__(
        self, 
        model_path: str = None,
        confidence_thresholds: Dict[str, float] = None,
        enable_preprocessing: bool = True
    ):
        """
        Initialize integrated NER pipeline.
        
        Args:
            model_path: Path to DeBERTa model (optional)
            confidence_thresholds: Custom confidence thresholds per entity type
            enable_preprocessing: Whether to apply text preprocessing before NER
        """
        self.logger = logging.getLogger(__name__)
        self.enable_preprocessing = enable_preprocessing
        
        # Initialize DeBERTa NER parser
        try:
            self.ner_parser = DeBERTaNerParser(model_path=model_path)
            self.logger.info("✅ DeBERTa NER parser initialized")
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize DeBERTa parser: {e}")
            self.ner_parser = None
        
        # Initialize post-processor
        self.post_processor = NERPostProcessor(confidence_thresholds=confidence_thresholds)
        self.logger.info("✅ NER post-processor initialized")
    
    def extract_entities(
        self, 
        text: str,
        return_raw: bool = False
    ) -> Dict[str, Any]:
        """
        Extract entities from resume text using complete pipeline.
        
        Args:
            text: Resume text to process
            return_raw: If True, also return raw NER predictions
            
        Returns:
            Dictionary with structured entities:
            {
                'companies': [...],
                'roles': [...],
                'clients': [...],
                'locations': [...],
                'degrees': [...],
                'institutions': [...],
                'fields': [...],
                'date_start': [...],
                'date_end': [...],
                'edu_year_start': [...],
                'edu_year_end': [...],
                'grades': [...],
                'person_names': [...],
                'raw_predictions': [...] (if return_raw=True)
            }
        """
        if not text:
            self.logger.warning("Empty text provided to NER pipeline")
            return self._empty_result()
        
        self.logger.info("=" * 80)
        self.logger.info("INTEGRATED NER PIPELINE - START")
        self.logger.info("=" * 80)
        self.logger.info(f"Input text length: {len(text)} characters")
        
        # STEP 1: Pre-process text
        if self.enable_preprocessing:
            self.logger.info("STEP 1: Pre-processing text...")
            processed_text = NERPostProcessor.preprocess_text(text)
            self.logger.info(f"Pre-processed text length: {len(processed_text)} characters")
        else:
            processed_text = text
            self.logger.info("STEP 1: Skipping pre-processing (disabled)")
        
        # STEP 2: Run DeBERTa NER model
        if not self.ner_parser or not self.ner_parser.is_available():
            self.logger.error("DeBERTa NER parser not available - cannot extract entities")
            return self._empty_result()
        
        self.logger.info("STEP 2: Running DeBERTa NER model...")
        try:
            raw_predictions = self._run_deberta_ner(processed_text)
            self.logger.info(f"DeBERTa extracted {len(raw_predictions)} raw entities")
        except Exception as e:
            self.logger.error(f"DeBERTa NER failed: {e}", exc_info=True)
            return self._empty_result()
        
        # STEP 3: Post-process predictions
        self.logger.info("STEP 3: Post-processing predictions...")
        try:
            structured_entities = self.post_processor.process(
                entities=raw_predictions,
                full_text=processed_text
            )
            self.logger.info("Post-processing complete")
        except Exception as e:
            self.logger.error(f"Post-processing failed: {e}", exc_info=True)
            return self._empty_result()
        
        # STEP 4: Build final result
        result = structured_entities.copy()
        
        if return_raw:
            result['raw_predictions'] = raw_predictions
        
        # Add metadata
        result['metadata'] = {
            'total_raw_entities': len(raw_predictions),
            'total_validated_entities': sum(len(v) for v in structured_entities.values() if isinstance(v, list)),
            'preprocessing_enabled': self.enable_preprocessing,
            'model_available': self.ner_parser.is_available() if self.ner_parser else False
        }
        
        self.logger.info("=" * 80)
        self.logger.info("INTEGRATED NER PIPELINE - COMPLETE")
        self.logger.info("=" * 80)
        
        return result
    
    def _run_deberta_ner(self, text: str) -> List[Dict[str, Any]]:
        """
        Run DeBERTa NER model and convert output to standard format.
        
        Args:
            text: Text to process
            
        Returns:
            List of entity dictionaries with 'entity_group', 'word', 'score'
        """
        # Call DeBERTa parser (use parse_text method)
        parsed_result = self.ner_parser.parse_text(text)
        
        # Log what DeBERTa returned
        self.logger.info(f"DeBERTa parse_text returned: companies={len(parsed_result.get('companies', []))}, roles={len(parsed_result.get('job_titles', []))}, work_exp={len(parsed_result.get('work_experience', []))}")
        
        # Convert DeBERTa output to standard format
        entities = []
        
        if not parsed_result:
            return entities
        
        # DeBERTa returns format like:
        # {
        #   'companies': ['TCS', 'Infosys'],
        #   'job_titles': ['Software Engineer'],
        #   'locations': ['Hyderabad'],
        #   'work_experience': [{...}],
        #   'education': [{...}],
        #   ...
        # }
        
        # Map DeBERTa field names to standard entity types
        field_to_entity_type = {
            'companies': 'COMPANY',
            'job_titles': 'ROLE',
            'clients': 'CLIENT',
            'locations': 'LOCATION',
            'dates': 'DATE_START',
            'degrees': 'DEGREE',
            'institutions': 'INSTITUTION',
            'fields_of_study': 'FIELD',
            'person_names': 'PERSON_NAME'
        }
        
        # Extract simple list fields
        for field_name, entity_type in field_to_entity_type.items():
            if field_name in parsed_result and isinstance(parsed_result[field_name], list):
                for value in parsed_result[field_name]:
                    if isinstance(value, str) and value.strip():
                        entities.append({
                            'entity_group': entity_type,
                            'word': value.strip(),
                            'score': 1.0
                        })
                        self.logger.info(f"Added {entity_type}: {value.strip()}")
        
        # Extract from work_experience structure
        if 'work_experience' in parsed_result and isinstance(parsed_result['work_experience'], list):
            for exp in parsed_result['work_experience']:
                if isinstance(exp, dict):
                    # Extract company (avoid duplicates)
                    company = exp.get('company_name') or exp.get('company')
                    if company and company not in [e['word'] for e in entities if e['entity_group'] == 'COMPANY']:
                        entities.append({
                            'entity_group': 'COMPANY',
                            'word': company,
                            'score': 1.0
                        })
                        self.logger.info(f"Added COMPANY from work_exp: {company}")
                    
                    # Extract role (avoid duplicates)
                    role = exp.get('job_title') or exp.get('role')
                    if role and role not in [e['word'] for e in entities if e['entity_group'] == 'ROLE']:
                        entities.append({
                            'entity_group': 'ROLE',
                            'word': role,
                            'score': 1.0
                        })
                        self.logger.info(f"Added ROLE from work_exp: {role}")
                    
                    # Extract client (avoid duplicates)
                    client = exp.get('client')
                    if client and client not in [e['word'] for e in entities if e['entity_group'] == 'CLIENT']:
                        entities.append({
                            'entity_group': 'CLIENT',
                            'word': client,
                            'score': 1.0
                        })
                        self.logger.info(f"Added CLIENT from work_exp: {client}")
                    
                    # Extract location
                    location = exp.get('location')
                    if location:
                        entities.append({
                            'entity_group': 'LOCATION',
                            'word': location,
                            'score': 1.0
                        })
                    
                    # Extract dates
                    start_date = exp.get('start_date')
                    if start_date:
                        entities.append({
                            'entity_group': 'DATE_START',
                            'word': start_date,
                            'score': 1.0
                        })
                    
                    end_date = exp.get('end_date')
                    if end_date:
                        entities.append({
                            'entity_group': 'DATE_END',
                            'word': end_date,
                            'score': 1.0
                        })
        
        # Extract from education structure
        if 'education' in parsed_result and isinstance(parsed_result['education'], list):
            for edu in parsed_result['education']:
                if isinstance(edu, dict):
                    # Extract degree
                    degree = edu.get('degree') or edu.get('degree_name')
                    if degree:
                        entities.append({
                            'entity_group': 'DEGREE',
                            'word': degree,
                            'score': 1.0
                        })
                    
                    # Extract institution
                    institution = edu.get('institution') or edu.get('institution_name')
                    if institution:
                        entities.append({
                            'entity_group': 'INSTITUTION',
                            'word': institution,
                            'score': 1.0
                        })
                    
                    # Extract field
                    field = edu.get('field_of_study') or edu.get('field')
                    if field:
                        entities.append({
                            'entity_group': 'FIELD',
                            'word': field,
                            'score': 1.0
                        })
                    
                    # Extract years
                    start_year = edu.get('start_year')
                    if start_year:
                        entities.append({
                            'entity_group': 'EDU_YEAR_START',
                            'word': str(start_year),
                            'score': 1.0
                        })
                    
                    end_year = edu.get('end_year')
                    if end_year:
                        entities.append({
                            'entity_group': 'EDU_YEAR_END',
                            'word': str(end_year),
                            'score': 1.0
                        })
                    
                    # Extract grade
                    grade = edu.get('gpa') or edu.get('grade')
                    if grade:
                        entities.append({
                            'entity_group': 'GRADE',
                            'word': str(grade),
                            'score': 1.0
                        })
        
        self.logger.info(f"Total entities extracted from DeBERTa: {len(entities)}")
        return entities
    
    def _empty_result(self) -> Dict[str, Any]:
        """Return empty result structure."""
        return {
            'companies': [],
            'roles': [],
            'clients': [],
            'locations': [],
            'degrees': [],
            'institutions': [],
            'fields': [],
            'date_start': [],
            'date_end': [],
            'edu_year_start': [],
            'edu_year_end': [],
            'grades': [],
            'person_names': [],
            'metadata': {
                'total_raw_entities': 0,
                'total_validated_entities': 0,
                'preprocessing_enabled': self.enable_preprocessing,
                'model_available': False
            }
        }
    
    def extract_work_experience(self, text: str) -> Dict[str, Any]:
        """
        Extract work experience entities specifically.
        
        Returns only ROLE, COMPANY, CLIENT, LOCATION, DATE_START, DATE_END.
        
        Args:
            text: Resume text
            
        Returns:
            Dictionary with work experience entities
        """
        all_entities = self.extract_entities(text)
        
        return {
            'roles': all_entities.get('roles', []),
            'companies': all_entities.get('companies', []),
            'clients': all_entities.get('clients', []),
            'locations': all_entities.get('locations', []),
            'date_start': all_entities.get('date_start', []),
            'date_end': all_entities.get('date_end', [])
        }
    
    def extract_education(self, text: str) -> Dict[str, Any]:
        """
        Extract education entities specifically.
        
        Returns only DEGREE, INSTITUTION, FIELD, EDU_YEAR_START, EDU_YEAR_END, GRADE.
        
        Args:
            text: Resume text
            
        Returns:
            Dictionary with education entities
        """
        all_entities = self.extract_entities(text)
        
        return {
            'degrees': all_entities.get('degrees', []),
            'institutions': all_entities.get('institutions', []),
            'fields': all_entities.get('fields', []),
            'edu_year_start': all_entities.get('edu_year_start', []),
            'edu_year_end': all_entities.get('edu_year_end', []),
            'grades': all_entities.get('grades', [])
        }
    
    def is_available(self) -> bool:
        """
        Check if the NER pipeline is available and ready to use.
        
        Returns:
            True if pipeline is ready, False otherwise
        """
        return (
            self.ner_parser is not None and 
            self.ner_parser.is_available() and 
            self.post_processor is not None
        )


# ═══════════════════════════════════════════════════════════════════════════
# USAGE EXAMPLES
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Example 1: Basic usage
    print("\n" + "=" * 80)
    print("EXAMPLE 1: Basic Entity Extraction")
    print("=" * 80)
    
    sample_resume = """
    John Doe
    john.doe@email.com | +1-555-123-4567
    linkedin.com/in/johndoe
    
    PROFESSIONAL SUMMARY
    Senior Full Stack Developer with 8+ years of experience in building scalable web applications.
    
    WORK EXPERIENCE
    
    Senior Full Stack Developer
    TechMahindra Pvt Ltd | Hyderabad, Telangana
    January 2020 - Present
    
    • Led team of 5 developers on cloud infrastructure project
    • Developed REST APIs using Node.js and Express
    • Worked with business analysts and stakeholders
    
    Software Engineer
    Infosys Limited | Bangalore
    June 2017 - December 2019
    
    • Implemented microservices architecture
    • Performed integration test cases and unit testing
    • Collaborated with teams across multiple locations
    
    EDUCATION
    
    Bachelor of Technology in Computer Science and Engineering
    JNTU Hyderabad | 2013 - 2017
    GPA: 3.8/4.0
    
    SKILLS
    React, Node.js, Python, AWS, Docker, Kubernetes
    """
    
    pipeline = IntegratedNERPipeline()
    
    if pipeline.is_available():
        result = pipeline.extract_entities(sample_resume)
        
        print("\nExtracted Entities:")
        print(f"Companies: {result['companies']}")
        print(f"Roles: {result['roles']}")
        print(f"Locations: {result['locations']}")
        print(f"Institutions: {result['institutions']}")
        print(f"Degrees: {result['degrees']}")
        print(f"Fields: {result['fields']}")
        
        print("\nMetadata:")
        print(f"Total raw entities: {result['metadata']['total_raw_entities']}")
        print(f"Total validated entities: {result['metadata']['total_validated_entities']}")
    else:
        print("❌ NER pipeline not available (DeBERTa model not loaded)")
    
    # Example 2: Work experience extraction only
    print("\n" + "=" * 80)
    print("EXAMPLE 2: Work Experience Extraction")
    print("=" * 80)
    
    if pipeline.is_available():
        work_exp = pipeline.extract_work_experience(sample_resume)
        
        print("\nWork Experience Entities:")
        for key, values in work_exp.items():
            if values:
                print(f"{key}: {values}")
    
    # Example 3: Education extraction only
    print("\n" + "=" * 80)
    print("EXAMPLE 3: Education Extraction")
    print("=" * 80)
    
    if pipeline.is_available():
        education = pipeline.extract_education(sample_resume)
        
        print("\nEducation Entities:")
        for key, values in education.items():
            if values:
                print(f"{key}: {values}")
    
    # Example 4: Custom confidence thresholds
    print("\n" + "=" * 80)
    print("EXAMPLE 4: Custom Confidence Thresholds")
    print("=" * 80)
    
    custom_thresholds = {
        'ROLE': 0.95,  # Higher threshold for roles
        'COMPANY': 0.85,  # Lower threshold for companies
    }
    
    strict_pipeline = IntegratedNERPipeline(confidence_thresholds=custom_thresholds)
    
    if strict_pipeline.is_available():
        result = strict_pipeline.extract_entities(sample_resume)
        print(f"\nWith strict thresholds - Roles: {result['roles']}")
        print(f"With strict thresholds - Companies: {result['companies']}")
