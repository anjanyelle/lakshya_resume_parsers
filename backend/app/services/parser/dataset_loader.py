"""
Dataset Loader Utility for Dynamic Loading and Caching
Provides efficient loading and management of external datasets
"""

import os
import csv
import json
import pickle
import hashlib
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class DatasetLoader:
    """
    Utility class for loading and caching external datasets
    with automatic refresh and validation capabilities
    """
    
    def __init__(self, cache_dir: Optional[str] = None, cache_ttl_hours: int = 24):
        self.cache_dir = cache_dir or self._get_default_cache_dir()
        self.cache_ttl = timedelta(hours=cache_ttl_hours)
        self._ensure_cache_dir()
        
        # Dataset file configurations
        self.dataset_configs = {
            'companies': {
                'files': [
                    'data/external/companies/fortune500_companies/csv/fortune500-2019.csv',
                    'data/external/companies/startups_companies.csv',
                    'data/external/companies/consulting_companies.csv',
                    'data/external/companies/healthcare_companies.csv'
                ],
                'required_columns': {
                    'fortune500': ['company', 'rank', 'revenue ($ millions)', 'profit ($ millions)'],
                    'startups': ['company', 'normalized_company', 'industry', 'funding_stage', 'employee_count', 'headquarters'],
                    'consulting': ['company', 'normalized_company', 'industry', 'specialization', 'employee_count', 'headquarters'],
                    'healthcare': ['company', 'normalized_company', 'industry', 'specialization', 'employee_count', 'headquarters']
                }
            },
            'job_titles': {
                'files': ['data/external/job_titles.csv'],
                'required_columns': ['raw_title', 'normalized_title', 'category']
            },
            'skills': {
                'files': ['data/external/skills.csv'],
                'required_columns': ['skill_name', 'category', 'subcategory', 'level']
            },
            'education': {
                'files': ['data/external/education.csv'],
                'required_columns': ['institution', 'normalized_institution', 'type', 'country', 'state', 'city']
            },
            'locations': {
                'files': ['data/external/locations.csv'],
                'required_columns': ['city', 'state', 'country', 'country_code', 'latitude', 'longitude']
            }
        }
    
    def _get_default_cache_dir(self) -> str:
        """Get default cache directory"""
        base_dir = os.path.dirname(__file__)
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(base_dir))))
        cache_dir = os.path.join(project_root, 'data', 'cache')
        return cache_dir
    
    def _ensure_cache_dir(self):
        """Ensure cache directory exists"""
        os.makedirs(self.cache_dir, exist_ok=True)
    
    def _get_project_root(self) -> str:
        """Get the project root directory"""
        base_dir = os.path.dirname(__file__)
        return os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(base_dir))))
    
    def _get_cache_key(self, dataset_type: str, file_paths: List[str]) -> str:
        """Generate cache key based on dataset type and file modification times"""
        project_root = self._get_project_root()
        key_data = f"{dataset_type}_"
        
        for file_path in file_paths:
            full_path = os.path.join(project_root, file_path)
            if os.path.exists(full_path):
                mtime = os.path.getmtime(full_path)
                key_data += f"{file_path}_{mtime}_"
        
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _get_cache_path(self, cache_key: str) -> str:
        """Get cache file path"""
        return os.path.join(self.cache_dir, f"{cache_key}.pkl")
    
    def _is_cache_valid(self, cache_path: str) -> bool:
        """Check if cache file is still valid"""
        if not os.path.exists(cache_path):
            return False
        
        cache_time = datetime.fromtimestamp(os.path.getmtime(cache_path))
        return datetime.now() - cache_time < self.cache_ttl
    
    def _load_from_cache(self, cache_path: str) -> Optional[Dict]:
        """Load data from cache file"""
        try:
            with open(cache_path, 'rb') as f:
                return pickle.load(f)
        except Exception as e:
            logger.warning(f"Failed to load cache from {cache_path}: {e}")
            return None
    
    def _save_to_cache(self, cache_path: str, data: Dict):
        """Save data to cache file"""
        try:
            with open(cache_path, 'wb') as f:
                pickle.dump(data, f)
        except Exception as e:
            logger.warning(f"Failed to save cache to {cache_path}: {e}")
    
    def _validate_csv_file(self, file_path: str, required_columns: List[str]) -> bool:
        """Validate CSV file has required columns"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                available_columns = reader.fieldnames or []
                missing_columns = set(required_columns) - set(available_columns)
                
                if missing_columns:
                    logger.error(f"Missing required columns in {file_path}: {missing_columns}")
                    return False
                
                return True
        except Exception as e:
            logger.error(f"Error validating CSV file {file_path}: {e}")
            return False
    
    def _load_csv_file(self, file_path: str, dataset_type: str) -> List[Dict]:
        """Load data from CSV file"""
        data = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row_num, row in enumerate(reader, 1):
                    try:
                        # Clean row data
                        cleaned_row = {}
                        for key, value in row.items():
                            if value is not None:
                                cleaned_row[key.strip()] = value.strip()
                            else:
                                cleaned_row[key.strip()] = ''
                        
                        data.append(cleaned_row)
                    except Exception as e:
                        logger.warning(f"Error processing row {row_num} in {file_path}: {e}")
                        continue
            
            logger.info(f"Loaded {len(data)} rows from {file_path}")
            return data
            
        except Exception as e:
            logger.error(f"Error loading CSV file {file_path}: {e}")
            return []
    
    def load_dataset(self, dataset_type: str, use_cache: bool = True) -> Dict:
        """
        Load dataset with caching support
        
        Args:
            dataset_type: Type of dataset to load
            use_cache: Whether to use cached data if available
            
        Returns:
            Dictionary containing loaded dataset
        """
        if dataset_type not in self.dataset_configs:
            raise ValueError(f"Unknown dataset type: {dataset_type}")
        
        config = self.dataset_configs[dataset_type]
        file_paths = config['files']
        
        # Check cache first
        if use_cache:
            cache_key = self._get_cache_key(dataset_type, file_paths)
            cache_path = self._get_cache_path(cache_key)
            
            if self._is_cache_valid(cache_path):
                cached_data = self._load_from_cache(cache_path)
                if cached_data:
                    logger.info(f"Loaded {dataset_type} dataset from cache")
                    return cached_data
        
        # Load from files
        project_root = self._get_project_root()
        dataset_data = {}
        
        for file_path in file_paths:
            full_path = os.path.join(project_root, file_path)
            
            if not os.path.exists(full_path):
                logger.warning(f"Dataset file not found: {full_path}")
                continue
            
            # Validate file
            file_type = os.path.basename(os.path.dirname(file_path)).split('_')[0]
            required_columns_config = config.get('required_columns', {})
            
            if isinstance(required_columns_config, dict):
                if file_type in required_columns_config:
                    required_columns = required_columns_config[file_type]
                else:
                    required_columns = required_columns_config.get('default', [])
            elif isinstance(required_columns_config, list):
                required_columns = required_columns_config
            else:
                required_columns = []
            
            if not self._validate_csv_file(full_path, required_columns):
                continue
            
            # Load data
            raw_data = self._load_csv_file(full_path, dataset_type)
            
            # Process data based on dataset type
            if dataset_type == 'companies':
                processed_data = self._process_companies_data(raw_data, file_type)
            elif dataset_type == 'job_titles':
                processed_data = self._process_job_titles_data(raw_data)
            elif dataset_type == 'skills':
                processed_data = self._process_skills_data(raw_data)
            elif dataset_type == 'education':
                processed_data = self._process_education_data(raw_data)
            elif dataset_type == 'locations':
                processed_data = self._process_locations_data(raw_data)
            else:
                processed_data = raw_data
            
            dataset_data.update(processed_data)
        
        # Save to cache
        if use_cache and dataset_data:
            cache_key = self._get_cache_key(dataset_type, file_paths)
            cache_path = self._get_cache_path(cache_key)
            self._save_to_cache(cache_path, dataset_data)
        
        logger.info(f"Loaded {dataset_type} dataset: {len(dataset_data)} entries")
        return dataset_data
    
    def _process_companies_data(self, raw_data: List[Dict], file_type: str) -> Dict:
        """Process companies data based on file type"""
        processed = {}
        
        for row in raw_data:
            if file_type == 'fortune500':
                company_name = row['company'].strip().lower()
                processed[company_name] = {
                    'name': row['company'].strip(),
                    'type': 'fortune500',
                    'rank': int(row['rank']),
                    'revenue': float(row['revenue ($ millions)'] or 0),
                    'profit': float(row['profit ($ millions)'] or 0)
                }
            else:  # startups, consulting, healthcare
                company_name = row.get('company', row.get('normalized_company', '')).strip().lower()
                if company_name:
                    processed[company_name] = {
                        'name': row.get('company', row.get('normalized_company', '')).strip(),
                        'type': file_type,
                        'normalized_company': row.get('normalized_company', '').strip(),
                        'industry': row.get('industry', '').strip(),
                        'specialization': row.get('specialization', '').strip(),
                        'employee_count': row.get('employee_count', '').strip(),
                        'headquarters': row.get('headquarters', '').strip(),
                        'funding_stage': row.get('funding_stage', '').strip()
                    }
        
        return processed
    
    def _process_job_titles_data(self, raw_data: List[Dict]) -> Dict:
        """Process job titles data"""
        processed = {}
        
        for row in raw_data:
            title_key = row['raw_title'].strip().lower()
            processed[title_key] = {
                'normalized': row['normalized_title'].strip(),
                'category': row['category'].strip()
            }
        
        return processed
    
    def _process_skills_data(self, raw_data: List[Dict]) -> Dict:
        """Process skills data"""
        processed = {}
        
        for row in raw_data:
            skill_key = row['skill_name'].strip().lower()
            processed[skill_key] = {
                'category': row['category'].strip(),
                'subcategory': row['subcategory'].strip(),
                'level': row['level'].strip()
            }
        
        return processed
    
    def _process_education_data(self, raw_data: List[Dict]) -> Dict:
        """Process education data"""
        processed = {}
        
        for row in raw_data:
            institution_key = row['institution'].strip().lower()
            processed[institution_key] = {
                'name': row['institution'].strip(),
                'normalized': row['normalized_institution'].strip(),
                'type': row['type'].strip(),
                'country': row['country'].strip(),
                'state': row['state'].strip(),
                'city': row['city'].strip(),
                'ranking': row.get('ranking', '').strip()
            }
        
        return processed
    
    def _process_locations_data(self, raw_data: List[Dict]) -> Dict:
        """Process locations data"""
        processed = {}
        
        for row in raw_data:
            # Create both city,state and city only entries
            city_state = f"{row['city'].strip()}, {row['state'].strip()}"
            city_only = row['city'].strip()
            
            location_data = {
                'city': row['city'].strip(),
                'state': row['state'].strip(),
                'country': row['country'].strip(),
                'country_code': row['country_code'].strip(),
                'latitude': float(row['latitude']),
                'longitude': float(row['longitude'])
            }
            
            processed[city_state.lower()] = location_data
            processed[city_only.lower()] = location_data
        
        return processed
    
    def refresh_cache(self, dataset_type: Optional[str] = None):
        """Refresh cache for specific dataset or all datasets"""
        if dataset_type:
            cache_keys = [self._get_cache_key(dataset_type, self.dataset_configs[dataset_type]['files'])]
        else:
            cache_keys = []
            for dt in self.dataset_configs:
                cache_keys.append(self._get_cache_key(dt, self.dataset_configs[dt]['files']))
        
        for cache_key in cache_keys:
            cache_path = self._get_cache_path(cache_key)
            if os.path.exists(cache_path):
                try:
                    os.remove(cache_path)
                    logger.info(f"Removed cache file: {cache_path}")
                except Exception as e:
                    logger.warning(f"Failed to remove cache file {cache_path}: {e}")
    
    def get_cache_info(self) -> Dict:
        """Get information about cached datasets"""
        cache_info = {}
        
        for cache_file in os.listdir(self.cache_dir):
            if cache_file.endswith('.pkl'):
                cache_path = os.path.join(self.cache_dir, cache_file)
                cache_time = datetime.fromtimestamp(os.path.getmtime(cache_path))
                cache_size = os.path.getsize(cache_path)
                is_valid = self._is_cache_valid(cache_path)
                
                cache_info[cache_file] = {
                    'path': cache_path,
                    'created': cache_time,
                    'size_bytes': cache_size,
                    'is_valid': is_valid,
                    'expires_at': cache_time + self.cache_ttl
                }
        
        return cache_info
    
    def validate_datasets(self) -> Dict:
        """Validate all dataset files"""
        validation_results = {}
        project_root = self._get_project_root()
        
        for dataset_type, config in self.dataset_configs.items():
            validation_results[dataset_type] = {
                'valid': True,
                'errors': [],
                'warnings': [],
                'file_count': 0,
                'total_records': 0
            }
            
            for file_path in config['files']:
                full_path = os.path.join(project_root, file_path)
                
                if not os.path.exists(full_path):
                    validation_results[dataset_type]['errors'].append(f"File not found: {file_path}")
                    validation_results[dataset_type]['valid'] = False
                    continue
                
                # Determine required columns for this file
                file_type = os.path.basename(os.path.dirname(file_path)).split('_')[0]
                required_columns_config = config.get('required_columns', {})
                
                if isinstance(required_columns_config, dict):
                    if file_type in required_columns_config:
                        required_columns = required_columns_config[file_type]
                    else:
                        required_columns = required_columns_config.get('default', [])
                elif isinstance(required_columns_config, list):
                    required_columns = required_columns_config
                else:
                    required_columns = []
                    
                if not self._validate_csv_file(full_path, required_columns):
                    validation_results[dataset_type]['valid'] = False
                
                validation_results[dataset_type]['file_count'] += 1
                
                # Count records
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        reader = csv.DictReader(f)
                        record_count = sum(1 for _ in reader)
                        validation_results[dataset_type]['total_records'] += record_count
                except Exception as e:
                    validation_results[dataset_type]['errors'].append(f"Error counting records in {file_path}: {e}")
                    validation_results[dataset_type]['valid'] = False
        
        return validation_results
