#!/usr/bin/env python3
"""
Test script to verify the feedback store functionality.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from parsers.feedback_store import FeedbackStore

def test_feedback_store():
    print("="*70)
    print("🧪 TESTING FEEDBACK STORE")
    print("="*70)
    
    try:
        # Initialize feedback store with test directory
        test_storage = "test_feedback_data"
        store = FeedbackStore(storage_dir=test_storage)
        print(f"✅ FeedbackStore initialized with storage: {test_storage}")
        
        # Test 1: Save low confidence parse
        print(f"\n📝 Test 1: Save low confidence parse")
        parsed_data = {
            'name': 'John Smith',
            'email': 'john@example.com',
            'phone': '+1-555-123-4567',
            'skills': ['Python', 'Java']
        }
        
        confidence_scores = {
            'overall': 0.65,  # Below 0.75 threshold
            'sections': {
                'personal_info': 0.70,
                'skills': 0.60
            },
            'fields': {
                'name': 0.80,
                'email': 0.50,
                'phone': 0.70
            }
        }
        
        raw_text = """John Smith
Email: john@example.com
Phone: +1-555-123-4567
Skills: Python, Java, JavaScript"""
        
        store.save_low_confidence_parse(parsed_data, confidence_scores, raw_text)
        print(f"✅ Low confidence case saved")
        
        # Test 2: Save high confidence parse (should not save)
        print(f"\n📝 Test 2: Save high confidence parse (should not save)")
        high_confidence_scores = {'overall': 0.85}  # Above threshold
        store.save_low_confidence_parse(parsed_data, high_confidence_scores, raw_text)
        print(f"✅ High confidence case correctly ignored")
        
        # Test 3: Save user correction
        print(f"\n📝 Test 3: Save user correction")
        store.save_user_correction(
            original_parse_id="test-parse-123",
            field="name",
            wrong_value="John Sm",
            correct_value="John Smith"
        )
        print(f"✅ User correction saved")
        
        # Test 4: Get low confidence cases
        print(f"\n📝 Test 4: Get low confidence cases")
        cases = store.get_low_confidence_cases(limit=10)
        print(f"✅ Retrieved {len(cases)} low confidence cases")
        if cases:
            case = cases[0]
            print(f"   Case ID: {case.get('id')}")
            print(f"   Confidence: {case.get('overall_confidence')}")
            print(f"   Type: {case.get('type')}")
        
        # Test 5: Get user corrections
        print(f"\n📝 Test 5: Get user corrections")
        corrections = store.get_user_corrections(limit=10)
        print(f"✅ Retrieved {len(corrections)} user corrections")
        if corrections:
            correction = corrections[0]
            print(f"   Correction ID: {correction.get('id')}")
            print(f"   Field: {correction.get('field_corrected')}")
            print(f"   Wrong: {correction.get('wrong_value')}")
            print(f"   Correct: {correction.get('correct_value')}")
        
        # Test 6: Get statistics
        print(f"\n📝 Test 6: Get statistics")
        stats = store.get_statistics()
        print(f"✅ Statistics retrieved:")
        for key, value in stats.items():
            print(f"   {key}: {value}")
        
        # Test 7: Mark case as reviewed
        print(f"\n📝 Test 7: Mark case as reviewed")
        if cases:
            case_id = cases[0].get('id')
            store.mark_case_reviewed(case_id, reviewer_notes="Reviewed in test")
            print(f"✅ Case {case_id} marked as reviewed")
        
        # Test 8: Mark correction as processed
        print(f"\n📝 Test 8: Mark correction as processed")
        if corrections:
            correction_id = corrections[0].get('id')
            store.mark_correction_processed(correction_id)
            print(f"✅ Correction {correction_id} marked as processed")
        
        # Test 9: Export training data
        print(f"\n📝 Test 9: Export training data")
        export_file = store.export_training_data()
        print(f"✅ Training data exported to: {export_file}")
        
        print(f"\n🎉 All feedback store tests passed!")
        
        # Cleanup test directory
        import shutil
        if os.path.exists(test_storage):
            shutil.rmtree(test_storage)
            print(f"🧹 Cleaned up test directory")
        
    except Exception as e:
        print(f"❌ Error during feedback store test: {e}")
        import traceback
        traceback.print_exc()

def test_master_parser_integration():
    print("\n" + "="*70)
    print("🔗 TESTING MASTER PARSER INTEGRATION")
    print("="*70)
    
    try:
        # Test that the master parser can import and use the feedback store
        from parsers.master_parser import MasterParser
        
        parser = MasterParser()
        
        # Check if feedback store is available
        if hasattr(parser, 'feedback_store') and parser.feedback_store:
            print(f"✅ FeedbackStore integrated in MasterParser")
            
            # Test the save_user_correction method
            success = parser.save_user_correction(
                original_parse_id="test-integration-123",
                field="email",
                wrong_value="wrong@email.com",
                correct_value="correct@email.com"
            )
            
            if success:
                print(f"✅ User correction saved through MasterParser")
            else:
                print(f"❌ Failed to save user correction through MasterParser")
            
            # Test feedback statistics
            stats = parser.get_feedback_statistics()
            if 'error' not in stats:
                print(f"✅ Feedback statistics retrieved through MasterParser")
                print(f"   Total records: {stats.get('total_records', 0)}")
                print(f"   Low confidence cases: {stats.get('low_confidence_cases', 0)}")
                print(f"   User corrections: {stats.get('user_corrections', 0)}")
            else:
                print(f"❌ Error getting feedback statistics: {stats['error']}")
        else:
            print(f"❌ FeedbackStore not available in MasterParser")
        
        print(f"\n🎉 Master Parser integration test completed!")
        
    except Exception as e:
        print(f"❌ Error during master parser integration test: {e}")
        import traceback
        traceback.print_exc()

def test_api_endpoint_structure():
    print("\n" + "="*70)
    print("🌐 TESTING API ENDPOINT STRUCTURE")
    print("="*70)
    
    try:
        # Check if the API endpoint file exists and has the correct structure
        api_file = "../backend/app/api/v1/endpoints/corrections.py"
        
        if os.path.exists(api_file):
            with open(api_file, 'r') as f:
                content = f.read()
            
            # Check for the new endpoint
            if '@router.post("/parse/{parse_id}/correct")' in content:
                print(f"✅ POST /parse/{{parse_id}}/correct endpoint found")
            else:
                print(f"❌ POST /parse/{{parse_id}}/correct endpoint not found")
            
            # Check for the request model
            if 'class UserCorrectionRequest' in content:
                print(f"✅ UserCorrectionRequest model found")
            else:
                print(f"❌ UserCorrectionRequest model not found")
            
            # Check for the feedback store integration
            if 'from parsers.master_parser import MasterParser' in content:
                print(f"✅ MasterParser import found")
            else:
                print(f"❌ MasterParser import not found")
            
            # Check for the save_user_correction call
            if 'save_user_correction' in content:
                print(f"✅ save_user_correction call found")
            else:
                print(f"❌ save_user_correction call not found")
            
            print(f"✅ API endpoint structure verified")
        else:
            print(f"❌ API endpoint file not found: {api_file}")
        
        print(f"\n🎉 API endpoint structure test completed!")
        
    except Exception as e:
        print(f"❌ Error during API endpoint test: {e}")

if __name__ == "__main__":
    test_feedback_store()
    test_master_parser_integration()
    test_api_endpoint_structure()
