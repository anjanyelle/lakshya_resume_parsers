#!/usr/bin/env python3
"""
Simple test to verify the validator works correctly.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from parsers.validator import ParsedDataValidator

def test_validator():
    print("="*70)
    print("🧪 TESTING PARSED DATA VALIDATOR")
    print("="*70)
    
    validator = ParsedDataValidator()
    
    # Test data with various issues
    test_data = {
        'personal_info': {
            'name': 'john.doe@example.com',  # Email in name field
            'email': 'invalid-email',        # Invalid email format
            'phone': '123456'               # Too short phone
        },
        'years_experience': -5,              # Negative years
        'skills': ['Python', 'A', 'http://example.com', 'Java'],  # Invalid skills
        'experience': [
            {
                'start_date': 'Jan 2030',    # Future date
                'end_date': 'Present'
            }
        ],
        'education': [
            {
                'graduation_date': 'invalid_date'  # Invalid date format
            }
        ]
    }
    
    print(f"\n📝 Original test data:")
    for key, value in test_data.items():
        print(f"   {key}: {value}")
    
    # Validate and fix
    result, warnings = validator.validate_and_fix(test_data)
    
    print(f"\n✨ Validation results:")
    print(f"   Warnings generated: {len(warnings)}")
    for i, warning in enumerate(warnings, 1):
        print(f"   {i}. {warning}")
    
    print(f"\n🔍 Fixed data:")
    for key, value in result.items():
        if key != '_validation_warnings':
            print(f"   {key}: {value}")
    
    print(f"\n📊 Validation summary:")
    summary = validator.get_validation_summary(result)
    for key, value in summary.items():
        print(f"   {key}: {value}")
    
    # Test individual validation methods
    print(f"\n🧪 Testing individual methods:")
    
    # Test name validation
    name_data = {'personal_info': {'name': 'Valid Name'}}
    result, warnings = validator.validate_and_fix(name_data)
    print(f"   Valid name: {'✅' if result['personal_info']['name'] == 'Valid Name' and not warnings else '❌'}")
    
    # Test email validation
    email_data = {'personal_info': {'email': 'valid@example.com'}}
    result, warnings = validator.validate_and_fix(email_data)
    print(f"   Valid email: {'✅' if result['personal_info']['email'] == 'valid@example.com' and not warnings else '❌'}")
    
    # Test phone validation
    phone_data = {'personal_info': {'phone': '+1-555-123-4567'}}
    result, warnings = validator.validate_and_fix(phone_data)
    print(f"   Valid phone: {'✅' if result['personal_info']['phone'] == '+1-555-123-4567' and not warnings else '❌'}")
    
    # Test skills validation
    skills_data = {'skills': ['Python', 'Java', 'JavaScript']}
    result, warnings = validator.validate_and_fix(skills_data)
    print(f"   Valid skills: {'✅' if result['skills'] == ['Python', 'Java', 'JavaScript'] and not warnings else '❌'}")
    
    print(f"\n🎉 Validator test completed!")

if __name__ == "__main__":
    test_validator()
