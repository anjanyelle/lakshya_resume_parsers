#!/usr/bin/env python3
"""
Debug script to see what entities the NER model extracts
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from transformers import pipeline
from pathlib import Path

def debug_ner_entities():
    """Debug what entities the NER model extracts"""
    
    # Test with the exact model being used
    model_path = Path('./models/resume-ner-deberta')
    if not model_path.exists():
        print("❌ Custom model not found, using fallback model")
        model_name = "jjzha/jobbert-base-cased"
    else:
        print("✅ Using custom model")
        model_name = str(model_path)
    
    # Load the NER pipeline
    try:
        ner = pipeline('ner', model=model_name, aggregation_strategy='simple')
        print(f"✅ Loaded model: {model_name}")
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        return
    
    # Test with your experience text
    text = "Senior Data Engineer at Home Depot Atlanta, GA March 2023 - Present"
    print(f"\n📝 Testing text: {text}")
    
    try:
        entities = ner(text)
        print(f"🎯 Found {len(entities)} entities:")
        
        for i, ent in enumerate(entities, 1):
            word = ent.get('word', '').strip()
            label = ent.get('entity_group', ent.get('entity', '')).upper()
            score = ent.get('score', 0)
            start = ent.get('start', 0)
            end = ent.get('end', 0)
            
            print(f"  {i}. '{word}' -> {label} (score: {score:.3f}) [{start}:{end}]")
            
        # Test with more complex experience text
        complex_text = """Senior Data Engineer
Home Depot
Atlanta, GA
March 2023 - Present

Environment: Python, Java, SQL, Hadoop, HDFS, MapReduce, Hive, Spark
- Designed multi-account AWS landing zone
- Implemented secure VPC peering"""
        
        print(f"\n📝 Testing complex text:")
        print(complex_text[:100] + "...")
        
        complex_entities = ner(complex_text)
        print(f"🎯 Found {len(complex_entities)} entities:")
        
        for i, ent in enumerate(complex_entities, 1):
            word = ent.get('word', '').strip()
            label = ent.get('entity_group', ent.get('entity', '')).upper()
            score = ent.get('score', 0)
            
            print(f"  {i}. '{word}' -> {label} (score: {score:.3f})")
            
        # Analyze label patterns
        print(f"\n📊 Label Analysis:")
        all_labels = [ent.get('entity_group', ent.get('entity', '')).upper() for ent in complex_entities]
        unique_labels = list(set(all_labels))
        for label in unique_labels:
            count = all_labels.count(label)
            print(f"  {label}: {count} entities")
            
    except Exception as e:
        print(f"❌ Error extracting entities: {e}")

if __name__ == "__main__":
    debug_ner_entities()
