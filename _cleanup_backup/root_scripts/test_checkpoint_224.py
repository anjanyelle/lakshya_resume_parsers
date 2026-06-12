#!/usr/bin/env python3
"""
Test checkpoint-224 specifically.
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

def test_checkpoint_224():
    """Test the best checkpoint (224)."""
    
    model_path = "./models/resume-ner-final/checkpoint-224"
    
    # Change to the parent directory first
    os.chdir(str(parent_dir))
    
    try:
        print("🧪 TESTING CHECKPOINT-224 (BEST MODEL)")
        print("=" * 50)
        
        # Load model
        tokenizer = AutoTokenizer.from_pretrained(model_path, local_files_only=True)
        model = AutoModelForTokenClassification.from_pretrained(model_path, local_files_only=True)
        
        with open(f"{model_path}/label_mappings.json", 'r') as f:
            mappings = json.load(f)
        
        id_to_label = {int(k): v for k, v in mappings['id_to_label'].items()}
        
        print("✅ Model loaded successfully!")
        
        # Test with simple text
        text = "Senior Java Developer at Infosys"
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
                if label != 'O':
                    print(f"  {display_token:<15} -> {label} ⭐")
                    entities_found.append((display_token, label))
                else:
                    print(f"  {display_token:<15} -> {label}")
        
        print(f"\n🎯 ENTITIES FOUND: {len(entities_found)}")
        return len(entities_found) > 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_checkpoint_224()
    if success:
        print("\n🎉 Checkpoint-224 is working!")
    else:
        print("\n💥 Checkpoint-224 also failed!")
