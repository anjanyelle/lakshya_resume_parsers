#!/usr/bin/env python3
"""
Test DeBERTa model on all resumes in resumetestmodel directory
Calculate accuracy metrics for entity extraction
"""

import sys
import os
from pathlib import Path
from typing import Dict, List, Any
import logging

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from parsers.deberta_ner_parser import DeBERTaNerParser

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s:%(name)s:%(message)s'
)

logger = logging.getLogger(__name__)


def test_single_resume(file_path: str, parser: DeBERTaNerParser) -> Dict[str, Any]:
    """Test DeBERTa model on a single resume file."""
    
    # Read resume text
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            resume_text = f.read()
    except Exception as e:
        return {
            'file': os.path.basename(file_path),
            'error': str(e),
            'success': False
        }
    
    # Parse with DeBERTa
    try:
        result = parser.parse_text(resume_text)
        
        return {
            'file': os.path.basename(file_path),
            'success': True,
            'text_length': len(resume_text),
            'companies': result.get('companies', []),
            'job_titles': result.get('job_titles', []),
            'locations': result.get('locations', []),
            'dates': result.get('dates', []),
            'work_experience': result.get('work_experience', []),
            'education': result.get('education', []),
            'degrees': result.get('degrees', []),
            'institutions': result.get('institutions', []),
            'clients': result.get('clients', []),
            'num_companies': len(result.get('companies', [])),
            'num_roles': len(result.get('job_titles', [])),
            'num_work_exp': len(result.get('work_experience', [])),
            'num_education': len(result.get('education', [])),
            'num_degrees': len(result.get('degrees', [])),
            'num_institutions': len(result.get('institutions', [])),
        }
    except Exception as e:
        logger.error(f"Error parsing {os.path.basename(file_path)}: {e}")
        return {
            'file': os.path.basename(file_path),
            'error': str(e),
            'success': False
        }


def calculate_metrics(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate accuracy metrics from test results."""
    
    successful = [r for r in results if r.get('success', False)]
    failed = [r for r in results if not r.get('success', False)]
    
    total_companies = sum(r['num_companies'] for r in successful)
    total_roles = sum(r['num_roles'] for r in successful)
    total_work_exp = sum(r['num_work_exp'] for r in successful)
    total_education = sum(r['num_education'] for r in successful)
    total_degrees = sum(r['num_degrees'] for r in successful)
    total_institutions = sum(r['num_institutions'] for r in successful)
    
    # Count resumes with at least one extraction
    resumes_with_companies = sum(1 for r in successful if r['num_companies'] > 0)
    resumes_with_roles = sum(1 for r in successful if r['num_roles'] > 0)
    resumes_with_work_exp = sum(1 for r in successful if r['num_work_exp'] > 0)
    resumes_with_education = sum(1 for r in successful if r['num_education'] > 0)
    
    return {
        'total_resumes': len(results),
        'successful': len(successful),
        'failed': len(failed),
        'total_companies': total_companies,
        'total_roles': total_roles,
        'total_work_exp': total_work_exp,
        'total_education': total_education,
        'total_degrees': total_degrees,
        'total_institutions': total_institutions,
        'avg_companies_per_resume': total_companies / len(successful) if successful else 0,
        'avg_roles_per_resume': total_roles / len(successful) if successful else 0,
        'avg_work_exp_per_resume': total_work_exp / len(successful) if successful else 0,
        'avg_education_per_resume': total_education / len(successful) if successful else 0,
        'resumes_with_companies': resumes_with_companies,
        'resumes_with_roles': resumes_with_roles,
        'resumes_with_work_exp': resumes_with_work_exp,
        'resumes_with_education': resumes_with_education,
        'company_extraction_rate': (resumes_with_companies / len(successful) * 100) if successful else 0,
        'role_extraction_rate': (resumes_with_roles / len(successful) * 100) if successful else 0,
        'work_exp_extraction_rate': (resumes_with_work_exp / len(successful) * 100) if successful else 0,
        'education_extraction_rate': (resumes_with_education / len(successful) * 100) if successful else 0,
    }


def main():
    """Test all resumes in textfiletestmodel directory."""
    
    # Get textfiletestmodel directory
    base_dir = Path(__file__).parent.parent
    resume_dir = base_dir / "textfiletestmodel"
    
    if not resume_dir.exists():
        print(f"❌ Directory not found: {resume_dir}")
        return
    
    # Get all .txt files
    resume_files = sorted(resume_dir.glob("*.txt"))
    
    if not resume_files:
        print(f"❌ No .txt files found in {resume_dir}")
        return
    
    print("=" * 100)
    print("🧪 DEBERTA MODEL ACCURACY TESTING")
    print("=" * 100)
    print(f"📁 Directory: {resume_dir}")
    print(f"📄 Total resumes: {len(resume_files)}")
    print("=" * 100)
    
    # Initialize DeBERTa parser
    print("\n🤖 Initializing DeBERTa NER parser...")
    parser = DeBERTaNerParser()
    print("✅ Parser initialized\n")
    
    # Test each resume
    results = []
    for i, resume_file in enumerate(resume_files, 1):
        print(f"\r⏳ Processing: {i}/{len(resume_files)} - {resume_file.name}", end="", flush=True)
        result = test_single_resume(str(resume_file), parser)
        results.append(result)
    
    print("\n\n" + "=" * 100)
    print("📊 DETAILED RESULTS")
    print("=" * 100)
    
    # Display individual results
    successful_results = [r for r in results if r.get('success', False)]
    
    print(f"\n{'File':<30} {'Companies':<12} {'Roles':<12} {'Work Exp':<12} {'Education':<12} {'Degrees':<12}")
    print("-" * 100)
    
    for result in successful_results:
        print(f"{result['file']:<30} "
              f"{result['num_companies']:<12} "
              f"{result['num_roles']:<12} "
              f"{result['num_work_exp']:<12} "
              f"{result['num_education']:<12} "
              f"{result['num_degrees']:<12}")
    
    # Show failed resumes
    failed_results = [r for r in results if not r.get('success', False)]
    if failed_results:
        print("\n" + "=" * 100)
        print("❌ FAILED RESUMES")
        print("=" * 100)
        for result in failed_results:
            print(f"  {result['file']}: {result.get('error', 'Unknown error')}")
    
    # Calculate and display metrics
    print("\n" + "=" * 100)
    print("📈 ACCURACY METRICS")
    print("=" * 100)
    
    metrics = calculate_metrics(results)
    
    print(f"\n📊 Processing Summary:")
    print(f"  Total Resumes: {metrics['total_resumes']}")
    print(f"  Successful: {metrics['successful']} ({metrics['successful']/metrics['total_resumes']*100:.1f}%)")
    print(f"  Failed: {metrics['failed']}")
    
    print(f"\n🏢 Company Extraction:")
    print(f"  Total Companies: {metrics['total_companies']}")
    print(f"  Avg per Resume: {metrics['avg_companies_per_resume']:.2f}")
    print(f"  Extraction Rate: {metrics['company_extraction_rate']:.1f}% ({metrics['resumes_with_companies']}/{metrics['successful']} resumes)")
    
    print(f"\n💼 Role Extraction:")
    print(f"  Total Roles: {metrics['total_roles']}")
    print(f"  Avg per Resume: {metrics['avg_roles_per_resume']:.2f}")
    print(f"  Extraction Rate: {metrics['role_extraction_rate']:.1f}% ({metrics['resumes_with_roles']}/{metrics['successful']} resumes)")
    
    print(f"\n📋 Work Experience:")
    print(f"  Total Entries: {metrics['total_work_exp']}")
    print(f"  Avg per Resume: {metrics['avg_work_exp_per_resume']:.2f}")
    print(f"  Extraction Rate: {metrics['work_exp_extraction_rate']:.1f}% ({metrics['resumes_with_work_exp']}/{metrics['successful']} resumes)")
    
    print(f"\n🎓 Education Extraction:")
    print(f"  Total Entries: {metrics['total_education']}")
    print(f"  Total Degrees: {metrics['total_degrees']}")
    print(f"  Total Institutions: {metrics['total_institutions']}")
    print(f"  Avg per Resume: {metrics['avg_education_per_resume']:.2f}")
    print(f"  Extraction Rate: {metrics['education_extraction_rate']:.1f}% ({metrics['resumes_with_education']}/{metrics['successful']} resumes)")
    
    # Overall score
    print("\n" + "=" * 100)
    print("🎯 OVERALL MODEL PERFORMANCE")
    print("=" * 100)
    
    avg_extraction_rate = (
        metrics['company_extraction_rate'] +
        metrics['role_extraction_rate'] +
        metrics['work_exp_extraction_rate'] +
        metrics['education_extraction_rate']
    ) / 4
    
    print(f"\n  Average Extraction Rate: {avg_extraction_rate:.1f}%")
    
    if avg_extraction_rate >= 80:
        print("  ✅ EXCELLENT - Model is performing very well!")
    elif avg_extraction_rate >= 60:
        print("  ⚠️  GOOD - Model is working but has room for improvement")
    elif avg_extraction_rate >= 40:
        print("  ⚠️  FAIR - Model needs significant improvement")
    else:
        print("  ❌ POOR - Model requires retraining or debugging")
    
    print("\n" + "=" * 100)
    print("✅ Testing Complete!")
    print("=" * 100)
    
    # Save detailed results to JSON
    import json
    output_file = base_dir / "model_test_results.json"
    with open(output_file, 'w') as f:
        json.dump({
            'metrics': metrics,
            'results': results
        }, f, indent=2)
    
    print(f"\n💾 Detailed results saved to: {output_file}")


if __name__ == "__main__":
    main()
