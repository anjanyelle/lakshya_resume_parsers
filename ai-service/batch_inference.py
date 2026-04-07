#!/usr/bin/env python3
"""
Batch Resume Processing Script
Process multiple resumes and export to JSON/CSV
"""

import json
import csv
from pathlib import Path
from inference_example import ResumeParser
from tqdm import tqdm
import argparse


def process_resume_folder(folder_path, output_format='json', confidence_threshold=0.7):
    """
    Process all resume files in a folder
    
    Args:
        folder_path: Path to folder containing resume files
        output_format: 'json' or 'csv'
        confidence_threshold: Minimum confidence for entities
    """
    folder = Path(folder_path)
    
    if not folder.exists():
        print(f"❌ Folder not found: {folder}")
        return
    
    # Find all text files
    resume_files = list(folder.glob('*.txt')) + list(folder.glob('*.md'))
    
    if not resume_files:
        print(f"❌ No .txt or .md files found in {folder}")
        return
    
    print(f"📂 Found {len(resume_files)} resume files")
    
    # Initialize parser
    parser = ResumeParser()
    
    # Process all resumes
    results = []
    
    for resume_file in tqdm(resume_files, desc="Processing resumes"):
        try:
            with open(resume_file, 'r', encoding='utf-8') as f:
                resume_text = f.read()
            
            # Extract structured data
            data = parser.extract_structured_data(resume_text, confidence_threshold)
            
            # Add metadata
            data['filename'] = resume_file.name
            data['file_path'] = str(resume_file)
            
            results.append(data)
            
        except Exception as e:
            print(f"\n⚠️  Error processing {resume_file.name}: {e}")
            continue
    
    # Export results
    output_file = folder / f"parsed_resumes.{output_format}"
    
    if output_format == 'json':
        export_to_json(results, output_file)
    elif output_format == 'csv':
        export_to_csv(results, output_file)
    
    print(f"\n✅ Processed {len(results)} resumes")
    print(f"📄 Results saved to: {output_file}")
    
    return results


def export_to_json(results, output_file):
    """Export results to JSON"""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)


def export_to_csv(results, output_file):
    """Export results to CSV (flattened structure)"""
    if not results:
        return
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        # Define CSV columns
        fieldnames = [
            'filename',
            'person_name',
            'current_company',
            'current_role',
            'current_location',
            'total_experience_count',
            'highest_degree',
            'latest_institution',
            'all_companies',
            'all_roles',
            'all_degrees'
        ]
        
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for data in results:
            # Flatten work experience
            work_exp = data.get('work_experience', [])
            current_exp = work_exp[0] if work_exp else {}
            
            # Flatten education
            education = data.get('education', [])
            latest_edu = education[0] if education else {}
            
            row = {
                'filename': data.get('filename', ''),
                'person_name': data.get('person_name', ''),
                'current_company': current_exp.get('company', ''),
                'current_role': current_exp.get('role', ''),
                'current_location': current_exp.get('location', ''),
                'total_experience_count': len(work_exp),
                'highest_degree': latest_edu.get('degree', ''),
                'latest_institution': latest_edu.get('institution', ''),
                'all_companies': ' | '.join([exp.get('company', '') for exp in work_exp if exp.get('company')]),
                'all_roles': ' | '.join([exp.get('role', '') for exp in work_exp if exp.get('role')]),
                'all_degrees': ' | '.join([edu.get('degree', '') for edu in education if edu.get('degree')])
            }
            
            writer.writerow(row)


def generate_statistics(results):
    """Generate statistics from parsed resumes"""
    from collections import Counter
    
    stats = {
        'total_resumes': len(results),
        'with_person_name': sum(1 for r in results if r.get('person_name')),
        'with_work_experience': sum(1 for r in results if r.get('work_experience')),
        'with_education': sum(1 for r in results if r.get('education')),
        'avg_work_experience': sum(len(r.get('work_experience', [])) for r in results) / len(results) if results else 0,
        'avg_education': sum(len(r.get('education', [])) for r in results) / len(results) if results else 0,
    }
    
    # Top companies
    all_companies = []
    for r in results:
        for exp in r.get('work_experience', []):
            if exp.get('company'):
                all_companies.append(exp['company'])
    
    stats['top_companies'] = Counter(all_companies).most_common(10)
    
    # Top roles
    all_roles = []
    for r in results:
        for exp in r.get('work_experience', []):
            if exp.get('role'):
                all_roles.append(exp['role'])
    
    stats['top_roles'] = Counter(all_roles).most_common(10)
    
    return stats


def print_statistics(stats):
    """Print statistics"""
    print("\n" + "="*60)
    print("📊 BATCH PROCESSING STATISTICS")
    print("="*60)
    
    print(f"\n📋 Overview:")
    print(f"  Total Resumes: {stats['total_resumes']}")
    print(f"  With Person Name: {stats['with_person_name']} ({stats['with_person_name']/stats['total_resumes']*100:.1f}%)")
    print(f"  With Work Experience: {stats['with_work_experience']} ({stats['with_work_experience']/stats['total_resumes']*100:.1f}%)")
    print(f"  With Education: {stats['with_education']} ({stats['with_education']/stats['total_resumes']*100:.1f}%)")
    
    print(f"\n📈 Averages:")
    print(f"  Avg Work Experiences per Resume: {stats['avg_work_experience']:.1f}")
    print(f"  Avg Education Entries per Resume: {stats['avg_education']:.1f}")
    
    if stats['top_companies']:
        print(f"\n🏢 Top 10 Companies:")
        for company, count in stats['top_companies']:
            print(f"  • {company}: {count} candidates")
    
    if stats['top_roles']:
        print(f"\n💼 Top 10 Roles:")
        for role, count in stats['top_roles']:
            print(f"  • {role}: {count} candidates")
    
    print("\n" + "="*60 + "\n")


def main():
    """Main function with CLI"""
    parser_cli = argparse.ArgumentParser(description='Batch process resume files')
    parser_cli.add_argument('folder', type=str, help='Path to folder containing resume files')
    parser_cli.add_argument('--format', type=str, choices=['json', 'csv'], default='json',
                           help='Output format (default: json)')
    parser_cli.add_argument('--confidence', type=float, default=0.7,
                           help='Minimum confidence threshold (default: 0.7)')
    parser_cli.add_argument('--stats', action='store_true',
                           help='Show statistics after processing')
    
    args = parser_cli.parse_args()
    
    # Process resumes
    results = process_resume_folder(
        args.folder,
        output_format=args.format,
        confidence_threshold=args.confidence
    )
    
    # Show statistics if requested
    if args.stats and results:
        stats = generate_statistics(results)
        print_statistics(stats)


if __name__ == "__main__":
    main()
