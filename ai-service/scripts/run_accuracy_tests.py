#!/usr/bin/env python3
"""
Run accuracy tests against ground truth data
Usage: python scripts/run_accuracy_tests.py [resume_dir] [ground_truth_file]
"""

import sys
import os

# Add parent directory (ai-service) to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from parsers.master_parser import MasterParser
from utils.accuracy_tester import AccuracyTester
from pathlib import Path
import json
import logging

logging.basicConfig(level=logging.WARNING)

def main():
    # Get arguments with defaults
    resume_dir = sys.argv[1] if len(sys.argv) > 1 else 'tests/sample_resumes'
    ground_truth_file = sys.argv[2] if len(sys.argv) > 2 else 'test_dataset/ground_truth/sample_resumes_gt.json'
    
    # Verify paths exist
    if not os.path.exists(resume_dir):
        print(f"❌ Resume directory not found: {resume_dir}")
        print("   Usage: python scripts/run_accuracy_tests.py <resume_dir> <ground_truth_file>")
        return 1
    
    if not os.path.exists(ground_truth_file):
        print(f"❌ Ground truth file not found: {ground_truth_file}")
        print("   Please create ground truth JSON data first")
        return 1
    
    # Initialize parser and tester
    print("🚀 Initializing parser...")
    try:
        parser = MasterParser()
        tester = AccuracyTester(parser)
    except Exception as e:
        print(f"❌ Failed to initialize parser: {e}")
        return 1
    
    print(f"📂 Resume directory: {resume_dir}")
    print(f"📊 Ground truth file: {ground_truth_file}")
    
    # Run test suite
    print("\n⏳ Running accuracy tests...\n")
    results = tester.run_test_suite(
        resume_dir,
        ground_truth_file
    )
    
    # Generate report
    report_path = tester.generate_report()
    
    # Print summary
    print("\n" + "="*60)
    print("ACCURACY TEST RESULTS")
    print("="*60)
    
    if 'aggregate_metrics' in results:
        metrics = results['aggregate_metrics']
        print(f"📊 Total tests:      {metrics.get('total_tests', 0)}")
        print(f"✅ Successful:       {metrics.get('successful_tests', 0)}")
        print(f"❌ Failed:           {metrics.get('failed_tests', 0)}")
        print(f"📈 Success rate:     {metrics.get('success_rate', 0):.1%}")
        print(f"🎯 Avg accuracy:      {metrics.get('average_overall_accuracy', 0):.1%}")
        print(f"📉 Min accuracy:      {metrics.get('min_accuracy', 0):.1%}")
        print(f"📈 Max accuracy:      {metrics.get('max_accuracy', 0):.1%}")
        print(f"⏱️  Avg process time: {metrics.get('average_processing_time', 0):.1f}s")
        print(f"📄 Report saved:     {report_path}")
    
    # Print recommendations
    if 'recommendations' in results and results['recommendations']:
        print("\n📋 Recommendations:")
        for rec in results['recommendations']:
            print(f"   • {rec}")
    
    # Print detailed test results
    if 'test_results' in results:
        print("\n" + "-"*60)
        print("DETAILED RESULTS")
        print("-"*60)
        for result in results['test_results']:
            name = result.get('test_name', 'unknown')
            status = result.get('status', 'unknown')
            if status == 'success':
                acc = result.get('overall_accuracy', {}).get('overall_accuracy', 0)
                print(f"✅ {name}: {acc:.1%} accuracy")
            else:
                error = result.get('error', 'unknown error')
                print(f"❌ {name}: {error}")
    
    print("\n" + "="*60)
    
    # Return exit code based on success
    success_rate = results.get('aggregate_metrics', {}).get('success_rate', 0)
    return 0 if success_rate > 0.5 else 1

if __name__ == '__main__':
    sys.exit(main())
