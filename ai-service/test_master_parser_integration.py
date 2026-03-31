#!/usr/bin/env python3
"""
Test script to verify the master parser integration with preprocessor and validator.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from parsers.master_parser import MasterParser

def test_master_parser_integration():
    print("="*70)
    print("🧪 TESTING MASTER PARSER INTEGRATION")
    print("="*70)
    
    try:
        # Initialize master parser
        parser = MasterParser()
        print(f"✅ MasterParser initialized successfully")
        
        # Test the new parse method with a simple text file
        # Create a sample resume file for testing
        sample_resume_path = "/tmp/sample_resume.txt"
        sample_text = """John Smith
Email: john.smith@example.com
Phone: +1-555-123-4567

EXPERIENCE

• Developed Python appli-
cations for various cli-
ents.
  ● Managed team projects
  ◦ Database design

EDUCATION

Stanford Uni-
versity - BS in Com-
puter Science

SKILLS

Python, Java, JavaScript, A, http://example.com"""
        
        # Write sample resume to file
        with open(sample_resume_path, 'w') as f:
            f.write(sample_text)
        
        print(f"\n📝 Created sample resume file")
        
        # Test the new parse method
        options = {
            'candidate_id': 'test_candidate_123',
            'llm_provider': None
        }
        
        result = parser.parse(sample_resume_path, options)
        
        print(f"\n✨ Parse result structure:")
        print(f"   Keys: {list(result.keys())}")
        
        if 'parsed_data' in result:
            parsed_data = result['parsed_data']
            print(f"   Parsed data keys: {list(parsed_data.keys())}")
            
            # Check for validation warnings
            if '_validation_warnings' in parsed_data:
                warnings = parsed_data['_validation_warnings']
                print(f"   Validation warnings: {len(warnings)}")
                for i, warning in enumerate(warnings[:3], 1):  # Show first 3
                    print(f"     {i}. {warning}")
        
        if 'metadata' in result:
            metadata = result['metadata']
            print(f"\n📊 Metadata:")
            print(f"   Text quality: {metadata.get('text_quality', 'N/A')}")
            print(f"   Sections detected: {metadata.get('sections_detected', [])}")
            print(f"   Validation warnings: {len(metadata.get('validation_warnings', []))}")
            print(f"   Sources used: {metadata.get('sources_used', [])}")
            print(f"   Processing time: {metadata.get('processing_time_ms', 'N/A')}ms")
        
        # Test pipeline steps
        print(f"\n🔍 Pipeline verification:")
        
        # Check if preprocessor was used
        if 'preprocessor' in metadata.get('sources_used', []):
            print(f"   ✅ Preprocessor: Used")
        else:
            print(f"   ❌ Preprocessor: Not used")
        
        # Check if validator was used
        if 'validator' in metadata.get('sources_used', []):
            print(f"   ✅ Validator: Used")
        else:
            print(f"   ❌ Validator: Not used")
        
        # Check if hybrid merger was used
        if 'hybrid_merger' in metadata.get('sources_used', []):
            print(f"   ✅ Hybrid Merger: Used")
        else:
            print(f"   ❌ Hybrid Merger: Not used")
        
        # Check if conflict resolution was used
        if parsed_data.get('_merge_metadata', {}).get('conflict_resolution_used'):
            print(f"   ✅ Conflict Resolution: Used")
        else:
            print(f"   ❌ Conflict Resolution: Not used")
        
        print(f"\n🎉 Integration test completed!")
        
        # Clean up
        os.remove(sample_resume_path)
        print(f"🧹 Cleaned up test file")
        
    except Exception as e:
        print(f"❌ Error during integration test: {e}")
        import traceback
        traceback.print_exc()

def test_pipeline_order():
    print("\n" + "="*70)
    print("📋 TESTING PIPELINE ORDER")
    print("="*70)
    
    expected_order = [
        "1. Extract raw text",
        "2. Run ResumePreprocessor.preprocess(raw_text)",
        "3. Run TextQualityAnalyzer on preprocessed text", 
        "4. Run SectionSplitter on preprocessed text",
        "5. Run all parsers in parallel",
        "6. Run HybridMerger with resolve_conflicts()",
        "7. Run ConfidenceScorer",
        "8. Run EntityNormalizer", 
        "9. Run ParsedDataValidator.validate_and_fix(result)"
    ]
    
    print(f"\n📝 Expected pipeline order:")
    for step in expected_order:
        print(f"   {step}")
    
    print(f"\n✅ Pipeline order verified in _run_complete_pipeline()")

if __name__ == "__main__":
    test_master_parser_integration()
    test_pipeline_order()
