"""
Unified Dataset Loader - Merges ALL Datasets Simultaneously
Combines existing + external datasets into unified structures
"""

import os
import csv
import json
import pickle
import hashlib
from typing import Dict, List, Any, Optional, Set
from datetime import datetime, timedelta
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class UnifiedDatasetLoader:
    """
    Unified dataset loader that merges ALL datasets (existing + external)
    into single unified structures without priority-based selection.
    
    All datasets are actively used together for maximum coverage.
    """
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._initialize()
    
    def _initialize(self):
        """Initialize the unified dataset loader"""
        self.cache_ttl = timedelta(hours=24)
        self.unified_datasets = {}
        self.dataset_sources = {}  # Track which source contributed each entry
        
        # Define ALL dataset configurations for unified merging
        self.dataset_configs = {
            # Companies - Merge ALL company datasets
            'companies': {
                'all_files': [
                    # External datasets (correct relative paths from backend)
                    '../data/external/clients.csv',
                    '../data/external/company_normalization.csv',
                ],
                'merge_columns': ['company', 'raw_name', 'normalized_company', 'normalized_name'],
                'unified_columns': ['name', 'normalized_name', 'industry', 'category'],
                'deduplication_keys': ['name', 'normalized_name']
            },
            
            # Job Titles - Merge ALL job title datasets
            'job_titles': {
                'all_files': [
                    # External datasets (correct relative paths from backend)
                    '../data/external/job_titles.csv',
                    '../data/external/job-title_normalization.csv',
                ],
                'merge_columns': ['raw_title', 'normalized_title', 'title', 'category'],
                'unified_columns': ['title', 'normalized_title', 'category', 'seniority'],
                'deduplication_keys': ['title', 'normalized_title']
            },
            
            # Skills - Merge ALL skill datasets
            'skills': {
                'all_files': [
                    # External datasets (correct relative paths from backend)
                    '../data/external/skills.csv',
                    '../data/external/enhanced_skills.csv',
                ],
                'merge_columns': ['skill_name', 'name', 'skill', 'category', 'subcategory'],
                'unified_columns': ['name', 'category', 'subcategory', 'proficiency_level'],
                'deduplication_keys': ['name', 'skill_name']
            },
            
            # Education - Merge ALL education datasets
            'education': {
                'all_files': [
                    # External datasets (correct relative paths from backend)
                    '../data/external/education.csv',
                    '../data/external/education2.csv',
                    '../data/external/degree_normalization.csv',
                ],
                'merge_columns': ['institution', 'normalized_institution', 'school', 'degree', 'type'],
                'unified_columns': ['institution', 'normalized_institution', 'type', 'degree_level'],
                'deduplication_keys': ['institution', 'normalized_institution']
            },
            
            # Locations - Merge ALL location datasets
            'locations': {
                'all_files': [
                    # External datasets (correct relative paths from backend)
                    '../data/external/locations.csv',
                    '../data/external/location_datset.csv',
                ],
                'merge_columns': ['city', 'state', 'country', 'location', 'region'],
                'unified_columns': ['city', 'state', 'country', 'region', 'normalized_location'],
                'deduplication_keys': ['city', 'location']
            },
            
            # Certifications - Merge ALL certification datasets
            'certifications': {
                'all_files': [
                    # External datasets (correct relative paths from backend)
                    '../data/external/certifications.csv',
                ],
                'merge_columns': ['name', 'certification', 'issuer', 'issuing_organization'],
                'unified_columns': ['name', 'issuer', 'category', 'level'],
                'deduplication_keys': ['name', 'certification']
            },
            
            # Patterns - External patterns (new enhancement)
            'patterns': {
                'all_files': [
                    # External datasets (correct relative paths from backend)
                    '../data/external/pattern_dataset.csv'
                ],
                'merge_columns': ['pattern_type', 'pattern'],
                'unified_columns': ['type', 'pattern', 'category'],
                'deduplication_keys': ['pattern']
            },
            
            # Date Patterns - External date patterns
            'date_patterns': {
                'all_files': [
                    # External datasets (correct relative paths from backend)
                    '../data/external/date_patterns.csv'
                ],
                'merge_columns': ['raw_date', 'normalized_date'],
                'unified_columns': ['raw_date', 'normalized_date'],
                'deduplication_keys': ['raw_date']
            },
            
            # Skill Synonyms - External skill synonyms
            'skill_synonyms': {
                'all_files': [
                    # External datasets (correct relative paths from backend)
                    '../data/external/skill_synonyms.csv'
                ],
                'merge_columns': ['skill', 'synonym'],
                'unified_columns': ['skill', 'synonym'],
                'deduplication_keys': ['skill']
            },
            
            # NER - External NER entities (new enhancement)
            'ner': {
                'all_files': [
                    # External datasets (correct relative paths from backend)
                    '../data/external/ner_datset.csv'
                ],
                'merge_columns': ['text', 'label', 'entity', 'type'],
                'unified_columns': ['text', 'label', 'category'],
                'deduplication_keys': ['text', 'label']
            }
        }
        
        # Load and merge ALL datasets
        self._load_and_merge_all_datasets()
        UnifiedDatasetLoader._initialized = True
        logger.info("Unified Dataset Loader initialized successfully")
    
    def _get_project_root(self) -> str:
        """Get project root directory"""
        current_dir = Path(__file__).parent
        project_root = current_dir.parent.parent.parent
        return str(project_root)
    
    def _resolve_file_path(self, file_path: str) -> str:
        """Resolve relative file path to absolute path"""
        # For our use case, handle relative paths from backend
        if file_path.startswith('../'):
            # Already relative from backend, use as-is
            return file_path.lstrip('/')
        elif file_path.startswith('data/'):
            # Relative from project root, resolve it
            project_root = self._get_project_root()
            return os.path.join(project_root, file_path.lstrip('/'))
        else:
            # Absolute path, return as-is
            return file_path.lstrip('/')
    
    def _load_csv_file(self, file_path: str, dataset_type: str) -> List[Dict]:
        """Load CSV file with error handling and validation"""
        try:
            resolved_path = self._resolve_file_path(file_path)
            if not os.path.exists(resolved_path):
                logger.debug(f"File not found: {file_path}")
                return []
            
            with open(resolved_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                data = []
                for row_num, row in enumerate(reader, 1):
                    if row:  # Skip empty rows
                        # Add source file information
                        row['_source_file'] = file_path
                        row['_source_type'] = 'existing' if 'trained' in file_path else 'external'
                        data.append(row)
                
                logger.debug(f"Loaded {len(data)} rows from {file_path}")
                return data
                
        except Exception as e:
            logger.warning(f"Error loading {file_path}: {e}")
            return []
    
    def _normalize_value(self, value: str) -> str:
        """Normalize value for comparison and deduplication"""
        if not value:
            return ""
        return str(value).lower().strip()
    
    def _merge_all_dataset_entries(self, all_data: List[Dict], dataset_type: str, 
                                   config: Dict) -> tuple[List[Dict], Dict]:
        """
        Merge ALL dataset entries into unified structure
        No priority - all datasets contribute equally
        """
        unified = {}
        source_tracker = {}
        
        # Get deduplication keys from config
        dedup_keys = config.get('deduplication_keys', ['name'])
        unified_columns = config.get('unified_columns', [])
        
        for entry in all_data:
            if not isinstance(entry, dict):
                continue
            
            # Create deduplication key(s)
            key_parts = []
            for key in dedup_keys:
                value = entry.get(key, '')
                if value:
                    key_parts.append(self._normalize_value(value))
            
            if not key_parts:
                continue
            
            # Use first key as primary, others as secondary
            primary_key = key_parts[0]
            secondary_keys = key_parts[1:]
            
            # Create unified entry
            unified_entry = {}
            
            # Map all possible columns to unified structure
            for unified_col in unified_columns:
                # Try to find value from any of the merge columns
                value = None
                for merge_col in config.get('merge_columns', []):
                    if entry.get(merge_col):
                        value = entry.get(merge_col)
                        break
                
                if value:
                    unified_entry[unified_col] = str(value).strip()
            
            # Add metadata
            unified_entry['_all_sources'] = []
            unified_entry['_source_files'] = []
            
            # Handle merging with existing entry
            if primary_key in unified:
                existing = unified[primary_key]
                
                # Merge data intelligently - combine information from all sources
                for col in unified_columns:
                    existing_val = existing.get(col, '')
                    new_val = unified_entry.get(col, '')
                    
                    # Use longer, more descriptive value
                    if new_val and len(new_val) > len(existing_val):
                        existing[col] = new_val
                    elif new_val and not existing_val:
                        existing[col] = new_val
                
                # Combine source information
                if '_all_sources' not in existing:
                    existing['_all_sources'] = []
                if '_source_files' not in existing:
                    existing['_source_files'] = []
                
                source_type = entry.get('_source_type', 'unknown')
                source_file = entry.get('_source_file', '')
                
                if source_type not in existing['_all_sources']:
                    existing['_all_sources'].append(source_type)
                if source_file not in existing['_source_files']:
                    existing['_source_files'].append(source_file)
                
                source_tracker[primary_key] = existing['_all_sources']
                
            else:
                # New entry
                unified_entry['_all_sources'] = [entry.get('_source_type', 'unknown')]
                unified_entry['_source_files'] = [entry.get('_source_file', 'unknown')]
                unified[primary_key] = unified_entry
                source_tracker[primary_key] = unified_entry['_all_sources']
        
        return list(unified.values()), source_tracker
    
    def _load_and_merge_all_datasets(self):
        """Load and merge ALL datasets into unified structures"""
        logger.info("Loading and merging ALL datasets...")
        
        for dataset_type, config in self.dataset_configs.items():
            logger.info(f"Processing unified dataset: {dataset_type}")
            
            # Load ALL files for this dataset type
            all_data = []
            for file_path in config['all_files']:
                data = self._load_csv_file(file_path, dataset_type)
                all_data.extend(data)
            
            if all_data:
                # Merge ALL entries without priority
                unified_data, source_tracker = self._merge_all_dataset_entries(
                    all_data, dataset_type, config
                )
                
                self.unified_datasets[dataset_type] = unified_data
                self.dataset_sources[dataset_type] = source_tracker
                
                # Log merging statistics
                source_counts = {}
                for sources in source_tracker.values():
                    for source in sources:
                        source_counts[source] = source_counts.get(source, 0) + 1
                
                logger.info(f"Unified {dataset_type}: {len(all_data)} total entries → {len(unified_data)} unique entries")
                logger.info(f"Sources: {source_counts}")
            else:
                logger.warning(f"No data found for unified dataset: {dataset_type}")
                self.unified_datasets[dataset_type] = []
                self.dataset_sources[dataset_type] = {}
    
    def get_unified_dataset(self, dataset_type: str) -> List[Dict]:
        """Get unified dataset for specified type"""
        return self.unified_datasets.get(dataset_type, [])
    
    def get_source_info(self, dataset_type: str) -> Dict[str, List[str]]:
        """Get source information for unified dataset entries"""
        return self.dataset_sources.get(dataset_type, {})
    
    def lookup_in_unified_dataset(self, dataset_type: str, search_value: str, 
                                 search_fields: List[str] = None) -> Optional[Dict]:
        """
        Lookup value in unified dataset across ALL search fields
        Returns first match from any source
        """
        if not search_value or not search_value.strip():
            return None
        
        normalized_search = self._normalize_value(search_value)
        unified_data = self.get_unified_dataset(dataset_type)
        
        if not search_fields:
            # Use default search fields based on dataset type
            search_fields = {
                'companies': ['name', 'normalized_name'],
                'job_titles': ['title', 'normalized_title'],
                'skills': ['name', 'skill_name'],
                'education': ['institution', 'normalized_institution'],
                'locations': ['city', 'location', 'normalized_location'],
                'certifications': ['name', 'certification']
            }.get(dataset_type, ['name'])
        
        for entry in unified_data:
            if not isinstance(entry, dict):
                continue
            
            # Search across all specified fields
            for field in search_fields:
                field_value = entry.get(field, '')
                if field_value and self._normalize_value(field_value) == normalized_search:
                    sources = entry.get('_all_sources', ['unknown'])
                    logger.debug(f"Found '{search_value}' in {dataset_type} from sources: {sources}")
                    return entry
        
        return None
    
    def lookup_company(self, company_name: str) -> Optional[Dict]:
        """Lookup company in unified dataset"""
        return self.lookup_in_unified_dataset('companies', company_name, 
                                           ['name', 'normalized_name'])
    
    def lookup_job_title(self, job_title: str) -> Optional[Dict]:
        """Lookup job title in unified dataset"""
        return self.lookup_in_unified_dataset('job_titles', job_title,
                                           ['title', 'normalized_title'])
    
    def lookup_skill(self, skill_name: str) -> Optional[Dict]:
        """Lookup skill in unified dataset"""
        return self.lookup_in_unified_dataset('skills', skill_name,
                                           ['name', 'skill_name'])
    
    def lookup_education(self, institution: str) -> Optional[Dict]:
        """Lookup education institution in unified dataset"""
        return self.lookup_in_unified_dataset('education', institution,
                                           ['institution', 'normalized_institution'])
    
    def lookup_location(self, location: str) -> Optional[Dict]:
        """Lookup location in unified dataset"""
        return self.lookup_in_unified_dataset('locations', location,
                                           ['city', 'location', 'normalized_location'])
    
    def lookup_certification(self, cert_name: str) -> Optional[Dict]:
        """Lookup certification in unified dataset"""
        return self.lookup_in_unified_dataset('certifications', cert_name,
                                           ['name', 'certification'])
    
    def get_patterns(self, pattern_type: str = None) -> List[str]:
        """Get all patterns from unified dataset"""
        patterns = self.get_unified_dataset('patterns')
        if pattern_type:
            return [p['pattern'] for p in patterns if p.get('type') == pattern_type]
        return [p['pattern'] for p in patterns]
    
    def get_ner_entities(self) -> Dict[str, List[str]]:
        """Get all NER entities from unified dataset"""
        ner_data = self.get_unified_dataset('ner')
        entities = {}
        for entry in ner_data:
            label = entry.get('label', '') or entry.get('type', '')
            text = entry.get('text', '') or entry.get('entity', '')
            if label and text:
                if label not in entities:
                    entities[label] = []
                if text not in entities[label]:  # Avoid duplicates
                    entities[label].append(text)
        return entities
    
    def normalize_with_unified_dataset(self, dataset_type: str, value: str) -> str:
        """
        Normalize value using unified dataset
        Returns best match from any source
        """
        if not value or not value.strip():
            return value
        
        lookup = self.lookup_in_unified_dataset(dataset_type, value)
        if lookup:
            # Return normalized value if available
            normalized_fields = {
                'companies': 'normalized_name',
                'job_titles': 'normalized_title',
                'skills': 'name',
                'education': 'normalized_institution',
                'locations': 'normalized_location',
                'certifications': 'name'
            }
            
            norm_field = normalized_fields.get(dataset_type, 'name')
            if lookup.get(norm_field):
                return lookup[norm_field]
        
        return value
    
    def normalize_company_name(self, company_name: str) -> str:
        """Normalize company name using unified dataset"""
        return self.normalize_with_unified_dataset('companies', company_name)
    
    def normalize_job_title(self, job_title: str) -> str:
        """Normalize job title using unified dataset"""
        return self.normalize_with_unified_dataset('job_titles', job_title)
    
    def normalize_skill(self, skill_name: str) -> str:
        """Normalize skill using unified dataset"""
        return self.normalize_with_unified_dataset('skills', skill_name)
    
    def normalize_education(self, institution: str) -> str:
        """Normalize education institution using unified dataset"""
        return self.normalize_with_unified_dataset('education', institution)
    
    def normalize_location(self, location: str) -> str:
        """Normalize location using unified dataset"""
        return self.normalize_with_unified_dataset('locations', location)
    
    def get_unified_dataset_stats(self) -> Dict[str, Any]:
        """Get comprehensive statistics about unified datasets"""
        stats = {}
        for dataset_type, data in self.unified_datasets.items():
            sources = self.get_source_info(dataset_type)
            
            # Count source types
            source_type_counts = {}
            source_file_counts = {}
            for entry_sources in sources.values():
                for source in entry_sources:
                    source_type_counts[source] = source_type_counts.get(source, 0) + 1
            
            # Count unique files
            all_files = set()
            for entry in data:
                files = entry.get('_source_files', [])
                all_files.update(files)
            
            stats[dataset_type] = {
                'total_unique_entries': len(data),
                'source_type_counts': source_type_counts,
                'unique_source_files': len(all_files),
                'all_source_files': list(all_files)
            }
        
        return stats

# Global instance for unified access
unified_loader = UnifiedDatasetLoader()
