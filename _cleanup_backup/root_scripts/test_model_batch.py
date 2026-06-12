#!/usr/bin/env python3
"""
Batch test DeBERTa model with all txt files and generate accuracy report
"""
import os
import json
import requests
from pathlib import Path
from collections import defaultdict

# Configuration
API_URL = "http://localhost:8000/parse-sections"
TEST_DIR = "ai-service/training/data/20 txt files"

def test_single_file(filepath):
    """Test a single txt file and return results"""
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()
    
    # Send to API
    try:
        response = requests.post(
            API_URL,
            json={"experience_text": text, "education_text": ""},
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"HTTP {response.status_code}", "detail": response.text}
    except Exception as e:
        return {"error": str(e)}

def count_expected_entries(text):
    """Estimate expected number of jobs and education entries from text"""
    lines = text.strip().split('\n')
    
    # Count potential job entries (lines with company patterns)
    job_count = 0
    edu_count = 0
    
    for line in lines:
        line = line.strip()
        # Job patterns: Company name followed by location or role
        if any(indicator in line.lower() for indicator in ['engineer', 'developer', 'analyst', 'manager', 'architect', 'consultant']):
            if any(loc in line for loc in [',', 'India', 'CA', 'NY', 'TX', 'WA']):
                job_count += 1
        
        # Education patterns
        if any(degree in line for degree in ['Bachelor', 'Master', 'B.Tech', 'M.Tech', 'B.E', 'M.E', 'B.S', 'M.S']):
            edu_count += 1
    
    return job_count, edu_count

def analyze_results(results):
    """Analyze batch test results and generate metrics"""
    metrics = {
        'total_files': len(results),
        'successful': 0,
        'failed': 0,
        'total_jobs_expected': 0,
        'total_jobs_extracted': 0,
        'total_edu_expected': 0,
        'total_edu_extracted': 0,
        'companies_extracted': 0,
        'roles_extracted': 0,
        'locations_extracted': 0,
        'institutions_extracted': 0,
        'missing_companies': 0,
        'missing_roles': 0,
        'missing_institutions': 0,
        'avg_processing_time': 0,
        'files_with_issues': []
    }
    
    total_time = 0
    
    for filename, data in results.items():
        if 'error' in data:
            metrics['failed'] += 1
            metrics['files_with_issues'].append({
                'file': filename,
                'issue': data['error']
            })
            continue
        
        metrics['successful'] += 1
        
        # Count extracted entities
        work_exp = data.get('work_experience', [])
        education = data.get('education', [])
        
        metrics['total_jobs_extracted'] += len(work_exp)
        metrics['total_edu_extracted'] += len(education)
        
        # Count non-empty fields
        for job in work_exp:
            if job.get('company'):
                metrics['companies_extracted'] += 1
            else:
                metrics['missing_companies'] += 1
            
            if job.get('role'):
                metrics['roles_extracted'] += 1
            else:
                metrics['missing_roles'] += 1
            
            if job.get('location'):
                metrics['locations_extracted'] += 1
        
        for edu in education:
            if edu.get('institution'):
                metrics['institutions_extracted'] += 1
            else:
                metrics['missing_institutions'] += 1
        
        # Processing time
        if 'processing_time_ms' in data:
            total_time += data['processing_time_ms']
    
    if metrics['successful'] > 0:
        metrics['avg_processing_time'] = total_time / metrics['successful']
    
    # Calculate percentages
    if metrics['total_jobs_extracted'] > 0:
        metrics['company_fill_rate'] = (metrics['companies_extracted'] / metrics['total_jobs_extracted']) * 100
        metrics['role_fill_rate'] = (metrics['roles_extracted'] / metrics['total_jobs_extracted']) * 100
        metrics['location_fill_rate'] = (metrics['locations_extracted'] / metrics['total_jobs_extracted']) * 100
    
    if metrics['total_edu_extracted'] > 0:
        metrics['institution_fill_rate'] = (metrics['institutions_extracted'] / metrics['total_edu_extracted']) * 100
    
    return metrics

def main():
    print("=" * 80)
    print("DEBERTA MODEL BATCH TEST - 20 TXT FILES")
    print("=" * 80)
    
    # Find all txt files
    test_path = Path(TEST_DIR)
    txt_files = sorted(test_path.glob("*.txt"))
    
    if not txt_files:
        print(f"❌ No txt files found in {TEST_DIR}")
        return
    
    print(f"\n📁 Found {len(txt_files)} txt files")
    print(f"🌐 Testing against API: {API_URL}\n")
    
    # Test each file
    results = {}
    expected_counts = {}
    
    for i, filepath in enumerate(txt_files, 1):
        filename = filepath.name
        print(f"[{i}/{len(txt_files)}] Testing {filename}...", end=" ")
        
        # Read file and estimate expected entries
        with open(filepath, 'r', encoding='utf-8') as f:
            text = f.read()
        
        job_count, edu_count = count_expected_entries(text)
        expected_counts[filename] = {'jobs': job_count, 'edu': edu_count}
        
        # Test
        result = test_single_file(filepath)
        results[filename] = result
        
        if 'error' in result:
            print(f"❌ FAILED: {result['error']}")
        else:
            jobs = len(result.get('work_experience', []))
            edu = len(result.get('education', []))
            print(f"✅ {jobs} jobs, {edu} edu (expected ~{job_count} jobs, ~{edu_count} edu)")
    
    # Analyze results
    print("\n" + "=" * 80)
    print("ANALYSIS RESULTS")
    print("=" * 80)
    
    metrics = analyze_results(results)
    
    print(f"\n📊 Overall Statistics:")
    print(f"  Total files tested: {metrics['total_files']}")
    print(f"  Successful: {metrics['successful']} ({metrics['successful']/metrics['total_files']*100:.1f}%)")
    print(f"  Failed: {metrics['failed']}")
    
    print(f"\n📈 Extraction Metrics:")
    print(f"  Total jobs extracted: {metrics['total_jobs_extracted']}")
    print(f"  Total education extracted: {metrics['total_edu_extracted']}")
    
    print(f"\n✅ Field Completion Rates:")
    if metrics['total_jobs_extracted'] > 0:
        print(f"  Company names: {metrics['companies_extracted']}/{metrics['total_jobs_extracted']} ({metrics.get('company_fill_rate', 0):.1f}%)")
        print(f"  Role names: {metrics['roles_extracted']}/{metrics['total_jobs_extracted']} ({metrics.get('role_fill_rate', 0):.1f}%)")
        print(f"  Locations: {metrics['locations_extracted']}/{metrics['total_jobs_extracted']} ({metrics.get('location_fill_rate', 0):.1f}%)")
    
    if metrics['total_edu_extracted'] > 0:
        print(f"  Institutions: {metrics['institutions_extracted']}/{metrics['total_edu_extracted']} ({metrics.get('institution_fill_rate', 0):.1f}%)")
    
    print(f"\n⚠️  Missing Fields:")
    print(f"  Missing companies: {metrics['missing_companies']}")
    print(f"  Missing roles: {metrics['missing_roles']}")
    print(f"  Missing institutions: {metrics['missing_institutions']}")
    
    print(f"\n⏱️  Performance:")
    print(f"  Average processing time: {metrics['avg_processing_time']:.2f} ms")
    
    # Show files with issues
    if metrics['files_with_issues']:
        print(f"\n❌ Files with Issues ({len(metrics['files_with_issues'])}):")
        for issue in metrics['files_with_issues']:
            print(f"  - {issue['file']}: {issue['issue']}")
    
    # Detailed results per file
    print("\n" + "=" * 80)
    print("DETAILED RESULTS PER FILE")
    print("=" * 80)
    
    for filename, result in results.items():
        if 'error' in result:
            continue
        
        print(f"\n📄 {filename}")
        
        work_exp = result.get('work_experience', [])
        education = result.get('education', [])
        
        print(f"  Work Experience ({len(work_exp)} entries):")
        for i, job in enumerate(work_exp, 1):
            company = job.get('company', 'MISSING')
            role = job.get('role', 'MISSING')
            location = job.get('location', 'MISSING')
            dates = f"{job.get('start_date', '?')} - {job.get('end_date', '?')}"
            
            status = "✅" if company and role else "⚠️"
            print(f"    {status} Job {i}: {company} | {role} | {location} | {dates}")
        
        print(f"  Education ({len(education)} entries):")
        for i, edu in enumerate(education, 1):
            institution = edu.get('institution', 'MISSING')
            degree = edu.get('degree', 'MISSING')
            field = edu.get('field_of_study', 'MISSING')
            
            status = "✅" if institution else "⚠️"
            print(f"    {status} Edu {i}: {institution} | {degree} | {field}")
    
    # Save results to JSON
    output_file = "test_results_batch.json"
    with open(output_file, 'w') as f:
        json.dump({
            'metrics': metrics,
            'results': results,
            'expected_counts': expected_counts
        }, f, indent=2)
    
    print(f"\n💾 Full results saved to: {output_file}")
    print("=" * 80)

if __name__ == "__main__":
    main()
