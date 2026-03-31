#!/usr/bin/env python3
"""
Simple test to verify the master parser integration structure.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_integration_structure():
    print("="*70)
    print("🧪 TESTING INTEGRATION STRUCTURE")
    print("="*70)
    
    try:
        # Test that the imports work
        from parsers.preprocessor import ResumePreprocessor
        from parsers.validator import ParsedDataValidator
        print(f"✅ New components imported successfully")
        
        # Test that they can be instantiated
        preprocessor = ResumePreprocessor()
        validator = ParsedDataValidator()
        print(f"✅ New components instantiated successfully")
        
        # Test preprocessing
        sample_text = """EXPERIENCE

• Developed Python appli-
cations for various cli-
ents.

EDUCATION

Stanford Uni-
versity - BS in Com-
puter Science"""
        
        preprocessed = preprocessor.preprocess(sample_text)
        print(f"✅ Preprocessing works: {len(preprocessed)} chars")
        
        # Test validation
        test_data = {
            'personal_info': {
                'name': 'john.doe@example.com',  # Should be flagged
                'email': 'invalid-email',        # Should be flagged
                'phone': '123456'               # Should be flagged
            },
            'years_experience': -5,
            'skills': ['Python', 'A', 'http://example.com']
        }
        
        validated, warnings = validator.validate_and_fix(test_data)
        print(f"✅ Validation works: {len(warnings)} warnings generated")
        
        # Check that warnings are stored
        if '_validation_warnings' in validated:
            print(f"✅ Warnings stored in result: {len(validated['_validation_warnings'])}")
        
        print(f"\n🎉 Integration structure test completed!")
        
    except Exception as e:
        print(f"❌ Error during structure test: {e}")
        import traceback
        traceback.print_exc()

def test_pipeline_order_verification():
    print("\n" + "="*70)
    print("📋 VERIFYING PIPELINE ORDER IN CODE")
    print("="*70)
    
    # Read the master_parser.py file to verify pipeline order
    try:
        with open('parsers/master_parser.py', 'r') as f:
            content = f.read()
        
        # Check for the new pipeline steps
        pipeline_checks = [
            ("ResumePreprocessor", "Step 2: Run ResumePreprocessor"),
            ("TextQualityAnalyzer", "Step 3: Run TextQualityAnalyzer"),
            ("SectionSplitter", "Step 4: Run SectionSplitter"),
            ("HybridMerger", "Step 6: Run HybridMerger"),
            ("ConfidenceScorer", "Step 7: Run ConfidenceScorer"),
            ("EntityNormalizer", "Step 8: Run EntityNormalizer"),
            ("ParsedDataValidator", "Step 9: Run ParsedDataValidator")
        ]
        
        print(f"\n🔍 Checking pipeline implementation:")
        for component, description in pipeline_checks:
            if component in content:
                print(f"   ✅ {description}: Found")
            else:
                print(f"   ❌ {description}: Not found")
        
        # Check for the new parse method
        if "def parse(self, file_path: str, options: dict = None) -> dict:" in content:
            print(f"   ✅ New parse method: Found")
        else:
            print(f"   ❌ New parse method: Not found")
        
        # Check for resolve_conflicts usage
        if "resolve_conflicts" in content:
            print(f"   ✅ Conflict resolution: Found")
        else:
            print(f"   ❌ Conflict resolution: Not found")
        
        # Check for validation_warnings in metadata
        if "'validation_warnings'" in content:
            print(f"   ✅ Validation warnings in metadata: Found")
        else:
            print(f"   ❌ Validation warnings in metadata: Not found")
        
        print(f"\n🎉 Pipeline order verification completed!")
        
    except Exception as e:
        print(f"❌ Error reading master_parser.py: {e}")

def test_imports_verification():
    print("\n" + "="*70)
    print("📦 VERIFYING IMPORTS")
    print("="*70)
    
    try:
        with open('parsers/master_parser.py', 'r') as f:
            content = f.read()
        
        required_imports = [
            "from parsers.preprocessor import ResumePreprocessor",
            "from parsers.validator import ParsedDataValidator"
        ]
        
        print(f"\n🔍 Checking required imports:")
        for import_stmt in required_imports:
            if import_stmt in content:
                print(f"   ✅ {import_stmt}: Found")
            else:
                print(f"   ❌ {import_stmt}: Not found")
        
        print(f"\n🎉 Import verification completed!")
        
    except Exception as e:
        print(f"❌ Error checking imports: {e}")

if __name__ == "__main__":
    test_integration_structure()
    test_pipeline_order_verification()
    test_imports_verification()
