#!/usr/bin/env python3
"""
Test the FastAPI server with the new trained model
"""

import requests
import json

API_URL = "http://localhost:8000"

print("="*70)
print("🧪 TESTING FASTAPI SERVER WITH NEW MODEL")
print("="*70)
print()

# Test 1: Health Check
print("TEST 1: Health Check")
print("-" * 70)
try:
    response = requests.get(f"{API_URL}/health")
    if response.status_code == 200:
        health = response.json()
        print(f"✅ Server Status: {health['status']}")
        print(f"✅ Version: {health['version']}")
        print(f"✅ Extractor Available: {health['extractor_available']}")
        print(f"✅ Supported Formats: {health['supported_formats']}")
    else:
        print(f"❌ Health check failed: {response.status_code}")
except Exception as e:
    print(f"❌ Error connecting to server: {e}")
    print("\n💡 Make sure the server is running:")
    print("   source venv/bin/activate && python ai-service/main.py")
    exit(1)

print()

# Test 2: Model Info
print("TEST 2: Model Information")
print("-" * 70)
try:
    response = requests.get(f"{API_URL}/model-info")
    if response.status_code == 200:
        info = response.json()
        print(f"✅ Model Name: {info['model_name']}")
        print(f"✅ Model Type: {info['model_type']}")
        print(f"✅ Device: {info['device']}")
        print(f"✅ Total Parses: {info['total_parses']}")
        print(f"✅ Successful Parses: {info['successful_parses']}")
        print(f"✅ Success Rate: {info['successful_parse_rate']*100:.1f}%")
        print(f"✅ Supported Entities: {len(info['supported_entities'])} entities")
        print(f"   {', '.join(info['supported_entities'][:10])}...")
    else:
        print(f"⚠️  Model info not available: {response.status_code}")
except Exception as e:
    print(f"⚠️  Error getting model info: {e}")

print()

# Test 3: Extract Entities (Direct NER Test)
print("TEST 3: Entity Extraction with New Model")
print("-" * 70)

test_text = """
John Smith worked at Infosys as Senior Data Engineer in Hyderabad from Jan 2021 to Mar 2023.
Client was Google. He then joined Microsoft as Lead Engineer in Seattle from April 2023 to Present.

Education:
B.Tech in Computer Science from JNTU Hyderabad, 2015-2019, Grade 8.2
"""

try:
    response = requests.post(
        f"{API_URL}/extract-entities",
        json={"text": test_text}
    )
    
    if response.status_code == 200:
        result = response.json()
        entities = result.get('entities', [])
        
        print(f"✅ Extracted {len(entities)} entities:")
        print()
        
        # Group by entity type
        by_type = {}
        for entity in entities:
            entity_type = entity['entity']
            if entity_type not in by_type:
                by_type[entity_type] = []
            by_type[entity_type].append(entity)
        
        for entity_type, items in sorted(by_type.items()):
            print(f"  📌 {entity_type}:")
            for item in items:
                confidence = item['score']
                text = item['text']
                color = "🟢" if confidence >= 0.9 else "🟡" if confidence >= 0.7 else "🔴"
                print(f"     {color} {text:30s} | {confidence:.1%}")
            print()
        
        # Summary
        avg_confidence = sum(e['score'] for e in entities) / len(entities) if entities else 0
        high_conf = sum(1 for e in entities if e['score'] >= 0.9)
        
        print("-" * 70)
        print(f"📊 Summary:")
        print(f"   Total entities: {len(entities)}")
        print(f"   Average confidence: {avg_confidence:.1%}")
        print(f"   High confidence (≥90%): {high_conf} ({high_conf/len(entities)*100:.1f}%)")
        
    else:
        print(f"❌ Entity extraction failed: {response.status_code}")
        print(f"   Response: {response.text}")
        
except Exception as e:
    print(f"❌ Error during entity extraction: {e}")

print()
print("="*70)
print("✅ TESTING COMPLETE")
print("="*70)
print()
print("💡 Your new trained model is working in the API!")
print("   You can now use the API endpoints to parse resumes.")
print()
print("📝 Available endpoints:")
print("   GET  /health          - Check server health")
print("   GET  /model-info      - Get model information")
print("   POST /extract-entities - Extract entities from text")
print("   POST /parse           - Parse a resume file")
print()
