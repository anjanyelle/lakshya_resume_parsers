#!/usr/bin/env python3
"""
Enhanced DeBERTa Model Testing with Accuracy Analysis
Shows what entities are expected vs what's actually extracted
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ai-service'))

from test_deberta_model import DeBERTaModelTester

def test_with_expected_results():
    """Test model with expected results comparison"""
    
    test_cases = [
        {
            "name": "Work Experience + Education",
            "file": "1.txt",
            "expected": {
                "COMPANY": ["ABC Tech Solutions Pvt Ltd", "XYZ Innovations Pvt Ltd"],
                "ROLE": ["Software Developer", "Frontend Developer"],
                "DEGREE": ["B.Tech"],
                "EDUCATION": ["JNTU Hyderabad"],
                "START_DATE": ["Jan", "Jun", "2017"],
                "END_DATE": ["Present", "Dec", "2021"]
            }
        },
        {
            "name": "Sample Resume 1",
            "file": "Sample.txt",
            "expected": {
                "COMPANY": ["ABC Tech Solutions Pvt Ltd", "XYZ Innovations Pvt Ltd"],
                "ROLE": ["Software Developer", "Frontend Developer"],
                "START_DATE": ["Feb", "Jan"],
                "END_DATE": ["Present", "Jan"]
            }
        },
        {
            "name": "Sample Resume 2", 
            "file": "Sample1.txt",
            "expected": {
                "COMPANY": ["NextGen Software Pvt Ltd", "CodeCraft Technologies Pvt Ltd"],
                "ROLE": ["Full Stack Developer", "React Developer"],
                "START_DATE": ["Mar", "Jul"],
                "END_DATE": ["Present", "Feb"]
            }
        },
        {
            "name": "Sample Resume 3",
            "file": "Sample3.txt", 
            "expected": {
                "COMPANY": ["TechNova Solutions Pvt Ltd", "WebSpark Technologies Pvt Ltd"],
                "ROLE": ["Software Engineer", "Frontend Developer"],
                "START_DATE": ["Jan", "Aug"],
                "END_DATE": ["Present", "Dec"]
            }
        }
    ]
    
    tester = DeBERTaModelTester()
    
    print("="*100)
    print("COMPREHENSIVE DEBERTA MODEL TESTING WITH ACCURACY ANALYSIS")
    print("="*100)
    
    total_correct = 0
    total_expected = 0
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'='*80}")
        print(f"TEST CASE {i}: {test_case['name']}")
        print(f"{'='*80}")
        
        try:
            # Read file content
            with open(test_case['file'], 'r') as f:
                text = f.read().strip()
            
            print(f"File: {test_case['file']}")
            print(f"Text length: {len(text)} characters")
            print("\nExpected entities:")
            for label, values in test_case['expected'].items():
                print(f"  {label}: {values}")
            
            # Test the model
            entities = tester.test_text(text, test_case['expected'], show_details=False)
            
            # Calculate accuracy
            overall_accuracy, results = tester.calculate_accuracy(entities, test_case['expected'])
            
            print(f"\nAccuracy Results:")
            for label, result in results.items():
                if label == 'overall':
                    print(f"  OVERALL: {result['accuracy']:.1f}% ({result['correct']}/{result['expected']})")
                    total_correct += result['correct']
                    total_expected += result['expected']
                else:
                    print(f"  {label}: {result['accuracy']:.1f}% ({result['correct']}/{result['expected']})")
            
            # Show missing entities
            print(f"\nMissing entities:")
            for label, expected_values in test_case['expected'].items():
                extracted_values = [e['text'] for e in entities if e['label'] == label]
                for exp_val in expected_values:
                    found = False
                    for ext_val in extracted_values:
                        if exp_val.lower() in ext_val.lower() or ext_val.lower() in exp_val.lower():
                            found = True
                            break
                    if not found:
                        print(f"  {label}: '{exp_val}'")
            
        except FileNotFoundError:
            print(f"File not found: {test_case['file']}")
        except Exception as e:
            print(f"Error processing {test_case['file']}: {e}")
    
    print(f"\n{'='*80}")
    print(f"OVERALL MODEL PERFORMANCE")
    print(f"{'='*80}")
    if total_expected > 0:
        overall_accuracy = (total_correct / total_expected * 100)
        print(f"Total Accuracy: {overall_accuracy:.1f}% ({total_correct}/{total_expected})")
    else:
        print("No test cases processed")
    
    # Recommendations
    print(f"\n{'='*80}")
    print(f"RECOMMENDATIONS FOR MODEL IMPROVEMENT")
    print(f"{'='*80}")
    print("1. Add more training examples for EDUCATION institution names")
    print("2. Include date patterns in training data")
    print("3. Add location examples if needed")
    print("4. Consider adding CLIENT entity examples")
    print("5. Include more company name variations")

if __name__ == "__main__":
    test_with_expected_results()
