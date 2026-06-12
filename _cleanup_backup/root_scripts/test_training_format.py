#!/usr/bin/env python3
"""
Test DeBERTa model with training-style text.
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

def test_with_training_format():
    """Test model with text similar to training data."""
    
    model_path = "./models/resume-ner-final"
    
    # Change to the parent directory first
    os.chdir(str(parent_dir))
    
    try:
        # Load model
        tokenizer = AutoTokenizer.from_pretrained(model_path, local_files_only=True)
        model = AutoModelForTokenClassification.from_pretrained(model_path, local_files_only=True)
        
        with open(f"{model_path}/label_mappings.json", 'r') as f:
            mappings = json.load(f)
        
        id_to_label = {int(k): v for k, v in mappings['id_to_label'].items()}
        
        # Test with training-style text (similar to what model saw during training)
        test_texts = [
            "Joined Deloitte in April 2022 as Sr IT Consultant",
            "Senior Java Developer at Infosys, Hyderabad from Jan 2021 to Mar 2023",
            "B.Tech Computer Science, JNTU Hyderabad, 2016-2020",
            "Software Engineer at TCS, Bangalore (2019-2021)"
        ]
        
        print("🧪 TESTING WITH TRAINING-STYLE TEXT")
        print("=" * 50)
        
        for i, text in enumerate(test_texts, 1):
            print(f"\n📝 Test {i}: '{text}'")
            print("-" * 40)
            
            # Tokenize
            inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
            
            # Get predictions
            with torch.no_grad():
                outputs = model(**inputs)
            
            predictions = torch.argmax(outputs.logits, dim=2)
            tokens = tokenizer.convert_ids_to_tokens(inputs["input_ids"][0])
            predicted_labels = [id_to_label[int(label_id)] for label_id in predictions[0]]
            
            # Show predictions
            entities_found = []
            for token, label in zip(tokens, predicted_labels):
                if token not in ['[CLS]', '[SEP]', '[PAD]']:
                    display_token = token.replace('##', '')
                    if label != 'O':
                        print(f"  {display_token:<15} -> {label} ⭐")
                        entities_found.append((display_token, label))
                    else:
                        print(f"  {display_token:<15} -> {label}")
            
            print(f"🎯 Entities: {len(entities_found)}")
        
        # Test with individual tokens
        print(f"\n🔍 TESTING INDIVIDUAL TOKENS")
        print("-" * 40)
        
        test_tokens = ["Deloitte", "Infosys", "TCS", "Senior", "Java", "Developer", "Hyderabad", "Bangalore", "B.Tech", "Computer", "Science"]
        
        for token in test_tokens:
            inputs = tokenizer(token, return_tensors="pt", truncation=True, max_length=512)
            
            with torch.no_grad():
                outputs = model(**inputs)
            
            predictions = torch.argmax(outputs.logits, dim=2)
            predicted_labels = [id_to_label[int(label_id)] for label_id in predictions[0]]
            
            # Get the prediction for the actual token (not special tokens)
            if len(predicted_labels) >= 3:  # [CLS], token, [SEP]
                token_prediction = predicted_labels[1]  # The actual token
                if token_prediction != 'O':
                    print(f"  {token:<15} -> {token_prediction} ⭐")
                else:
                    print(f"  {token:<15} -> {token_prediction}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_with_training_format()
