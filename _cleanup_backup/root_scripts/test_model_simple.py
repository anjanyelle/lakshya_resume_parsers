#!/usr/bin/env python3
"""
Simple test of DeBERTa model using relative paths.
"""

import torch
import sys
import os
from pathlib import Path

# Add the parent directory to path
parent_dir = Path(__file__).parent
sys.path.append(str(parent_dir))

from transformers import AutoTokenizer, AutoModelForTokenClassification
import json

def test_model_directly():
    """Test model with proper path handling."""
    
    # Use relative path to avoid spaces issue
    model_path = "./models/resume-ner-final"
    
    print("🔍 TESTING DEBERTA MODEL DIRECTLY")
    print("=" * 50)
    
    # Change to the parent directory first
    os.chdir(str(parent_dir))
    
    if not os.path.exists(model_path):
        print(f"❌ Model path not found: {model_path}")
        return False
    
    try:
        # Load tokenizer and model
        print("📥 Loading tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained(model_path, local_files_only=True)
        
        print("🤖 Loading model...")
        model = AutoModelForTokenClassification.from_pretrained(model_path, local_files_only=True)
        
        print("✅ Model loaded successfully!")
        
        # Load label mappings
        with open(f"{model_path}/label_mappings.json", 'r') as f:
            mappings = json.load(f)
        
        id_to_label = {int(k): v for k, v in mappings['id_to_label'].items()}
        print(f"✅ Labels loaded: {len(id_to_label)}")
        
        # Test with simple text
        text = "Senior Java Developer at Infosys, Hyderabad"
        print(f"\n📝 Testing: '{text}'")
        
        # Tokenize
        inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
        
        # Get predictions
        with torch.no_grad():
            outputs = model(**inputs)
        
        predictions = torch.argmax(outputs.logits, dim=2)
        tokens = tokenizer.convert_ids_to_tokens(inputs["input_ids"][0])
        predicted_labels = [id_to_label[int(label_id)] for label_id in predictions[0]]
        
        print("\n🔍 TOKENS AND PREDICTIONS:")
        print("-" * 40)
        
        entities_found = []
        for token, label in zip(tokens, predicted_labels):
            if token not in ['[CLS]', '[SEP]', '[PAD]']:
                display_token = token.replace('##', '')
                print(f"{display_token:<15} -> {label}")
                if label != 'O':
                    entities_found.append((display_token, label))
        
        print(f"\n🎯 ENTITIES FOUND: {len(entities_found)}")
        for token, label in entities_found:
            print(f"  {token} -> {label}")
        
        return len(entities_found) > 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_model_directly()
    if success:
        print("\n🎉 Model is working!")
    else:
        print("\n💥 Model failed!")
