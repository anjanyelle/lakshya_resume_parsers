#!/usr/bin/env python3
"""
Fix training data conflicts in NER models
"""

import os
import json
import spacy
from spacy.training import Example
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def clean_overlapping_entities(entities):
    """Clean overlapping entities in training data"""
    # Sort entities by start position
    entities = sorted(entities, key=lambda x: x[0])
    
    cleaned = []
    i = 0
    while i < len(entities):
        current = entities[i]
        start, end, label = current
        
        # Check if this entity overlaps with next ones
        j = i + 1
        while j < len(entities):
            next_entity = entities[j]
            next_start, next_end, next_label = next_entity
            
            # Check for overlap
            if not (end <= next_start or next_end <= start):
                # Overlap detected - keep the longer one
                if (end - start) >= (next_end - next_start):
                    # Keep current, skip next
                    entities.pop(j)
                else:
                    # Keep next, skip current
                    entities.pop(i)
                    i -= 1
                    break
            else:
                j += 1
        i += 1
    
    return entities

def collect_and_clean_training_data():
    """Collect and clean training data"""
    
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL not found")
        return {}
    
    if database_url.startswith("postgresql+psycopg2://"):
        database_url = database_url.replace("postgresql+psycopg2://", "postgresql://")
    
    conn = psycopg2.connect(database_url)
    cursor = conn.cursor()
    
    # Get parsing results
    cursor.execute("""
        SELECT id, raw_text, parsed_data 
        FROM parsing_jobs 
        WHERE parsed_data IS NOT NULL
        ORDER BY id DESC
        LIMIT 50
    """)
    
    section_data = {
        "work": [],
        "education": [],
        "skills": [],
        "certifications": []
    }
    
    for row in cursor.fetchall():
        job_id, raw_text, parsed_data = row
        
        if not parsed_data:
            continue
            
        try:
            parsed = json.loads(parsed_data) if isinstance(parsed_data, str) else parsed_data
            
            # Extract work data
            if 'work_history' in parsed and parsed['work_history']:
                for item in parsed['work_history']:
                    if isinstance(item, dict):
                        entities = []
                        if item.get('company'):
                            entities.append((0, len(item['company']), "COMPANY"))
                        if item.get('title'):
                            entities.append((0, len(item['title']), "TITLE"))
                        
                        # Clean overlapping entities
                        entities = clean_overlapping_entities(entities)
                        
                        section_data["work"].append({
                            "raw_text": f"{item.get('company', '')} {item.get('title', '')}",
                            "section_data": entities
                        })
            
            # Extract education data
            if 'education' in parsed and parsed['education']:
                for item in parsed['education']:
                    if isinstance(item, dict):
                        entities = []
                        if item.get('university'):
                            entities.append((0, len(item['university']), "UNIVERSITY"))
                        if item.get('degree'):
                            entities.append((0, len(item['degree']), "DEGREE"))
                        
                        # Clean overlapping entities
                        entities = clean_overlapping_entities(entities)
                        
                        section_data["education"].append({
                            "raw_text": f"{item.get('university', '')} {item.get('degree', '')}",
                            "section_data": entities
                        })
                        
        except Exception as e:
            print(f"⚠️ Error processing job {job_id}: {e}")
            continue
    
    conn.close()
    return section_data

def train_clean_ner_model(section_name, training_data):
    """Train NER model with cleaned data"""
    print(f"🤖 Training clean NER model for {section_name}...")
    
    # Create blank spaCy model
    nlp = spacy.blank("en")
    
    # Add NER pipeline
    if "ner" not in nlp.pipe_names:
        nlp.add_pipe("ner")
    
    # Get NER component
    ner = nlp.get_pipe("ner")
    
    # Add labels
    entity_labels = []
    for item in training_data:
        for entity in item["section_data"]:
            if entity[2] not in entity_labels:
                entity_labels.append(entity[2])
    
    for label in entity_labels:
        ner.add_label(label)
    
    print(f"  📋 Labels: {entity_labels}")
    print(f"  📊 Training samples: {len(training_data)}")
    
    # Create training examples
    training_examples = []
    for item in training_data:
        doc = nlp.make_doc(item["raw_text"])
        example = Example.from_dict(doc, {"entities": item["section_data"]})
        training_examples.append(example)
    
    # Train model
    nlp.begin_training()
    for iteration in range(30):
        nlp.update(training_examples)
    nlp.end_training()
    
    # Save model
    model_path = f"clean_{section_name}_ner_model"
    nlp.to_disk(model_path)
    print(f"  ✅ Clean {section_name} model saved to {model_path}")
    
    return model_path

def main():
    print("🔧 FIXING TRAINING CONFLICTS...")
    
    # Collect and clean training data
    section_data = collect_and_clean_training_data()
    
    print(f"\n📊 Clean Data Statistics:")
    for section, data in section_data.items():
        print(f"  ✅ {section}: {len(data)} cleaned samples")
    
    # Train clean models
    clean_models = {}
    for section_name, training_data in section_data.items():
        if training_data:  # Only train if we have data
            model_path = train_clean_ner_model(section_name, training_data)
            clean_models[section_name] = model_path
    
    print(f"\n🎉 CLEAN MODELS TRAINED!")
    print(f"📁 Models: {list(clean_models.keys())}")

if __name__ == "__main__":
    main()
