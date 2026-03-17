#!/usr/bin/env python3
"""
Train custom models for resume parsing
"""

import os
import json
import spacy
from spacy.training import Example
import random
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
import psycopg2
from psycopg2.extras import Json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def collect_training_data():
    """Collect training data from successful parsing results"""
    
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL environment variable not found")
        print("📋 Please set DATABASE_URL or load from .env file")
        return [], []
    
    if database_url.startswith("postgresql+psycopg2://"):
        database_url = database_url.replace("postgresql+psycopg2://", "postgresql://")
    
    conn = psycopg2.connect(database_url)
    cursor = conn.cursor()
    
    # Get successful parsing results
    cursor.execute("""
        SELECT id, raw_text, parsed_data 
        FROM parsing_jobs 
        WHERE parsed_data->'work' IS NOT NULL
        AND jsonb_array_length(parsed_data->'work') > 0
        ORDER BY id DESC
        LIMIT 100
    """)
    
    training_samples = []
    labeled_data = []
    
    for job_id, raw_text, parsed_data in cursor.fetchall():
        if parsed_data and parsed_data.get("work"):
            for work_entry in parsed_data["work"]:
                # Create training sample for ML
                training_samples.append({
                    "resume_text": raw_text,
                    "company": work_entry.get("company"),
                    "title": work_entry.get("jobTitle"),
                    "start_date": work_entry.get("startDate"),
                    "end_date": work_entry.get("endDate"),
                    "location": work_entry.get("location")
                })
                
                # Create labeled data for NER
                company = work_entry.get("company", "")
                title = work_entry.get("jobTitle", "")
                location = work_entry.get("location", "")
                
                if company and title and raw_text:
                    # Find entities in text
                    entities = []
                    
                    # Find company
                    company_start = raw_text.find(company)
                    if company_start != -1:
                        entities.append({
                            "start": company_start,
                            "end": company_start + len(company),
                            "label": "COMPANY",
                            "text": company
                        })
                    
                    # Find title
                    title_start = raw_text.find(title)
                    if title_start != -1:
                        entities.append({
                            "start": title_start,
                            "end": title_start + len(title),
                            "label": "TITLE", 
                            "text": title
                        })
                    
                    # Find location
                    if location:
                        location_start = raw_text.find(location)
                        if location_start != -1:
                            entities.append({
                                "start": location_start,
                                "end": location_start + len(location),
                                "label": "LOCATION",
                                "text": location
                            })
                    
                    if entities:
                        # Convert entities to spaCy format
                        spacy_entities = []
                        for entity in entities:
                            spacy_entities.append((
                                entity["start"],
                                entity["end"],
                                entity["label"]
                            ))
                        
                        labeled_data.append({
                            "text": raw_text,
                            "entities": spacy_entities
                        })
    
    conn.close()
    
    print(f"✅ Collected {len(training_samples)} training samples")
    print(f"✅ Collected {len(labeled_data)} labeled NER samples")
    
    return training_samples, labeled_data

def train_ner_model(labeled_data):
    """Train custom NER model"""
    print("🤖 Training custom NER model...")
    
    # Create blank model
    nlp = spacy.blank("en")
    
    # Add NER pipeline
    if "ner" not in nlp.pipe_names:
        ner = nlp.add_pipe("ner")
    else:
        ner = nlp.get_pipe("ner")
    
    # Add labels
    labels = set()
    for item in labeled_data:
        for entity in item["entities"]:
            # entity is now a tuple (start, end, label)
            labels.add(entity[2])
    
    for label in labels:
        ner.add_label(label)
    
    # Train model
    optimizer = nlp.initialize()
    
    for i in range(100):
        random.shuffle(labeled_data)
        losses = {}
        
        # Create batches
        batches = spacy.util.minibatch(labeled_data, size=8)
        for batch in batches:
            examples = []
            for item in batch:
                doc = nlp.make_doc(item["text"])
                example = Example.from_dict(doc, item)
                examples.append(example)
            
            nlp.update(examples, sgd=optimizer, losses=losses)
        
        if i % 10 == 0:
            print(f"  Iteration {i}, Losses: {losses}")
    
    # Save model
    model_path = "custom_ner_model"
    nlp.to_disk(model_path)
    print(f"✅ NER model saved to {model_path}")
    
    return model_path

def train_quality_classifier(training_samples):
    """Train quality classifier for validation"""
    print("🔍 Training quality classifier...")
    
    # Create training data for quality assessment
    quality_data = []
    
    for sample in training_samples:
        # Positive examples (good data)
        if sample["company"] and sample["title"]:
            quality_data.append({
                "text": sample["company"],
                "label": 1,
                "type": "company"
            })
            quality_data.append({
                "text": sample["title"],
                "label": 1,
                "type": "title"
            })
        
        # Negative examples (bad patterns)
        if len(sample.get("company", "")) > 50:  # Probably description
            quality_data.append({
                "text": sample["company"],
                "label": 0,
                "type": "company"
            })
    
    if len(quality_data) < 10:
        print("❌ Not enough quality data for training")
        return None
    
    # Train classifier
    texts = [item["text"] for item in quality_data]
    labels = [item["label"] for item in quality_data]
    
    vectorizer = TfidfVectorizer(max_features=1000)
    X = vectorizer.fit_transform(texts)
    
    classifier = RandomForestClassifier(n_estimators=100, random_state=42)
    classifier.fit(X, labels)
    
    # Save classifier
    import joblib
    classifier_path = "quality_classifier.pkl"
    vectorizer_path = "tfidf_vectorizer.pkl"
    
    joblib.dump(classifier, classifier_path)
    joblib.dump(vectorizer, vectorizer_path)
    
    print(f"✅ Quality classifier saved to {classifier_path}")
    print(f"✅ Vectorizer saved to {vectorizer_path}")
    
    return classifier_path, vectorizer_path

def main():
    print("🎯 Starting custom model training...")
    
    # Collect training data
    training_samples, labeled_data = collect_training_data()
    
    if len(labeled_data) == 0:
        print("❌ No labeled data found for training")
        return
    
    # Train NER model
    ner_model_path = train_ner_model(labeled_data)
    
    # Train quality classifier
    quality_result = train_quality_classifier(training_samples)
    
    print("🎉 Training completed!")
    print(f"📁 NER Model: {ner_model_path}")
    if quality_result:
        print(f"📁 Quality Classifier: {quality_result[0]}")
        print(f"📁 Vectorizer: {quality_result[1]}")

if __name__ == "__main__":
    main()
