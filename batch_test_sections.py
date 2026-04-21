#!/usr/bin/env python3
"""
Batch test script to verify section extraction on multiple resume files
Generates a detailed report showing which sections are detected in each resume
"""

import sys
import os
import json
from pathlib import Path

# Add ai-service to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ai-service'))

from parsers.text_extractor import TextExtractor
from parsers.section_splitter import SectionSplitter

def test_resume_file(filepath):
    """Test section extraction on a single resume file"""
    try:
        extractor = TextExtractor()
        splitter = SectionSplitter()
        
        # Extract text based on file type
        if filepath.endswith('.pdf'):
            text, _ = extractor.extract_with_font_metadata(filepath)
        elif filepath.endswith(('.docx', '.doc')):
            text = extractor.extract_from_docx(filepath)
        else:
            print(f"⚠️  Skipping unsupported file type: {filepath}")
            return None
        
        # Split into sections
        sections = splitter.split_sections(text)
        
        # Analyze results
        detected = []
        empty = []
        
        for section_name, content in sections.items():
            if content and content.strip():
                detected.append(section_name)
            else:
                empty.append(section_name)
        
        return {
            'filename': os.path.basename(filepath),
            'filepath': filepath,
            'raw_text_length': len(text),
            'total_sections': len(sections),
            'detected_sections': detected,
            'empty_sections': empty,
            'sections': {k: len(v) for k, v in sections.items() if v.strip()}
        }
        
    except Exception as e:
        print(f"❌ Error processing {filepath}: {str(e)}")
        return {
            'filename': os.path.basename(filepath),
            'filepath': filepath,
            'error': str(e)
        }

def main():
    """Run batch tests on all resume files"""
    
    print("\n" + "="*80)
    print("🧪 BATCH SECTION EXTRACTION TEST")
    print("="*80)
    
    # Test directory
    test_dir = "/Users/anjanyelle/Desktop/untitled folder 3/Lakshya-LLM-Resume-Parser/resumetestmodel/RESUMES_FILES 2"
    
    if not os.path.exists(test_dir):
        print(f"❌ Test directory not found: {test_dir}")
        return
    
    # Get all resume files
    files = []
    for ext in ['.pdf', '.docx', '.doc']:
        files.extend(Path(test_dir).glob(f'*{ext}'))
    
    files = sorted(files)
    print(f"\n📁 Found {len(files)} resume files to test\n")
    
    # Test each file
    results = []
    for i, filepath in enumerate(files, 1):
        print(f"[{i}/{len(files)}] Testing: {filepath.name}")
        result = test_resume_file(str(filepath))
        if result:
            results.append(result)
    
    # Generate summary report
    print("\n\n" + "="*80)
    print("📊 SECTION DETECTION SUMMARY REPORT")
    print("="*80)
    
    # Count section detection across all resumes
    section_stats = {
        'summary': 0,
        'experience': 0,
        'education': 0,
        'skills': 0,
        'certifications': 0,
        'projects': 0
    }
    
    total_tested = 0
    total_errors = 0
    
    for result in results:
        if 'error' in result:
            total_errors += 1
            continue
        
        total_tested += 1
        for section in result['detected_sections']:
            if section in section_stats:
                section_stats[section] += 1
    
    print(f"\n✅ Successfully tested: {total_tested} resumes")
    print(f"❌ Errors: {total_errors} resumes")
    
    print(f"\n📈 Section Detection Rates:")
    print(f"{'─'*80}")
    for section, count in section_stats.items():
        percentage = (count / total_tested * 100) if total_tested > 0 else 0
        bar = '█' * int(percentage / 2)
        print(f"{section.upper():15} │ {count:2}/{total_tested} │ {percentage:5.1f}% │ {bar}")
    
    # Detailed results
    print(f"\n\n{'='*80}")
    print("📋 DETAILED RESULTS BY FILE")
    print(f"{'='*80}\n")
    
    for result in results:
        if 'error' in result:
            print(f"❌ {result['filename']}")
            print(f"   Error: {result['error']}\n")
            continue
        
        print(f"📄 {result['filename']}")
        print(f"   Raw text: {result['raw_text_length']:,} chars")
        print(f"   Detected: {', '.join(result['detected_sections']) if result['detected_sections'] else 'None'}")
        print(f"   Missing:  {', '.join(result['empty_sections']) if result['empty_sections'] else 'None'}")
        
        # Show character counts for detected sections
        if result['sections']:
            print(f"   Lengths:  ", end='')
            section_lengths = [f"{k}={v}" for k, v in result['sections'].items()]
            print(', '.join(section_lengths))
        print()
    
    # Save detailed JSON report
    report_path = os.path.join(os.path.dirname(__file__), 'section_extraction_report.json')
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Detailed JSON report saved to: {report_path}")
    
    print("\n" + "="*80)
    print("✅ BATCH TEST COMPLETED")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()
