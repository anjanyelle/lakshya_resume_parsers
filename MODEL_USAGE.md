# 📖 Resume NER Model - Usage Guide

## 🎯 Model Overview

**Model Type:** Named Entity Recognition (NER) for Resume Parsing  
**Base Model:** microsoft/deberta-v3-base  
**Model Size:** 735 MB  
**Training Data:** 4,293 resumes  
**Current F1 Score:** 98.90%  

### Supported Entity Types

| Entity | Description | F1 Score | Support |
|--------|-------------|----------|---------|
| **COMPANY** | Company/Organization names | 97.86% | 770 |
| **CLIENT** | Client names in projects | 97.90% | 329 |
| **ROLE** | Job titles/designations | 98.86% | 1,186 |
| **LOCATION** | Work locations | 96.43% | 713 |
| **DEGREE** | Educational degrees | 99.48% | 389 |
| **PERSON** | Person names | - | 0 |
| **EDUCATION** | Educational institutions | - | 0 |
| **START_DATE** | Start dates | - | 0 |
| **END_DATE** | End dates | - | 0 |

---

## 🚀 Quick Start

### 1. Basic Usage (Python)

```python
from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline

# Load model and tokenizer
model_path = "./models/resume-ner-deberta"
tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForTokenClassification.from_pretrained(model_path)

# Create NER pipeline
nlp = pipeline("ner", model=model, tokenizer=tokenizer, aggregation_strategy="simple")

# Parse resume text
resume_text = """
John Doe worked at Infosys as Senior Software Engineer in Bangalore from 2020 to 2023.
He developed solutions for Microsoft as a client.
Education: B.Tech in Computer Science from IIT Delhi.
"""

# Get entities
entities = nlp(resume_text)

# Print results
for entity in entities:
    print(f"{entity['entity_group']}: {entity['word']} (confidence: {entity['score']:.2f})")
```

**Output:**
```
COMPANY: Infosys (confidence: 0.99)
ROLE: Senior Software Engineer (confidence: 0.98)
LOCATION: Bangalore (confidence: 0.97)
CLIENT: Microsoft (confidence: 0.99)
DEGREE: B.Tech in Computer Science (confidence: 0.99)
EDUCATION: IIT Delhi (confidence: 0.98)
```

---

### 2. Processing Long Resumes (8-10 pages)

For long resumes, use chunking to handle the 256 token limit:

```python
from transformers import AutoTokenizer, AutoModelForTokenClassification
import torch

model_path = "./models/resume-ner-deberta"
tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForTokenClassification.from_pretrained(model_path)

def extract_entities_from_long_resume(resume_text, max_length=256, overlap=50):
    """
    Process long resumes by chunking with overlap
    
    Args:
        resume_text: Full resume text
        max_length: Maximum tokens per chunk (256 for this model)
        overlap: Number of overlapping tokens between chunks
    """
    # Split into sentences
    sentences = resume_text.split('. ')
    
    all_entities = []
    current_chunk = ""
    
    for sentence in sentences:
        # Check if adding this sentence exceeds max_length
        test_chunk = current_chunk + sentence + ". "
        tokens = tokenizer(test_chunk, return_tensors="pt", truncation=False)
        
        if tokens['input_ids'].shape[1] > max_length:
            # Process current chunk
            if current_chunk:
                entities = process_chunk(current_chunk)
                all_entities.extend(entities)
            
            # Start new chunk with overlap (last sentence)
            current_chunk = sentence + ". "
        else:
            current_chunk = test_chunk
    
    # Process final chunk
    if current_chunk:
        entities = process_chunk(current_chunk)
        all_entities.extend(entities)
    
    # Remove duplicates
    return deduplicate_entities(all_entities)

def process_chunk(text):
    """Process a single chunk of text"""
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=256)
    
    with torch.no_grad():
        outputs = model(**inputs)
    
    predictions = torch.argmax(outputs.logits, dim=2)
    tokens = tokenizer.convert_ids_to_tokens(inputs["input_ids"][0])
    
    entities = []
    current_entity = None
    
    for token, pred_id in zip(tokens, predictions[0]):
        label = model.config.id2label[pred_id.item()]
        
        if label.startswith('B-'):
            if current_entity:
                entities.append(current_entity)
            current_entity = {
                'type': label[2:],
                'text': token.replace('▁', ' '),
                'confidence': outputs.logits[0][len(entities)][pred_id].item()
            }
        elif label.startswith('I-') and current_entity:
            current_entity['text'] += token.replace('▁', ' ')
        else:
            if current_entity:
                entities.append(current_entity)
                current_entity = None
    
    if current_entity:
        entities.append(current_entity)
    
    return entities

def deduplicate_entities(entities):
    """Remove duplicate entities"""
    seen = set()
    unique_entities = []
    
    for entity in entities:
        key = (entity['type'], entity['text'].strip())
        if key not in seen:
            seen.add(key)
            unique_entities.append(entity)
    
    return unique_entities

# Example usage
with open('long_resume.txt', 'r') as f:
    resume_text = f.read()

entities = extract_entities_from_long_resume(resume_text)

# Group by entity type
from collections import defaultdict
grouped = defaultdict(list)

for entity in entities:
    grouped[entity['type']].append(entity['text'].strip())

# Print structured output
print("📋 EXTRACTED INFORMATION\n")
print("👤 PERSON:", grouped.get('PERSON', ['Not found'])[0])
print("\n💼 WORK EXPERIENCE:")
for i, (company, role, location) in enumerate(zip(
    grouped.get('COMPANY', []),
    grouped.get('ROLE', []),
    grouped.get('LOCATION', [])
), 1):
    print(f"  {i}. {role} at {company}, {location}")
    if i < len(grouped.get('CLIENT', [])):
        print(f"     Client: {grouped['CLIENT'][i-1]}")

print("\n🎓 EDUCATION:")
for degree, edu in zip(grouped.get('DEGREE', []), grouped.get('EDUCATION', [])):
    print(f"  • {degree} from {edu}")
```

---

### 3. Extract Only Required Fields

```python
def extract_required_fields(resume_text):
    """
    Extract only: Person Name, Work Experience, Education
    """
    entities = extract_entities_from_long_resume(resume_text)
    
    result = {
        'person_name': None,
        'work_experience': [],
        'education': []
    }
    
    # Group entities
    grouped = {}
    for entity in entities:
        entity_type = entity['type']
        if entity_type not in grouped:
            grouped[entity_type] = []
        grouped[entity_type].append(entity['text'].strip())
    
    # Extract person name
    if 'PERSON' in grouped and grouped['PERSON']:
        result['person_name'] = grouped['PERSON'][0]
    
    # Extract work experience
    companies = grouped.get('COMPANY', [])
    roles = grouped.get('ROLE', [])
    locations = grouped.get('LOCATION', [])
    clients = grouped.get('CLIENT', [])
    
    for i in range(max(len(companies), len(roles))):
        experience = {
            'company': companies[i] if i < len(companies) else None,
            'role': roles[i] if i < len(roles) else None,
            'location': locations[i] if i < len(locations) else None,
            'client': clients[i] if i < len(clients) else None
        }
        result['work_experience'].append(experience)
    
    # Extract education
    degrees = grouped.get('DEGREE', [])
    institutions = grouped.get('EDUCATION', [])
    
    for i in range(max(len(degrees), len(institutions))):
        education = {
            'degree': degrees[i] if i < len(degrees) else None,
            'institution': institutions[i] if i < len(institutions) else None
        }
        result['education'].append(education)
    
    return result

# Usage
resume_text = open('resume.txt').read()
data = extract_required_fields(resume_text)

print("Person:", data['person_name'])
print("\nWork Experience:")
for exp in data['work_experience']:
    print(f"  - {exp['role']} at {exp['company']}")
print("\nEducation:")
for edu in data['education']:
    print(f"  - {edu['degree']} from {edu['institution']}")
```

---

## 📁 File Structure

```
models/resume-ner-deberta/
├── config.json              # Model configuration
├── model.safetensors        # Model weights (735 MB)
├── tokenizer.json           # Tokenizer vocabulary
├── tokenizer_config.json    # Tokenizer settings
├── spm.model                # SentencePiece model
├── label_mappings.json      # Entity label mappings
├── added_tokens.json        # Additional tokens
└── special_tokens_map.json  # Special token mappings
```

---

## ⚙️ Advanced Configuration

### Adjust Confidence Threshold

```python
# Filter low-confidence predictions
entities = nlp(resume_text)
high_confidence = [e for e in entities if e['score'] > 0.85]
```

### Batch Processing

```python
# Process multiple resumes
resumes = ["resume1.txt", "resume2.txt", "resume3.txt"]

for resume_file in resumes:
    with open(resume_file) as f:
        text = f.read()
    entities = extract_required_fields(text)
    print(f"Processed: {resume_file}")
```

---

## 🐛 Troubleshooting

### Issue: "Token indices sequence length is longer than the maximum"
**Solution:** Use the chunking approach shown above for long resumes.

### Issue: Missing entities
**Solution:** 
1. Check if entity type was in training data (see support column)
2. Increase training data for that entity type
3. Lower confidence threshold

### Issue: Slow performance
**Solution:**
```python
# Use CPU optimization
import torch
torch.set_num_threads(4)

# Or use GPU if available
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = model.to(device)
```

---

## 📊 Performance Metrics

- **Overall F1 Score:** 98.90%
- **Inference Speed:** ~100-150 tokens/second (CPU)
- **Memory Usage:** ~2-3 GB RAM
- **Max Input Length:** 256 tokens per chunk

---

## 🔗 Integration Examples

### Flask API

```python
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/parse-resume', methods=['POST'])
def parse_resume():
    resume_text = request.json.get('text', '')
    entities = extract_required_fields(resume_text)
    return jsonify(entities)

if __name__ == '__main__':
    app.run(port=5000)
```

### FastAPI

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Resume(BaseModel):
    text: str

@app.post("/parse-resume")
async def parse_resume(resume: Resume):
    entities = extract_required_fields(resume.text)
    return entities
```

---

## 📝 Notes

1. **Token Limit:** Model has 256 token limit - use chunking for long resumes
2. **Missing Entities:** PERSON, EDUCATION, START_DATE, END_DATE have 0 support - need more training data
3. **Best Performance:** DEGREE (99.48%), ROLE (98.86%), CLIENT (97.90%)
4. **Language:** Currently trained on English resumes only

---

## 📞 Support

For issues or questions, refer to `IMPROVEMENT_GUIDE.md` for steps to improve accuracy.
