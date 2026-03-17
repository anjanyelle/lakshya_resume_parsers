#!/usr/bin/env python3
"""
Train Skills NER Model using spaCy and CSV training data
"""

import spacy
import pandas as pd
import json
import random
from pathlib import Path
from spacy.training import Example
from spacy.tokens import DocBin
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_training_data():
    """Load skills data from CSV and convert to spaCy training format"""
    try:
        # Load skills CSV
        skills_df = pd.read_csv('data/external/skills.csv')
        
        training_data = []
        
        # Create training examples from skills
        for _, row in skills_df.iterrows():
            skill_name = str(row['skill_name']).strip()
            category = str(row.get('category', 'Technical')).strip()
            
            if skill_name and skill_name != 'nan':
                # Create simple training sentences
                sentences = [
                    f"I have experience with {skill_name}.",
                    f"My skills include {skill_name} and other technologies.",
                    f"I am proficient in {skill_name}.",
                    f"Technical skills: {skill_name}, Python, JavaScript.",
                    f"Experience with {skill_name} for 3 years."
                ]
                
                for sentence in sentences:
                    # Find the skill in the sentence
                    start = sentence.lower().find(skill_name.lower())
                    if start != -1:
                        end = start + len(skill_name)
                        entities = [(start, end, "SKILL")]
                        training_data.append((sentence, {"entities": entities}))
        
        logger.info(f"Created {len(training_data)} training examples")
        return training_data
        
    except Exception as e:
        logger.error(f"Error loading training data: {e}")
        return []

def create_ner_model():
    """Create and train a spaCy NER model for skills"""
    try:
        # Load base model
        logger.info("Loading base spaCy model...")
        nlp = spacy.load("en_core_web_sm")
        
        # Get the NER component
        if "ner" not in nlp.pipe_names:
            ner = nlp.add_pipe("ner")
        else:
            ner = nlp.get_pipe("ner")
        
        # Add SKILL label
        ner.add_label("SKILL")
        
        # Load training data
        training_data = load_training_data()
        
        if not training_data:
            logger.error("No training data available")
            return False
        
        # Convert training data to DocBin format
        doc_bin = DocBin()
        for text, annotations in training_data:
            doc = nlp.make_doc(text)
            example = Example.from_dict(doc, annotations)
            doc_bin.add(example.reference)
        
        # Split data
        train_data = []
        for doc in doc_bin.get_docs(nlp.vocab):
            train_data.append(doc)
        
        # Reserve some data for testing
        split_idx = int(len(train_data) * 0.8)
        train_docs = train_data[:split_idx]
        test_docs = train_data[split_idx:]
        
        logger.info(f"Training on {len(train_docs)} examples, testing on {len(test_docs)}")
        
        # Training
        optimizer = nlp.initialize()
        
        for epoch in range(10):  # 10 epochs
            random.shuffle(train_docs)
            losses = {}
            
            for doc in train_docs:
                example = Example.from_dict(doc, {"entities": []})
                nlp.update([example], losses=losses, sgd=optimizer)
            
            logger.info(f"Epoch {epoch + 1}, Loss: {losses.get('ner', 0.0)}")
        
        # Test the model
        logger.info("Testing model...")
        test_text = "I have experience with Python, JavaScript, React, and Node.js."
        doc = nlp(test_text)
        entities = [(ent.text, ent.label_) for ent in doc.ents]
        logger.info(f"Test result: {entities}")
        
        # Save the model
        output_dir = Path("data/models/skills_ner_trained")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        nlp.to_disk(output_dir)
        logger.info(f"Model saved to {output_dir}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error training model: {e}")
        return False

def main():
    """Main training function"""
    logger.info("Starting Skills NER Model Training")
    
    # Check if skills CSV exists
    if not Path("data/external/skills.csv").exists():
        logger.error("skills.csv not found in data/external/")
        logger.info("Please ensure your skills CSV file exists")
        return
    
    # Create the model
    success = create_ner_model()
    
    if success:
        logger.info("✅ Skills NER model training completed successfully!")
        logger.info("Model saved to: data/models/skills_ner_trained")
        logger.info("Restart your server to use the new model")
    else:
        logger.error("❌ Model training failed")

if __name__ == "__main__":
    main()
