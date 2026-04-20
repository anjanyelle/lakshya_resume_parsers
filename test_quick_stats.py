#!/usr/bin/env python3
"""
Quick statistics test - shows only summary numbers
"""

import sys
import os
import logging
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ai-service'))

logging.basicConfig(level=logging.WARNING, format='%(message)s')

def analyze_resume(file_path: str):
    from resume_parser_pipeline import parse_resume
    from parsers.text_extractor import TextExtractor
    
    result = {
        'filename': os.path.basename(file_path),
        'success': False,
        'has_experience': False,
        'has_education': False,
        'has_skills': False,
        'has_summary': False,
        'has_certifications': False,
        'has_projects': False,
    }
    
    try:
        parsed = parse_resume('', file_path=file_path)
        
        result['has_experience'] = len(parsed.get('experience', '')) > 0
        result['has_education'] = len(parsed.get('education', '')) > 0
        result['has_skills'] = len(parsed.get('skills', '')) > 0
        result['has_summary'] = len(parsed.get('summary', '')) > 0
        result['has_certifications'] = len(parsed.get('certifications', '')) > 0
        result['has_projects'] = len(parsed.get('projects', '')) > 0
        result['success'] = True
    except:
        pass
    
    return result

# Find all resume files
resume_files = []
for ext in ['.pdf', '.docx', '.txt']:
    resume_files.extend(Path('resumes').glob(f'*{ext}'))

results = []
for file_path in resume_files:
    result = analyze_resume(str(file_path))
    results.append(result)

# Calculate statistics
total = len(results)
successful = sum(1 for r in results if r['success'])
exp_count = sum(1 for r in results if r['has_experience'])
edu_count = sum(1 for r in results if r['has_education'])
skills_count = sum(1 for r in results if r['has_skills'])
summary_count = sum(1 for r in results if r['has_summary'])
cert_count = sum(1 for r in results if r['has_certifications'])
proj_count = sum(1 for r in results if r['has_projects'])
perfect = sum(1 for r in results if r['has_experience'] and r['has_education'] and r['has_skills'])

print("\n" + "="*80)
print("QUICK STATISTICS AFTER KEYWORD FIXES")
print("="*80)
print(f"\nTotal resumes: {total}")
print(f"Successfully processed: {successful} ({successful/total*100:.1f}%)")
print(f"Perfect (exp+edu+skills): {perfect} ({perfect/successful*100:.1f}% of successful)")
print(f"\nSection Detection:")
print(f"  Experience: {exp_count}/{successful} ({exp_count/successful*100:.1f}%)")
print(f"  Education: {edu_count}/{successful} ({edu_count/successful*100:.1f}%)")
print(f"  Skills: {skills_count}/{successful} ({skills_count/successful*100:.1f}%)")
print(f"  Summary: {summary_count}/{successful} ({summary_count/successful*100:.1f}%)")
print(f"  Certifications: {cert_count}/{successful} ({cert_count/successful*100:.1f}%)")
print(f"  Projects: {proj_count}/{successful} ({proj_count/successful*100:.1f}%)")
print("="*80)
