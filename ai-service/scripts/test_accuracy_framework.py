#!/usr/bin/env python3
"""
Lightweight accuracy framework test - tests evaluation components without full parser dependencies
Usage: python scripts/test_accuracy_framework.py <resume_dir> <ground_truth_file>
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def load_ground_truth(ground_truth_path):
    """Load ground truth data."""
    with open(ground_truth_path, 'r') as f:
        return json.load(f)

def load_resume_text(resume_path):
    """Load resume text file."""
    with open(resume_path, 'r', encoding='utf-8', errors='ignore') as f:
        return f.read()

def simple_extract_entities(text):
    """Simple rule-based entity extraction for testing."""
    import re
    
    entities = {
        'name': '',
        'email': '',
        'phone': '',
        'work_experience': [],
        'education': [],
        'skills': []
    }
    
    # Extract email
    email_match = re.search(r'[\w.-]+@[\w.-]+\.\w+', text)
    if email_match:
        entities['email'] = email_match.group(0)
    
    # Extract phone
    phone_match = re.search(r'[\+]?[\d\s\-\(\)]{10,}', text)
    if phone_match:
        entities['phone'] = phone_match.group(0).strip()
    
    # Extract name (first line if it looks like a name)
    lines = text.strip().split('\n')
    if lines and len(lines[0].split()) <= 4:
        entities['name'] = lines[0].strip()
    
    return entities

def calculate_field_accuracy(extracted, ground_truth):
    """Calculate accuracy for a single field."""
    if not ground_truth:
        return 0.0
    
    if isinstance(ground_truth, list):
        if not extracted:
            return 0.0
        # Calculate overlap for lists
        gt_set = set(str(item).lower() for item in ground_truth)
        ext_set = set(str(item).lower() for item in extracted) if isinstance(extracted, list) else {str(extracted).lower()}
        
        if not gt_set:
            return 1.0 if not ext_set else 0.0
        
        intersection = gt_set & ext_set
        return len(intersection) / len(gt_set)
    else:
        # String comparison
        return 1.0 if str(extracted).lower() == str(ground_truth).lower() else 0.0

def run_accuracy_test(resume_path, ground_truth):
    """Run a single accuracy test."""
    text = load_resume_text(resume_path)
    extracted = simple_extract_entities(text)
    
    results = {
        'test_name': Path(resume_path).name,
        'fields_tested': [],
        'field_accuracies': {},
        'overall_accuracy': 0.0,
        'errors': []
    }
    
    total_accuracy = 0.0
    field_count = 0
    
    for field in ['name', 'email', 'phone', 'skills']:
        if field in ground_truth:
            extracted_value = extracted.get(field, '')
            gt_value = ground_truth[field]
            
            accuracy = calculate_field_accuracy(extracted_value, gt_value)
            results['field_accuracies'][field] = accuracy
            results['fields_tested'].append(field)
            total_accuracy += accuracy
            field_count += 1
    
    results['overall_accuracy'] = total_accuracy / field_count if field_count > 0 else 0.0
    
    return results

def main():
    resume_dir = sys.argv[1] if len(sys.argv) > 1 else 'tests/sample_resumes'
    ground_truth_file = sys.argv[2] if len(sys.argv) > 2 else 'test_dataset/ground_truth/sample_resumes_gt.json'
    
    if not os.path.exists(resume_dir):
        print(f"❌ Resume directory not found: {resume_dir}")
        return 1
    
    if not os.path.exists(ground_truth_file):
        print(f"❌ Ground truth file not found: {ground_truth_file}")
        return 1
    
    # Load ground truth
    ground_truth_data = load_ground_truth(ground_truth_file)
    
    # Find resume files
    resume_files = list(Path(resume_dir).glob('*.txt'))
    
    print("="*60)
    print("ACCURACY FRAMEWORK TEST")
    print("="*60)
    print(f"📂 Resume directory: {resume_dir}")
    print(f"📊 Ground truth: {ground_truth_file}")
    print(f"📄 Resume files found: {len(resume_files)}\n")
    
    all_results = []
    
    for resume_file in resume_files:
        filename = resume_file.name
        
        # Find ground truth for this resume
        gt = ground_truth_data.get(filename)
        if not gt:
            gt = ground_truth_data.get(filename.replace('.txt', ''))
        
        if not gt:
            print(f"⚠️  No ground truth for {filename}, skipping")
            continue
        
        print(f"⏳ Testing: {filename}...")
        result = run_accuracy_test(str(resume_file), gt)
        all_results.append(result)
        
        print(f"   Overall: {result['overall_accuracy']:.1%}")
        for field, acc in result['field_accuracies'].items():
            status = "✅" if acc >= 0.8 else "⚠️" if acc >= 0.5 else "❌"
            print(f"   {status} {field}: {acc:.1%}")
        print()
    
    # Calculate aggregate metrics
    if all_results:
        avg_accuracy = sum(r['overall_accuracy'] for r in all_results) / len(all_results)
        
        print("="*60)
        print("SUMMARY")
        print("="*60)
        print(f"📊 Total tests: {len(all_results)}")
        print(f"📈 Average accuracy: {avg_accuracy:.1%}")
        
        # Per-field averages
        field_totals = {}
        field_counts = {}
        for result in all_results:
            for field, acc in result['field_accuracies'].items():
                field_totals[field] = field_totals.get(field, 0) + acc
                field_counts[field] = field_counts.get(field, 0) + 1
        
        print(f"\n📋 Per-field accuracy:")
        for field in field_totals:
            avg = field_totals[field] / field_counts[field]
            print(f"   • {field}: {avg:.1%}")
        
        # Generate simple report
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_tests': len(all_results),
            'average_accuracy': avg_accuracy,
            'per_field_accuracy': {f: field_totals[f] / field_counts[f] for f in field_totals},
            'detailed_results': all_results
        }
        
        report_path = f"accuracy_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📄 Report saved: {report_path}")
        print("="*60)
        
        return 0 if avg_accuracy > 0.5 else 1
    else:
        print("❌ No tests could be run")
        return 1

if __name__ == '__main__':
    sys.exit(main())
