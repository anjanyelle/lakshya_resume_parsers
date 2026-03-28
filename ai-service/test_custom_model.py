#!/usr/bin/env python3
"""
Test script to verify custom trained model loads and works correctly.
"""

from parsers.ai_ner_parser import AINamedEntityParser

def test_custom_model():
    print("="*60)
    print("🧪 Testing Custom Trained Resume NER Model")
    print("="*60)
    
    # Initialize parser (will use custom model by default)
    print("\n1️⃣ Initializing AI NER Parser...")
    parser = AINamedEntityParser(use_custom_model=True)
    print("✅ Parser initialized successfully!")
    
    # Test with sample resume text
    sample_text = """
    John Smith
    Senior Software Engineer
    Email: john.smith@email.com
    Phone: +1-555-0123
    
    EXPERIENCE
    Google Inc. - Senior Software Engineer (2020-2023)
    Led development of cloud infrastructure using Python and AWS.
    
    EDUCATION
    Stanford University - BS Computer Science (2016-2020)
    
    SKILLS
    Python, Java, AWS, Docker, Kubernetes
    """
    
    print("\n2️⃣ Testing entity extraction...")
    print(f"Sample text length: {len(sample_text)} characters")
    
    entities = parser.extract_entities(sample_text)
    
    print("\n3️⃣ Extracted Entities:")
    print("="*60)
    for entity_type, values in entities.items():
        print(f"  {entity_type.upper()}: {values}")
    
    print("\n" + "="*60)
    print("✅ Test completed successfully!")
    print("="*60)

if __name__ == "__main__":
    test_custom_model()
