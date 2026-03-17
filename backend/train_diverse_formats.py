#!/usr/bin/env python3
"""
Train models on diverse resume formats
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

def collect_diverse_training_data():
    """Collect training data from various resume formats"""
    
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL not found")
        return [], []
    
    if database_url.startswith("postgresql+psycopg2://"):
        database_url = database_url.replace("postgresql+psycopg2://", "postgresql://")
    
    conn = psycopg2.connect(database_url)
    cursor = conn.cursor()
    
    # Get ALL parsing results for diverse formats
    cursor.execute("""
        SELECT id, raw_text, parsed_data 
        FROM parsing_jobs 
        WHERE parsed_data->'work' IS NOT NULL
        ORDER BY id DESC
        LIMIT 50
    """)
    
    training_samples = []
    labeled_data = []
    
    for job_id, raw_text, parsed_data in cursor.fetchall():
        if parsed_data and parsed_data.get("work"):
            for work_entry in parsed_data["work"]:
                # Create training sample
                training_samples.append({
                    "resume_text": raw_text,
                    "company": work_entry.get("company"),
                    "title": work_entry.get("jobTitle"),
                    "start_date": work_entry.get("startDate"),
                    "end_date": work_entry.get("endDate"),
                    "location": work_entry.get("location")
                })
                
                # Create NER training data with multiple patterns
                company = work_entry.get("company", "")
                title = work_entry.get("jobTitle", "")
                location = work_entry.get("location", "")
                
                if company and title and raw_text:
                    entities = []
                    
                    # Find company (multiple patterns)
                    company_patterns = [
                        company,  # Exact match
                        company.split(" (")[0] if " (" in company else company,  # Without location
                    ]
                    
                    for pattern in company_patterns:
                        start = raw_text.find(pattern)
                        if start != -1 and len(pattern) > 2:
                            entities.append((start, start + len(pattern), "COMPANY"))
                            break
                    
                    # Find title (multiple patterns)
                    title_patterns = [
                        title,  # Exact match
                        f"Role: {title}",  # With "Role:" prefix
                        f"Position: {title}",  # With "Position:" prefix
                    ]
                    
                    for pattern in title_patterns:
                        start = raw_text.find(pattern)
                        if start != -1 and len(pattern) > 2:
                            entities.append((start, start + len(pattern), "TITLE"))
                            break
                    
                    # Find location
                    if location:
                        location_patterns = [
                            location,  # Exact match
                            f"Location: {location}",  # With "Location:" prefix
                            f"({location})",  # In parentheses
                        ]
                        
                        for pattern in location_patterns:
                            start = raw_text.find(pattern)
                            if start != -1 and len(pattern) > 2:
                                entities.append((start, start + len(pattern), "LOCATION"))
                                break
                    
                    if entities:
                        labeled_data.append({
                            "text": raw_text,
                            "entities": entities
                        })
    
    conn.close()
    
    print(f"✅ Collected {len(training_samples)} training samples")
    print(f"✅ Collected {len(labeled_data)} labeled NER samples")
    
    return training_samples, labeled_data

def add_synthetic_training_data(training_samples, labeled_data):
    """Add synthetic examples for diverse formats"""
    
    synthetic_samples = []
    synthetic_labeled = []
    
    # Common company names
    companies = ["Google", "Microsoft", "Amazon", "Apple", "Meta", "Netflix", "Tesla"]
    titles = ["Software Engineer", "Senior Developer", "Lead Engineer", "Architect", "Manager"]
    locations = ["San Francisco, CA", "New York, NY", "Seattle, WA", "Austin, TX"]
    
    # Generate synthetic examples for different formats
    for i in range(50):  # Add 50 synthetic samples
        company = random.choice(companies)
        title = random.choice(titles)
        location = random.choice(locations)
        
        # Format 1: Company: Title | Date | Location
        format1_text = f"{company}: {title} | 2022-2023 | {location}"
        entities1 = [(0, len(company), "COMPANY"), (len(company) + 2, len(company) + 2 + len(title), "TITLE")]
        
        # Format 2: Title at Company (Location)
        format2_text = f"{title} at {company} ({location})"
        entities2 = [(0, len(title), "TITLE"), (len(title) + 4, len(title) + 4 + len(company), "COMPANY")]
        
        # Format 3: Vertical layout
        format3_text = f"{title}\n{company}\n{location}"
        entities3 = [(0, len(title), "TITLE"), (len(title) + 1, len(title) + 1 + len(company), "COMPANY")]
        
        # Add to training data
        synthetic_labeled.extend([
            {"text": format1_text, "entities": entities1},
            {"text": format2_text, "entities": entities2},
            {"text": format3_text, "entities": entities3}
        ])
        
        synthetic_samples.extend([
            {"company": company, "title": title, "location": location},
            {"company": company, "title": title, "location": location},
            {"company": company, "title": title, "location": location}
        ])
    
    print(f"✅ Added {len(synthetic_samples)} synthetic training samples")
    print(f"✅ Added {len(synthetic_labeled)} synthetic NER samples")
    
    return training_samples + synthetic_samples, labeled_data + synthetic_labeled

def train_enhanced_ner_model(labeled_data):
    """Train NER model with diverse formats"""
    print("🤖 Training enhanced NER model for diverse formats...")
    
    nlp = spacy.blank("en")
    
    if "ner" not in nlp.pipe_names:
        ner = nlp.add_pipe("ner")
    else:
        ner = nlp.get_pipe("ner")
    
    # Add labels
    labels = set()
    for item in labeled_data:
        for entity in item["entities"]:
            labels.add(entity[2])
    
    for label in labels:
        ner.add_label(label)
    
    # Train with more iterations for diverse patterns
    optimizer = nlp.initialize()
    
    for i in range(200):  # More iterations for diverse patterns
        random.shuffle(labeled_data)
        losses = {}
        
        batches = spacy.util.minibatch(labeled_data, size=8)
        for batch in batches:
            examples = []
            for item in batch:
                doc = nlp.make_doc(item["text"])
                example = Example.from_dict(doc, item)
                examples.append(example)
            
            nlp.update(examples, sgd=optimizer, losses=losses)
        
        if i % 20 == 0:
            print(f"  Iteration {i}, Losses: {losses}")
    
    # Save enhanced model
    model_path = "enhanced_ner_model"
    nlp.to_disk(model_path)
    print(f"✅ Enhanced NER model saved to {model_path}")
    
    return model_path

def main():
    print("🎯 Starting diverse format training...")
    
    # Collect real data
    real_samples, real_labeled = collect_diverse_training_data()
    
    # Add synthetic data for diverse formats
    all_samples, all_labeled = add_synthetic_training_data(real_samples, real_labeled)
    
    if len(all_labeled) == 0:
        print("❌ No training data available")
        return
    
    # Train enhanced NER model
    ner_model_path = train_enhanced_ner_model(all_labeled)
    
    print("🎉 Diverse format training completed!")
    print(f"📁 Enhanced NER Model: {ner_model_path}")
    print(f"📊 Total Training Samples: {len(all_samples)}")
    print(f"📊 Total NER Samples: {len(all_labeled)}")

if __name__ == "__main__":
    main()
