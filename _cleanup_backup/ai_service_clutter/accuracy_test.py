#!/usr/bin/env python3
"""
Model accuracy testing with expected results
"""

from test_model_accuracy import test_model_with_text

def calculate_accuracy(extracted, expected):
    """Calculate accuracy score"""
    total_correct = 0
    total_expected = len(expected)
    
    for label, expected_values in expected.items():
        extracted_values = extracted.get(label, [])
        matches = 0
        
        for exp_val in expected_values:
            for ext_val in extracted_values:
                if exp_val.lower() in ext_val.lower() or ext_val.lower() in exp_val.lower():
                    matches += 1
                    break
        
        total_correct += matches
        print(f"  {label}: {matches}/{len(expected_values)} correct")
    
    accuracy = (total_correct / total_expected * 100) if total_expected > 0 else 0
    return accuracy, total_correct, total_expected

def run_accuracy_tests():
    """Run comprehensive accuracy tests"""
    
    test_cases = [
        {
            "name": "Simple Experience",
            "text": "Software Developer at Google from 2020 to 2023.",
            "expected": {
                "COMPANY": ["Google"],
                "ROLE": ["Software Developer"],
                "START_DATE": ["2020"],
                "END_DATE": ["2023"]
            }
        },
        {
            "name": "Multiple Companies",
            "text": "Software Developer at Google from 2020 to 2023. React Developer at Microsoft from 2023 to 2025.",
            "expected": {
                "COMPANY": ["Google", "Microsoft"],
                "ROLE": ["Software Developer", "React Developer"],
                "START_DATE": ["2020", "2023"],
                "END_DATE": ["2023", "2025"]
            }
        },
        {
            "name": "Your Resume Format",
            "text": "Software Developer\nLalataksha Consulting Services Pvt Ltd\nJan 2024 - Present",
            "expected": {
                "COMPANY": ["Lalataksha Consulting Services Pvt Ltd"],
                "ROLE": ["Software Developer"],
                "START_DATE": ["Jan"],
                "END_DATE": ["Present"]
            }
        },
        {
            "name": "Education",
            "text": "Bachelor of Technology in Computer Science from IIT Delhi.",
            "expected": {
                "DEGREE": ["Bachelor of Technology"],
                "EDUCATION": ["IIT Delhi"]
            }
        }
    ]
    
    print("="*80)
    print("MODEL ACCURACY TESTS")
    print("="*80)
    
    total_correct_overall = 0
    total_expected_overall = 0
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'='*80}")
        print(f"TEST {i}: {test_case['name']}")
        print(f"{'='*80}")
        print(f"Text: {test_case['text']}")
        
        entities = test_model_with_text(test_case['text'], show_details=False)
        
        # Group extracted entities
        extracted = {}
        for entity in entities:
            label = entity['label']
            if label not in extracted:
                extracted[label] = []
            extracted[label].append(entity['text'])
        
        print(f"\nExpected vs Extracted:")
        accuracy, correct, total = calculate_accuracy(extracted, test_case['expected'])
        
        total_correct_overall += correct
        total_expected_overall += total
        
        print(f"\nTest Accuracy: {accuracy:.1f}%")
        
    print(f"\n{'='*80}")
    print("OVERALL ACCURACY")
    print(f"{'='*80}")
    overall_accuracy = (total_correct_overall / total_expected_overall * 100) if total_expected_overall > 0 else 0
    print(f"Total Correct: {total_correct_overall}/{total_expected_overall}")
    print(f"Overall Accuracy: {overall_accuracy:.1f}%")
    
    if overall_accuracy >= 80:
        print("Status: EXCELLENT")
    elif overall_accuracy >= 60:
        print("Status: GOOD")
    else:
        print("Status: NEEDS IMPROVEMENT")

if __name__ == "__main__":
    run_accuracy_tests()
