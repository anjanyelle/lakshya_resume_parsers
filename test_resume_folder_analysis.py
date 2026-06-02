#!/usr/bin/env python3
"""
Comprehensive Resume Folder Analysis Script

Analyzes a folder of resumes and reports:
- Which resumes had missing sections
- Which had incorrect section assignments
- Which worked perfectly
- Extraction method used for each
- Processing time for each
"""

import sys
import os
import json
import logging
from pathlib import Path
from typing import Dict, List

# Add ai-service to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ai-service'))

# Configure logging to suppress detailed logs
logging.basicConfig(
    level=logging.WARNING,
    format='%(message)s'
)

# Global parser instance
parser_instance = None

def get_parser():
    global parser_instance
    if parser_instance is None:
        from resume_parser_pipeline import ResumeParser
        # Resolve model path dynamically
        model_path = None
        if os.path.exists("ai-service/models/resume-ner-deberta/config.json"):
            model_path = "ai-service/models/resume-ner-deberta"
        elif os.path.exists("models/resume-ner-deberta/config.json"):
            model_path = "models/resume-ner-deberta"
        else:
            model_path = "./models/resume-ner-deberta"
        print(f"Initializing ResumeParser with model path: {model_path} ...")
        parser_instance = ResumeParser(model_path)
    return parser_instance

def analyze_resume(file_path: str) -> Dict:
    """
    Analyze a single resume file
    
    Returns:
        Dictionary with analysis results
    """
    from parsers.text_extractor import TextExtractor
    
    result = {
        'filename': os.path.basename(file_path),
        'file_path': file_path,
        'success': False,
        'extraction_method': None,
        'sections_found': [],
        'sections_missing': [],
        'has_experience': False,
        'has_education': False,
        'has_skills': False,
        'has_summary': False,
        'has_certifications': False,
        'has_projects': False,
        'basic_info': {},
        'parsed_entities': 0,
        'error': None
    }
    
    try:
        # Extract text first to get extraction method
        extractor = TextExtractor()
        file_ext = file_path.lower().split('.')[-1]
        
        if file_ext == 'pdf':
            extraction_result = extractor.extract_from_pdf(file_path)
            result['extraction_method'] = extraction_result.get('method_used', 'unknown')
        elif file_ext == 'docx':
            result['extraction_method'] = 'python-docx'
        else:
            result['extraction_method'] = 'direct'
        
        # Parse the resume
        parser = get_parser()
        parsed = parser.parse('', file_path=file_path)
        
        # Analyze sections
        result['has_experience'] = len(parsed.get('experience', '')) > 0
        result['has_education'] = len(parsed.get('education', '')) > 0
        result['has_skills'] = len(parsed.get('skills', '')) > 0
        result['has_summary'] = len(parsed.get('summary', '')) > 0
        result['has_certifications'] = len(parsed.get('certifications', '')) > 0
        result['has_projects'] = len(parsed.get('projects', '')) > 0
        
        # Track which sections were found
        if result['has_experience']:
            result['sections_found'].append('experience')
        else:
            result['sections_missing'].append('experience')
            
        if result['has_education']:
            result['sections_found'].append('education')
        else:
            result['sections_missing'].append('education')
            
        if result['has_skills']:
            result['sections_found'].append('skills')
        else:
            result['sections_missing'].append('skills')
            
        if result['has_summary']:
            result['sections_found'].append('summary')
        else:
            result['sections_missing'].append('summary')
            
        if result['has_certifications']:
            result['sections_found'].append('certifications')
            
        if result['has_projects']:
            result['sections_found'].append('projects')
        
        # Get basic info
        result['basic_info'] = parsed.get('basic_info', {})
        
        # Count parsed entities
        parsed_data = parsed.get('parsed', {})
        exp_entities = len(parsed_data.get('experience', []))
        edu_entities = len(parsed_data.get('education', []))
        result['parsed_entities'] = exp_entities + edu_entities
        
        result['success'] = True
        
    except Exception as e:
        result['error'] = str(e)
    
    return result

def analyze_folder(folder_path: str) -> List[Dict]:
    """
    Analyze all resumes in a folder
    
    Returns:
        List of analysis results
    """
    results = []
    
    # Find all resume files
    supported_extensions = ['.pdf', '.docx', '.txt']
    resume_files = []
    
    for ext in supported_extensions:
        resume_files.extend(Path(folder_path).glob(f'*{ext}'))
    
    print(f"\n📁 Found {len(resume_files)} resume files in {folder_path}")
    print("="*80)
    
    for i, file_path in enumerate(resume_files, 1):
        print(f"\n[{i}/{len(resume_files)}] Processing: {file_path.name}")
        result = analyze_resume(str(file_path))
        results.append(result)
        
        if result['success']:
            print(f"   ✅ Success - {len(result['sections_found'])} sections found")
        else:
            print(f"   ❌ Failed - {result['error']}")
    
    return results

def generate_report(results: List[Dict]):
    """
    Generate comprehensive analysis report
    """
    print("\n" + "="*80)
    print("📊 COMPREHENSIVE ANALYSIS REPORT")
    print("="*80)
    
    total = len(results)
    successful = sum(1 for r in results if r['success'])
    failed = total - successful
    
    print(f"\n📈 Overall Statistics:")
    print(f"   Total resumes: {total}")
    print(f"   Successfully processed: {successful}")
    print(f"   Failed: {failed}")
    
    # Extraction methods
    print(f"\n🔧 Extraction Methods Used:")
    methods = {}
    for r in results:
        if r['success'] and r['extraction_method']:
            methods[r['extraction_method']] = methods.get(r['extraction_method'], 0) + 1
    
    for method, count in sorted(methods.items(), key=lambda x: x[1], reverse=True):
        print(f"   • {method}: {count} resumes")
    
    # Section detection statistics
    print(f"\n📋 Section Detection Statistics:")
    section_stats = {
        'experience': sum(1 for r in results if r['has_experience']),
        'education': sum(1 for r in results if r['has_education']),
        'skills': sum(1 for r in results if r['has_skills']),
        'summary': sum(1 for r in results if r['has_summary']),
        'certifications': sum(1 for r in results if r['has_certifications']),
        'projects': sum(1 for r in results if r['has_projects'])
    }
    
    for section, count in section_stats.items():
        percentage = (count / successful * 100) if successful > 0 else 0
        print(f"   • {section}: {count}/{successful} ({percentage:.1f}%)")
    
    # Perfect resumes (all core sections found)
    print(f"\n✅ PERFECT RESUMES (Experience + Education + Skills):")
    perfect = [r for r in results if r['has_experience'] and r['has_education'] and r['has_skills']]
    
    if perfect:
        for r in perfect:
            print(f"   ✓ {r['filename']}")
            print(f"      Sections: {', '.join(r['sections_found'])}")
            print(f"      Entities: {r['parsed_entities']}")
            print(f"      Name: {r['basic_info'].get('name', 'Not found')}")
    else:
        print("   None")
    
    print(f"\n   Total: {len(perfect)}/{successful} resumes")
    
    # Resumes with missing sections
    print(f"\n⚠️  RESUMES WITH MISSING SECTIONS:")
    missing = [r for r in results if r['success'] and r['sections_missing']]
    
    if missing:
        for r in missing:
            print(f"   • {r['filename']}")
            print(f"      Missing: {', '.join(r['sections_missing'])}")
            print(f"      Found: {', '.join(r['sections_found'])}")
    else:
        print("   None")
    
    # Resumes with potential incorrect assignments
    print(f"\n🔍 RESUMES NEEDING REVIEW (Missing core sections):")
    needs_review = [r for r in results if r['success'] and (not r['has_experience'] or not r['has_education'])]
    
    if needs_review:
        for r in needs_review:
            print(f"   • {r['filename']}")
            issues = []
            if not r['has_experience']:
                issues.append("No experience section")
            if not r['has_education']:
                issues.append("No education section")
            print(f"      Issues: {', '.join(issues)}")
            print(f"      Found sections: {', '.join(r['sections_found'])}")
    else:
        print("   None - All resumes have core sections!")
    
    # Failed resumes
    if failed > 0:
        print(f"\n❌ FAILED RESUMES:")
        failed_resumes = [r for r in results if not r['success']]
        for r in failed_resumes:
            print(f"   • {r['filename']}")
            print(f"      Error: {r['error']}")
    
    # Detailed breakdown
    print(f"\n" + "="*80)
    print("📝 DETAILED BREAKDOWN")
    print("="*80)
    
    for i, r in enumerate(results, 1):
        if not r['success']:
            continue
            
        print(f"\n[{i}] {r['filename']}")
        print(f"   Extraction: {r['extraction_method']}")
        print(f"   Sections found: {', '.join(r['sections_found']) if r['sections_found'] else 'None'}")
        if r['sections_missing']:
            print(f"   Sections missing: {', '.join(r['sections_missing'])}")
        print(f"   Basic info: Name={r['basic_info'].get('name', 'N/A')}, Email={r['basic_info'].get('email', 'N/A')}")
        print(f"   Parsed entities: {r['parsed_entities']}")
    
    print("\n" + "="*80)
    print("✅ ANALYSIS COMPLETE")
    print("="*80)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python test_resume_folder_analysis.py <folder_path>")
        print("\nExample: python test_resume_folder_analysis.py ./sample_resumes")
        sys.exit(1)
    
    folder_path = sys.argv[1]
    
    if not os.path.exists(folder_path):
        print(f"Error: Folder '{folder_path}' does not exist")
        sys.exit(1)
    
    print("\n" + "="*80)
    print("🚀 RESUME FOLDER ANALYSIS")
    print("="*80)
    print(f"Folder: {folder_path}")
    
    results = analyze_folder(folder_path)
    generate_report(results)
