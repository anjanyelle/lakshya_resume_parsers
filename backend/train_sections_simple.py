#!/usr/bin/env python3
"""
Simple training for all resume sections without entity overlap
"""

import os
import json
import spacy
from spacy.training import Example
import random
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def collect_section_data():
    """Collect training data from database"""
    
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL not found")
        return {}
    
    if database_url.startswith("postgresql+psycopg2://"):
        database_url = database_url.replace("postgresql+psycopg2://", "postgresql://")
    
    conn = psycopg2.connect(database_url)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, raw_text, parsed_data 
        FROM parsing_jobs 
        WHERE parsed_data IS NOT NULL
        ORDER BY id DESC
        LIMIT 50
    """)
    
    section_data = {}
    
    for job_id, raw_text, parsed_data in cursor.fetchall():
        if parsed_data:
            for section, data in parsed_data.items():
                if section not in section_data:
                    section_data[section] = []
                
                section_data[section].append({
                    "raw_text": raw_text,
                    "section_data": data
                })
    
    conn.close()
    
    print("📊 Section Data Statistics:")
    for section, data in section_data.items():
        print(f"  ✅ {section}: {len(data)} samples")
    
    return section_data

def create_simple_training_data():
    """Create simple training data without complex entities"""
    
    # Simple training examples for each section
    training_data = {
        "work": [
            {
                "text": "Aetna (CVS Health): September 2023 – Current (Location: Hartford, CT (Remote))\nRole: Senior Java Developer",
                "entities": [(0, 17, "COMPANY"), (80, 100, "TITLE")]
            },
            {
                "text": "Wells Fargo: July 2020 – August 2023 (Location: Charlotte, NC)\nRole: Senior Java Developer", 
                "entities": [(0, 11, "COMPANY"), (54, 74, "TITLE")]
            }
        ],
        "education": [
            {
                "text": "Stanford University\nBachelor of Science in Computer Science\nGraduated: 2020",
                "entities": [(0, 16, "UNIVERSITY"), (17, 37, "DEGREE"), (41, 58, "MAJOR")]
            },
            {
                "text": "MIT\nMaster of Science in Data Science\nGraduated: 2022",
                "entities": [(0, 3, "UNIVERSITY"), (4, 30, "DEGREE"), (34, 46, "MAJOR")]
            }
        ],
        "skills": [
            {
                "text": "Technical Skills\nPython - Expert\nReact - Advanced\nAWS - Intermediate",
                "entities": [(16, 22, "SKILL"), (25, 30, "SKILL"), (33, 36, "SKILL")]
            },
            {
                "text": "Skills\nJava, Spring Boot, React, PostgreSQL",
                "entities": [(7, 11, "SKILL"), (13, 23, "SKILL"), (25, 30, "SKILL")]
            }
        ],
        "projects": [
            {
                "text": "Projects\nE-commerce Platform\nTechnologies: React, Node.js, MongoDB",
                "entities": [(9, 26, "PROJECT_NAME"), (40, 65, "PROJECT_TECH")]
            },
            {
                "text": "Personal Projects\nData Analytics Dashboard\nTech Stack: Python, TensorFlow",
                "entities": [(18, 41, "PROJECT_NAME"), (53, 74, "PROJECT_TECH")]
            }
        ],
        "certifications": [
            {
                "text": "Certifications\nAWS Certified Solutions Architect\nIssued: 2023",
                "entities": [(14, 44, "CERT_NAME")]
            },
            {
                "text": "Professional Certifications\nGoogle Cloud Professional Developer\nIssued: 2022",
                "entities": [(24, 58, "CERT_NAME")]
            }
        ]
    }
    
    return training_data

def train_section_models(training_data):
    """Train NER models for each section"""
    
    section_models = {}
    
    for section, data in training_data.items():
        print(f"\n🤖 Training NER model for {section} section...")
        
        # Create blank model
        nlp = spacy.blank("en")
        
        if "ner" not in nlp.pipe_names:
            ner = nlp.add_pipe("ner")
        else:
            ner = nlp.get_pipe("ner")
        
        # Add unique labels
        labels = set()
        for item in data:
            for entity in item["entities"]:
                labels.add(entity[2])
        
        for label in labels:
            ner.add_label(label)
        
        # Train model
        optimizer = nlp.initialize()
        
        for i in range(50):  # Reduced iterations for stability
            random.shuffle(data)
            losses = {}
            
            batches = spacy.util.minibatch(data, size=2)
            for batch in batches:
                examples = []
                for item in batch:
                    doc = nlp.make_doc(item["text"])
                    try:
                        example = Example.from_dict(doc, item)
                        examples.append(example)
                    except Exception as e:
                        print(f"  ⚠️ Skipping problematic example: {e}")
                        continue
                
                if examples:
                    nlp.update(examples, sgd=optimizer, losses=losses)
            
            if i % 10 == 0:
                print(f"  Iteration {i}, Losses: {losses}")
        
        # Save model
        model_path = f"{section}_ner_model"
        nlp.to_disk(model_path)
        print(f"  ✅ {section} model saved to {model_path}")
        section_models[section] = model_path
    
    return section_models

def main():
    print("🎯 Starting SIMPLE ALL SECTIONS training...")
    
    # Create simple training data
    training_data = create_simple_training_data()
    
    # Train models for each section
    section_models = train_section_models(training_data)
    
    print("\n🎉 SIMPLE ALL SECTIONS training completed!")
    print(f"📁 Models trained: {list(section_models.keys())}")
    
    # Create model summary
    print("\n📊 Model Summary:")
    for section, model_path in section_models.items():
        print(f"  ✅ {section}: {model_path}")

if __name__ == "__main__":
    main()
