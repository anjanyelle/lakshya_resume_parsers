#!/usr/bin/env python3
"""
Debug script to test DeBERTa model directly and check predictions.
"""

import torch
import sys
import os
from pathlib import Path

# Add the parent directory to path
parent_dir = Path(__file__).parent.parent
sys.path.append(str(parent_dir))

from transformers import AutoTokenizer, AutoModelForTokenClassification
import json

def debug_deberta_model():
    """Debug DeBERTa model predictions."""
    
    model_path = str(parent_dir / "models" / "resume-ner-final")
    
    print("🔍 DEBUGGING DEBERTA MODEL")
    print("=" * 50)
    
    # Load tokenizer and model
    try:
        tokenizer = AutoTokenizer.from_pretrained(model_path)
        model = AutoModelForTokenClassification.from_pretrained(model_path)
        print("✅ Model and tokenizer loaded")
        
        # Load label mappings
        with open(f"{model_path}/label_mappings.json", 'r') as f:
            mappings = json.load(f)
        
        id_to_label = {int(k): v for k, v in mappings['id_to_label'].items()}
        print(f"✅ Label mappings loaded: {len(id_to_label)} labels")
        
        # Test text
        text = "Senior Java Developer at Infosys, Hyderabad from Jan 2021 to Mar 2023"
        print(f"\n📝 Test text: {text}")
        
        # Tokenize
        inputs = tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=512,
            padding=True
        )
        
        print(f"🔤 Tokenized input shape: {inputs['input_ids'].shape}")
        
        # Get predictions
        with torch.no_grad():
            outputs = model(**inputs)
        
        print(f"🤖 Output logits shape: {outputs.logits.shape}")
        
        # Get predicted labels
        predictions = torch.argmax(outputs.logits, dim=2)
        print(f"🏷️  Predictions shape: {predictions.shape}")
        
        # Convert tokens to labels
        tokens = tokenizer.convert_ids_to_tokens(inputs["input_ids"][0])
        predicted_labels = [id_to_label[int(label_id)] for label_id in predictions[0]]
        
        print(f"\n🔍 TOKEN-LEVEL ANALYSIS:")
        print("-" * 60)
        
        entity_count = 0
        for token, label in zip(tokens, predicted_labels):
            if token not in ['[CLS]', '[SEP]', '[PAD]']:
                print(f"{token:<15} -> {label}")
                if label != 'O':
                    entity_count += 1
        
        print(f"\n📊 ENTITIES FOUND: {entity_count}")
        
        # Group entities
        entities = {}
        current_entity = None
        current_tokens = []
        
        for token, label in zip(tokens, predicted_labels):
            if token in ['[CLS]', '[SEP]', '[PAD]']:
                continue
            
            if label.startswith('B-'):
                # Save previous entity if exists
                if current_entity and current_tokens:
                    entity_text = ' '.join(current_tokens).replace(' ##', '')
                    if current_entity not in entities:
                        entities[current_entity] = []
                    entities[current_entity].append(entity_text)
                
                # Start new entity
                current_entity = label[2:]  # Remove 'B-'
                current_tokens = [token]
            
            elif label.startswith('I-') and current_entity:
                # Continue current entity
                current_tokens.append(token)
            
            else:
                # Save current entity and reset
                if current_entity and current_tokens:
                    entity_text = ' '.join(current_tokens).replace(' ##', '')
                    if current_entity not in entities:
                        entities[current_entity] = []
                    entities[current_entity].append(entity_text)
                
                current_entity = None
                current_tokens = []
        
        # Save final entity
        if current_entity and current_tokens:
            entity_text = ' '.join(current_tokens).replace(' ##', '')
            if current_entity not in entities:
                entities[current_entity] = []
            entities[current_entity].append(entity_text)
        
        print(f"\n🎯 GROUPED ENTITIES:")
        print("-" * 40)
        for entity_type, entity_list in entities.items():
            print(f"{entity_type}: {entity_list}")
        
        return len(entities) > 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = debug_deberta_model()
    if success:
        print("\n🎉 Model is working correctly!")
    else:
        print("\n💥 Model has issues!")
