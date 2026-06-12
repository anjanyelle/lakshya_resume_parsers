#!/usr/bin/env python3
"""
Debug script to see raw model outputs.
"""

from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline
import torch
from pathlib import Path

MODEL_PATH = Path("models/resume-ner-deberta")

print("="*60)
print("🔍 Debugging Custom Model Outputs")
print("="*60)

print(f"\n📂 Loading model from: {MODEL_PATH}")
tokenizer = AutoTokenizer.from_pretrained(str(MODEL_PATH))
model = AutoModelForTokenClassification.from_pretrained(str(MODEL_PATH))

print(f"✅ Model loaded successfully!")
print(f"📊 Number of labels: {model.config.num_labels}")
print(f"🏷️  Label mapping: {model.config.id2label}")

device = 0 if torch.cuda.is_available() else -1
ner_pipeline = pipeline(
    "ner",
    model=model,
    tokenizer=tokenizer,
    aggregation_strategy="simple",
    device=device,
)

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

print("\n" + "="*60)
print("🧪 Testing with sample resume text")
print("="*60)

results = ner_pipeline(sample_text)

print(f"\n📊 Found {len(results)} entities:")
print("="*60)

for i, ent in enumerate(results, 1):
    print(f"{i}. Word: '{ent.get('word')}' | Label: {ent.get('entity_group')} | Score: {ent.get('score'):.3f}")

print("\n" + "="*60)
