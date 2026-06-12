#!/usr/bin/env python3
"""
Merge Multiple Label Studio JSON Exports
==========================================
This script combines multiple Label Studio JSON export files from different team members
into a single consolidated dataset for training.

Usage:
    python merge_label_studio_files.py --input-dir ./label_studio_exports --output merged_data.json
"""

import json
import os
import argparse
from pathlib import Path
from typing import List, Dict, Any
from collections import defaultdict


def load_label_studio_json(file_path: str) -> List[Dict[str, Any]]:
    """Load a Label Studio JSON export file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Handle both single object and array formats
    if isinstance(data, dict):
        return [data]
    return data


def merge_label_studio_files(input_files: List[str], remove_duplicates: bool = True) -> List[Dict[str, Any]]:
    """
    Merge multiple Label Studio JSON files into one dataset.
    
    Args:
        input_files: List of JSON file paths
        remove_duplicates: Remove duplicate texts (default: True)
    
    Returns:
        Merged list of annotated examples
    """
    all_examples = []
    seen_texts = set()
    stats = defaultdict(int)
    
    for file_path in input_files:
        print(f"📂 Processing: {os.path.basename(file_path)}")
        
        try:
            examples = load_label_studio_json(file_path)
            file_count = 0
            
            for example in examples:
                text = example.get('data', {}).get('text', '')
                
                # Skip if no text
                if not text:
                    stats['skipped_no_text'] += 1
                    continue
                
                # Skip if no annotations
                annotations = example.get('annotations', [])
                if not annotations:
                    stats['skipped_no_annotations'] += 1
                    continue
                
                # Check for duplicates
                if remove_duplicates:
                    if text in seen_texts:
                        stats['duplicates_removed'] += 1
                        continue
                    seen_texts.add(text)
                
                all_examples.append(example)
                file_count += 1
            
            stats[f'from_{os.path.basename(file_path)}'] = file_count
            print(f"  ✅ Added {file_count} examples")
            
        except Exception as e:
            print(f"  ❌ Error processing {file_path}: {e}")
            stats['errors'] += 1
    
    return all_examples, dict(stats)


def analyze_dataset(examples: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze the merged dataset and return statistics."""
    stats = {
        'total_examples': len(examples),
        'label_counts': defaultdict(int),
        'avg_entities_per_example': 0,
        'total_entities': 0,
        'avg_text_length': 0,
    }
    
    total_entities = 0
    total_text_length = 0
    
    for example in examples:
        text = example.get('data', {}).get('text', '')
        total_text_length += len(text)
        
        annotations = example.get('annotations', [])
        for ann in annotations:
            for result in ann.get('result', []):
                value = result.get('value', {})
                if 'labels' in value:
                    for label in value['labels']:
                        stats['label_counts'][label] += 1
                        total_entities += 1
    
    stats['total_entities'] = total_entities
    stats['avg_entities_per_example'] = total_entities / len(examples) if examples else 0
    stats['avg_text_length'] = total_text_length / len(examples) if examples else 0
    
    return stats


def main():
    parser = argparse.ArgumentParser(description='Merge Label Studio JSON export files')
    parser.add_argument('--input-dir', type=str, help='Directory containing JSON files')
    parser.add_argument('--input-files', nargs='+', help='Specific JSON files to merge')
    parser.add_argument('--output', type=str, default='merged_label_studio.json', help='Output file path')
    parser.add_argument('--keep-duplicates', action='store_true', help='Keep duplicate texts')
    parser.add_argument('--stats', action='store_true', help='Show detailed statistics')
    
    args = parser.parse_args()
    
    # Collect input files
    input_files = []
    if args.input_dir:
        input_dir = Path(args.input_dir)
        input_files = list(input_dir.glob('*.json'))
        print(f"📁 Found {len(input_files)} JSON files in {args.input_dir}")
    elif args.input_files:
        input_files = [Path(f) for f in args.input_files]
    else:
        print("❌ Error: Please provide --input-dir or --input-files")
        return
    
    if not input_files:
        print("❌ No JSON files found!")
        return
    
    print(f"\n🔄 Merging {len(input_files)} files...\n")
    
    # Merge files
    merged_data, merge_stats = merge_label_studio_files(
        [str(f) for f in input_files],
        remove_duplicates=not args.keep_duplicates
    )
    
    # Save merged data
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(merged_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Merged dataset saved to: {args.output}")
    print(f"📊 Total examples: {len(merged_data)}")
    
    # Show merge statistics
    print("\n📈 Merge Statistics:")
    for key, value in merge_stats.items():
        print(f"  {key}: {value}")
    
    # Analyze dataset
    if args.stats:
        print("\n📊 Dataset Analysis:")
        stats = analyze_dataset(merged_data)
        print(f"  Total examples: {stats['total_examples']}")
        print(f"  Total entities: {stats['total_entities']}")
        print(f"  Avg entities per example: {stats['avg_entities_per_example']:.2f}")
        print(f"  Avg text length: {stats['avg_text_length']:.0f} chars")
        print(f"\n  Label distribution:")
        for label, count in sorted(stats['label_counts'].items(), key=lambda x: x[1], reverse=True):
            print(f"    {label}: {count}")


if __name__ == '__main__':
    main()
