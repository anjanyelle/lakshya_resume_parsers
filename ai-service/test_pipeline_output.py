#!/usr/bin/env python3
"""Test pipeline aggregation output"""

from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline

model_path = "models/resume-ner-deberta"

print("Loading model...")
tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForTokenClassification.from_pretrained(model_path)

ner_pipeline = pipeline(
    "ner",
    model=model,
    tokenizer=tokenizer,
    aggregation_strategy="max",
    device=-1
)

test_text = "I worked as a Junior Full Stack Developer at Infosys Ltd"

print(f"\n📝 Input: {test_text}\n")
print("🔍 Pipeline predictions:\n")

predictions = ner_pipeline(test_text)

for i, pred in enumerate(predictions):
    print(f"{i+1}. Entity: {pred['entity_group']:<15} | Word: '{pred['word']:<30}' | Start: {pred['start']:<3} | End: {pred['end']:<3}")
    print(f"   Full text from positions: '{test_text[pred['start']:pred['end']]}'")
    print()
