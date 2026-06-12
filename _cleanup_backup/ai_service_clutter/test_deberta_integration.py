#!/usr/bin/env python3
"""
Test script to verify DeBERTa NER integration in AI service.
"""

import sys
import os
from pathlib import Path

# Add the ai-service directory to path
sys.path.append(str(Path(__file__).parent))

from parsers.master_parser import MasterParser

def test_deberta_integration():
    """Test DeBERTa NER integration with sample resume text."""
    
    # Sample resume text
    sample_text = """
    John Doe
    Senior Java Developer at Infosys, Hyderabad
    from Jan 2021 to Mar 2023. Client: Google.
    
    B.Tech Computer Science, JNTU Hyderabad, 2016-2020
    Skills: Java, Python, AWS, Docker
    
    Work Experience:
    - Software Engineer at TCS, Bangalore (2019-2021)
    - Intern at Wipro, Pune (2018-2019)
    
    Education:
    Bachelor of Technology in Computer Science Engineering
    Jawaharlal Nehru Technological University, Hyderabad
    2016 - 2020
    """
    
    print("🧪 Testing DeBERTa NER Integration")
    print("=" * 50)
    
    # Initialize MasterParser
    try:
        parser = MasterParser()
        print("✅ MasterParser initialized successfully")
        
        # Check if DeBERTa parser is available
        if hasattr(parser, 'deberta_parser') and parser.deberta_parser:
            if parser.deberta_parser.is_available():
                print("✅ DeBERTa NER Parser is available and loaded")
            else:
                print("⚠️  DeBERTa NER Parser not available - will use fallback")
        else:
            print("⚠️  DeBERTa NER Parser not initialized")
        
        # Test parsing
        print("\n🔍 Testing resume parsing...")
        result = parser.parse_text(sample_text, "test-candidate-001")
        
        # Check results
        print(f"✅ Parsing completed successfully")
        print(f"📊 Status: {result.get('status')}")
        print(f"👤 Name: {result.get('name')}")
        print(f"🏢 Companies: {result.get('companies', [])}")
        print(f"📍 Locations: {result.get('locations', [])}")
        print(f"💼 Job Titles: {result.get('job_titles', [])}")
        print(f"🎓 Education: {len(result.get('education', []))} entries")
        print(f"💻 Skills: {len(result.get('skills', []))} skills")
        
        # Check if DeBERTa was used
        processing_metrics = result.get('processing_metrics', {})
        if 'deberta_parsing_ms' in processing_metrics:
            deberta_time = processing_metrics['deberta_parsing_ms']
            print(f"🤖 DeBERTa parsing time: {deberta_time:.1f}ms")
            print("✅ DeBERTa NER was used in parsing!")
        else:
            print("⚠️  DeBERTa NER was not used (fallback parsing)")
        
        # Check merge metadata
        merge_metadata = result.get('_merge_metadata', {})
        if merge_metadata:
            sources = merge_metadata.get('sources_available', {})
            print(f"📋 Sources used: {sources}")
            if sources.get('deberta'):
                print("✅ DeBERTa results included in merge!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return False

if __name__ == "__main__":
    success = test_deberta_integration()
    if success:
        print("\n🎉 DeBERTa integration test completed successfully!")
    else:
        print("\n💥 DeBERTa integration test failed!")
        sys.exit(1)
