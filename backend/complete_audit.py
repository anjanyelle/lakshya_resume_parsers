#!/usr/bin/env python3
"""
COMPLETE HONEST AUDIT OF RESUME PARSER PROJECT
"""

import os
import json
import pickle
import pandas as pd
from pathlib import Path

def scan_project_structure():
    """AUDIT 1 — SCAN ENTIRE PROJECT STRUCTURE"""
    
    print("=" * 80)
    print("AUDIT 1 — SCAN ENTIRE PROJECT STRUCTURE")
    print("=" * 80)
    
    project_root = Path("c:/Users/Rajes/OneDrive/Desktop/Lakshya_Resume_paser_NEW!/Lakshya-LLM-Resume-Parser")
    
    structure = {}
    
    # Scan all directories and files
    for root, dirs, files in os.walk(project_root):
        root_path = Path(root)
        relative_path = root_path.relative_to(project_root)
        
        for file in files:
            file_path = root_path / file
            relative_file_path = relative_path / file
            
            # Get file info
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = len(f.readlines())
            except:
                lines = 0
            
            file_size = file_path.stat().st_size if file_path.exists() else 0
            
            # Determine purpose based on file path and name
            purpose = determine_file_purpose(str(relative_file_path))
            
            structure[str(relative_file_path)] = {
                'path': str(relative_file_path),
                'purpose': purpose,
                'status': determine_file_status(str(relative_file_path)),
                'size': file_size,
                'lines': lines
            }
    
    # Print structure organized by folder
    folders = {}
    for file_path, info in structure.items():
        folder = str(Path(file_path).parent)
        if folder not in folders:
            folders[folder] = []
        folders[folder].append((file_path, info))
    
    for folder in sorted(folders.keys()):
        print(f"\n{folder}/")
        for file_path, info in sorted(folders[folder]):
            print(f"  ├── {Path(file_path).name}")
            print(f"  │   FILE    : {info['path']}")
            print(f"  │   PURPOSE : {info['purpose']}")
            print(f"  │   STATUS  : {info['status']}")
            print(f"  │   SIZE    : {info['lines']} lines ({info['size']} bytes)")
            print(f"  │")
    
    return structure

def determine_file_purpose(file_path):
    """Determine file purpose based on path and name"""
    path_lower = file_path.lower()
    
    if 'parser' in path_lower and any(ext in path_lower for ext in ['.py']):
        return "Resume section/entity parser"
    elif 'extractor' in path_lower:
        return "Data extraction utility"
    elif 'pipeline' in path_lower:
        return "Main parsing pipeline orchestrator"
    elif 'model' in path_lower or '.pkl' in path_lower:
        return "Trained ML model"
    elif 'training' in path_lower or 'train' in path_lower:
        return "Model training script"
    elif '.csv' in path_lower:
        return "Training/reference dataset"
    elif 'json' in path_lower and 'data' in path_lower:
        return "Training data examples"
    elif 'api' in path_lower:
        return "REST API endpoint"
    elif 'endpoint' in path_lower:
        return "API route handler"
    elif 'upload' in path_lower:
        return "File upload handler"
    elif 'database' in path_lower or 'db' in path_lower:
        return "Database model/schema"
    elif 'utils' in path_lower:
        return "Utility functions"
    elif 'config' in path_lower:
        return "Configuration file"
    elif 'test' in path_lower:
        return "Test suite"
    elif 'frontend' in path_lower:
        return "Frontend component"
    elif 'component' in path_lower:
        return "UI component"
    elif 'requirements' in path_lower:
        return "Python dependencies"
    elif 'readme' in path_lower:
        return "Project documentation"
    elif 'license' in path_lower:
        return "License information"
    elif 'docker' in path_lower:
        return "Docker configuration"
    elif '.md' in path_lower:
        return "Documentation"
    elif '.yml' in path_lower or '.yaml' in path_lower:
        return "YAML configuration"
    else:
        return "General purpose file"

def determine_file_status(file_path):
    """Determine if file is actually used"""
    path_lower = file_path.lower()
    
    # Files that are definitely used
    if any(x in path_lower for x in [
        'backend/app/api/v1/endpoints/upload.py',
        'backend/app/workers/pipeline.py',
        'backend/app/services/parser/section_parser.py',
        'backend/app/services/parser/work_experience_parser.py',
        'backend/app/services/parser/education_parser.py',
        'backend/app/services/parser/certification_parser.py',
        'backend/app/services/parser/skill_extractor.py'
    ]):
        return "USED"
    
    # Training data files
    if any(x in path_lower for x in [
        'data/external/skills.csv',
        'data/external/job_titles.csv',
        'data/external/education.csv',
        'data/external/companies.csv'
    ]):
        return "PARTIALLY USED"
    
    # Model files
    if '.pkl' in path_lower:
        return "PARTIALLY USED"
    
    # spaCy models
    if 'spacy' in path_lower or 'ner_model' in path_lower:
        return "PARTIALLY USED"
    
    # Documentation and config
    if any(x in path_lower for x in ['.md', 'readme', 'license', 'requirements', '.yml', '.yaml', 'docker']):
        return "USED"
    
    # Test files
    if 'test' in path_lower:
        return "PARTIALLY USED"
    
    # Frontend files
    if 'frontend' in path_lower:
        return "USED"
    
    return "NOT USED"

def check_training_datasets():
    """AUDIT 2 — CHECK ALL TRAINING DATA AND DATASETS"""
    
    print("\n" + "=" * 80)
    print("AUDIT 2 — CHECK ALL TRAINING DATA AND DATASETS")
    print("=" * 80)
    
    project_root = Path("c:/Users/Rajes/OneDrive/Desktop/Lakshya_Resume_paser_NEW!/Lakshya-LLM-Resume-Parser")
    
    csv_files = []
    pkl_files = []
    spacy_models = []
    json_training_files = []
    
    # Find all relevant files
    for root, dirs, files in os.walk(project_root):
        for file in files:
            file_path = Path(root) / file
            relative_path = file_path.relative_to(project_root)
            
            if file.endswith('.csv'):
                csv_files.append(file_path)
            elif file.endswith('.pkl'):
                pkl_files.append(file_path)
            elif any(x in str(relative_path).lower() for x in ['spacy', 'ner_model']):
                spacy_models.append(file_path)
            elif 'training_data' in str(relative_path).lower() and file.endswith('.json'):
                json_training_files.append(file_path)
    
    print("\nCSV FILES FOUND:")
    for csv_file in csv_files:
        relative_path = csv_file.relative_to(project_root)
        print(f"\n  FILE NAME         : {csv_file.name}")
        print(f"  LOCATION          : {relative_path}")
        
        try:
            df = pd.read_csv(csv_file)
            print(f"  ROWS COUNT        : {len(df)}")
            print(f"  COLUMNS           : {list(df.columns)}")
        except Exception as e:
            print(f"  ERROR READING     : {e}")
            print(f"  ROWS COUNT        : UNKNOWN")
            print(f"  COLUMNS           : UNKNOWN")
        
        # Check if loaded in code
        loaded_in_code = check_if_csv_loaded(str(relative_path))
        print(f"  LOADED IN CODE    : {loaded_in_code['loaded']}")
        if loaded_in_code['loaded']:
            print(f"    → which file loads it: {loaded_in_code['file']}")
            print(f"    → which function: {loaded_in_code['function']}")
        else:
            print(f"    → it is SITTING IDLE — not being used")
        
        used_for_training = check_if_used_for_training(str(relative_path))
        print(f"  USED FOR TRAINING : {used_for_training['used']}")
        if used_for_training['used']:
            print(f"    → which model: {used_for_training['model']}")
        else:
            print(f"    → training never happens from this file")
        
        used_in_parser = check_if_used_in_parser(str(relative_path))
        print(f"  USED IN PARSER    : {used_in_parser['used']}")
        if used_in_parser['used']:
            print(f"    → how does parser use it: {used_in_parser['method']}")
        else:
            print(f"    → parser ignores this file completely")
    
    print("\nPKL FILES FOUND:")
    for pkl_file in pkl_files:
        relative_path = pkl_file.relative_to(project_root)
        file_size = pkl_file.stat().st_size / 1024  # KB
        print(f"\n  FILE NAME         : {pkl_file.name}")
        print(f"  LOCATION          : {relative_path}")
        print(f"  FILE SIZE         : {file_size:.2f} KB")
        
        # Try to determine what it contains
        try:
            with open(pkl_file, 'rb') as f:
                content = pickle.load(f)
                content_type = type(content).__name__
                if hasattr(content, '__len__'):
                    content_info = f"{content_type} ({len(content)} items)"
                else:
                    content_info = content_type
                print(f"  WHAT IT CONTAINS  : {content_info}")
        except Exception as e:
            print(f"  WHAT IT CONTAINS  : Cannot read - {e}")
        
        loaded_in_code = check_if_pkl_loaded(str(relative_path))
        print(f"  LOADED IN CODE    : {loaded_in_code['loaded']}")
        if loaded_in_code['loaded']:
            print(f"    → which file loads it: {loaded_in_code['file']}")
            print(f"    → which function: {loaded_in_code['function']}")
        else:
            print(f"    → model is SAVED but NEVER LOADED — wasted")
        
        used_in_pipeline = check_if_used_in_pipeline(str(relative_path))
        print(f"  USED IN PIPELINE  : {used_in_pipeline['used']}")
        if used_in_pipeline['used']:
            print(f"    → at which step: {used_in_pipeline['step']}")
        else:
            print(f"    → model exists but parser never calls it")
    
    return {
        'csv_files': csv_files,
        'pkl_files': pkl_files,
        'spacy_models': spacy_models,
        'json_training_files': json_training_files
    }

def check_if_csv_loaded(csv_path):
    """Check if CSV is loaded in code"""
    csv_name = Path(csv_path).name.lower()
    
    # Search for CSV loading patterns in code
    project_root = Path("c:/Users/Rajes/OneDrive/Desktop/Lakshya_Resume_paser_NEW!/Lakshya-LLM-Resume-Parser")
    
    for root, dirs, files in os.walk(project_root):
        for file in files:
            if file.endswith('.py'):
                file_path = Path(root) / file
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        if csv_name in content.lower() and 'pd.read_csv' in content:
                            lines = content.split('\n')
                            for i, line in enumerate(lines, 1):
                                if csv_name in line.lower() and 'pd.read_csv' in line:
                                    return {
                                        'loaded': True,
                                        'file': str(file_path.relative_to(project_root)),
                                        'function': f"line {i}"
                                    }
                except:
                    pass
    
    return {'loaded': False}

def check_if_used_for_training(csv_path):
    """Check if CSV is used for training"""
    csv_name = Path(csv_path).name.lower()
    
    project_root = Path("c:/Users/Rajes/OneDrive/Desktop/Lakshya_Resume_paser_NEW!/Lakshya-LLM-Resume-Parser")
    
    for root, dirs, files in os.walk(project_root):
        for file in files:
            if 'train' in file.lower() and file.endswith('.py'):
                file_path = Path(root) / file
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        if csv_name in content.lower():
                            return {
                                'used': True,
                                'model': str(file_path.relative_to(project_root))
                            }
                except:
                    pass
    
    return {'used': False}

def check_if_used_in_parser(csv_path):
    """Check if CSV is used in parser"""
    csv_name = Path(csv_path).name.lower()
    
    project_root = Path("c:/Users/Rajes/OneDrive/Desktop/Lakshya_Resume_paser_NEW!/Lakshya-LLM-Resume-Parser")
    
    parser_files = [
        'work_experience_parser.py',
        'education_parser.py', 
        'certification_parser.py',
        'skill_extractor.py'
    ]
    
    for parser_file in parser_files:
        parser_path = project_root / 'backend/app/services/parser' / parser_file
        if parser_path.exists():
            try:
                with open(parser_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    if csv_name in content.lower():
                        return {
                            'used': True,
                            'method': f'Referenced in {parser_file}'
                        }
            except:
                pass
    
    return {'used': False}

def check_if_pkl_loaded(pkl_path):
    """Check if PKL file is loaded in code"""
    pkl_name = Path(pkl_path).name.lower()
    
    project_root = Path("c:/Users/Rajes/OneDrive/Desktop/Lakshya_Resume_paser_NEW!/Lakshya-LLM-Resume-Parser")
    
    for root, dirs, files in os.walk(project_root):
        for file in files:
            if file.endswith('.py'):
                file_path = Path(root) / file
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        if pkl_name in content.lower() and 'pickle.load' in content:
                            lines = content.split('\n')
                            for i, line in enumerate(lines, 1):
                                if pkl_name in line.lower() and 'pickle.load' in line:
                                    return {
                                        'loaded': True,
                                        'file': str(file_path.relative_to(project_root)),
                                        'function': f"line {i}"
                                    }
                except:
                    pass
    
    return {'loaded': False}

def check_if_used_in_pipeline(pkl_path):
    """Check if PKL is used in pipeline"""
    pkl_name = Path(pkl_path).name.lower()
    
    pipeline_path = Path("c:/Users/Rajes/OneDrive/Desktop/Lakshya_Resume_paser_NEW!/Lakshya-LLM-Resume-Parser/backend/app/workers/pipeline.py")
    
    if pipeline_path.exists():
        try:
            with open(pipeline_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                if pkl_name in content.lower():
                    lines = content.split('\n')
                    for i, line in enumerate(lines, 1):
                        if pkl_name in line.lower():
                            return {
                                'used': True,
                                'step': f"pipeline.py line {i}"
                            }
        except:
            pass
    
    return {'used': False}

if __name__ == "__main__":
    structure = scan_project_structure()
    datasets = check_training_datasets()
    
    print(f"\n" + "=" * 80)
    print("PROJECT STRUCTURE SUMMARY:")
    print("=" * 80)
    print(f"Total files scanned: {len(structure)}")
    
    used_files = sum(1 for info in structure.values() if info['status'] == 'USED')
    not_used_files = sum(1 for info in structure.values() if info['status'] == 'NOT USED')
    partially_used_files = sum(1 for info in structure.values() if info['status'] == 'PARTIALLY USED')
    
    print(f"Files actively used: {used_files}")
    print(f"Files partially used: {partially_used_files}")
    print(f"Files not used: {not_used_files}")
    
    print(f"\nCSV files found: {len(datasets['csv_files'])}")
    print(f"PKL files found: {len(datasets['pkl_files'])}")
    print(f"SpaCy models found: {len(datasets['spacy_models'])}")
    print(f"Training JSON files: {len(datasets['json_training_files'])}")
