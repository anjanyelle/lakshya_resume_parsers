#!/usr/bin/env python3
"""
Train models for ALL resume sections
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

def collect_all_section_data():
    """Collect training data for ALL resume sections"""
    
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL not found")
        return {}
    
    if database_url.startswith("postgresql+psycopg2://"):
        database_url = database_url.replace("postgresql+psycopg2://", "postgresql://")
    
    conn = psycopg2.connect(database_url)
    cursor = conn.cursor()
    
    # Get ALL parsing results
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
        "projects": [],
        "certifications": [],
        "achievements": [],
        "volunteer": [],
        "publications": [],
        "awards": [],
        "hobbies": [],
        "languages": [],
        "references": []
    }
    
    for job_id, raw_text, parsed_data in cursor.fetchall():
        if parsed_data:
            # Collect data for each section
            for section in section_data.keys():
                if section in parsed_data:
                    section_data[section].append({
                        "raw_text": raw_text,
                        "section_data": parsed_data[section]
                    })
    
    conn.close()
    
    # Print statistics
    print("📊 Section Data Statistics:")
    for section, data in section_data.items():
        print(f"  ✅ {section}: {len(data)} samples")
    
    return section_data

def train_section_ner_models(section_data):
    """Train NER models for each section"""
    
    section_models = {}
    
    # Define entities for each section
    section_entities = {
        "work": ["COMPANY", "TITLE", "LOCATION", "DATE_RANGE"],
        "education": ["UNIVERSITY", "DEGREE", "MAJOR", "EDU_DATE", "GPA"],
        "skills": ["SKILL", "TECHNOLOGY", "TOOL", "FRAMEWORK"],
        "projects": ["PROJECT_NAME", "PROJECT_ROLE", "PROJECT_TECH", "PROJECT_DATE"],
        "certifications": ["CERT_NAME", "CERT_INSTITUTION", "CERT_DATE"],
        "achievements": ["ACHIEVEMENT", "AWARD_NAME", "ACHIEVEMENT_DATE"],
        "volunteer": ["VOLUNTEER_ORG", "VOLUNTEER_ROLE", "VOLUNTEER_DATE"],
        "publications": ["PUBLICATION_TITLE", "PUBLICATION_JOURNAL", "PUBLICATION_DATE"],
        "awards": ["AWARD_NAME", "AWARD_ORG", "AWARD_DATE"],
        "hobbies": ["HOBBY", "INTEREST"],
        "languages": ["LANGUAGE", "PROFICIENCY"],
        "references": ["REFERENCE_NAME", "REFERENCE_TITLE", "REFERENCE_CONTACT"]
    }
    
    for section, entities in section_entities.items():
        if section_data[section]:
            print(f"\n🤖 Training NER model for {section} section...")
            
            # Create training data for this section
            labeled_data = create_section_training_data(section_data[section], entities)
            
            if len(labeled_data) >= 5:  # Minimum samples for training
                model = train_single_ner_model(labeled_data, entities, section)
                section_models[section] = model
                print(f"✅ {section} NER model trained")
            else:
                print(f"❌ Insufficient data for {section} section ({len(labeled_data)} samples)")
    
    return section_models

def create_section_training_data(section_samples, entity_types):
    """Create training data for a specific section"""
    
    labeled_data = []
    
    for sample in section_samples:
        raw_text = sample["raw_text"]
        section_content = sample["section_data"]
        
        entities = []
        
        # Extract entities based on section type
        if isinstance(section_content, list):
            for item in section_content:
                if isinstance(item, dict):
                    # Extract entities from dictionary
                    for key, value in item.items():
                        if value and str(value).strip():
                            entity_type = map_key_to_entity_type(key, entity_types)
                            if entity_type:
                                start = raw_text.find(str(value))
                                if start != -1:
                                    entities.append((start, start + len(str(value)), entity_type))
        
        labeled_data.append({
            "text": raw_text,
            "entities": entities
        })
    
    return labeled_data

def map_key_to_entity_type(key, entity_types):
    """Map dictionary keys to entity types"""
    
    key_mapping = {
        # Work section
        "company": "COMPANY",
        "jobTitle": "TITLE",
        "title": "TITLE",
        "location": "LOCATION",
        "startDate": "DATE_RANGE",
        "endDate": "DATE_RANGE",
        
        # Education section
        "university": "UNIVERSITY",
        "degree": "DEGREE",
        "major": "MAJOR",
        "graduationDate": "EDU_DATE",
        "gpa": "GPA",
        
        # Skills section
        "skill": "SKILL",
        "technology": "TECHNOLOGY",
        "tool": "TOOL",
        "framework": "FRAMEWORK",
        
        # Projects section
        "projectName": "PROJECT_NAME",
        "projectRole": "PROJECT_ROLE",
        "projectTech": "PROJECT_TECH",
        "projectDate": "PROJECT_DATE",
        
        # Certifications section
        "certificationName": "CERT_NAME",
        "institution": "CERT_INSTITUTION",
        "certificationDate": "CERT_DATE",
        
        # Achievements section
        "achievement": "ACHIEVEMENT",
        "awardName": "AWARD_NAME",
        "achievementDate": "ACHIEVEMENT_DATE",
        
        # Volunteer section
        "organization": "VOLUNTEER_ORG",
        "volunteerRole": "VOLUNTEER_ROLE",
        "volunteerDate": "VOLUNTEER_DATE",
        
        # Publications section
        "title": "PUBLICATION_TITLE",
        "journal": "PUBLICATION_JOURNAL",
        "publicationDate": "PUBLICATION_DATE",
        
        # Awards section
        "awardName": "AWARD_NAME",
        "awardOrg": "AWARD_ORG",
        "awardDate": "AWARD_DATE",
        
        # Hobbies section
        "hobby": "HOBBY",
        "interest": "INTEREST",
        
        # Languages section
        "language": "LANGUAGE",
        "proficiency": "PROFICIENCY",
        
        # References section
        "referenceName": "REFERENCE_NAME",
        "referenceTitle": "REFERENCE_TITLE",
        "referenceContact": "REFERENCE_CONTACT"
    }
    
    return key_mapping.get(key)

def train_single_ner_model(labeled_data, entity_types, section_name):
    """Train NER model for a single section"""
    
    nlp = spacy.blank("en")
    
    if "ner" not in nlp.pipe_names:
        ner = nlp.add_pipe("ner")
    else:
        ner = nlp.get_pipe("ner")
    
    # Add entity labels
    for entity_type in entity_types:
        ner.add_label(entity_type)
    
    # Train model
    optimizer = nlp.initialize()
    
    for i in range(100):
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
    
    # Save model
    model_path = f"{section_name}_ner_model"
    nlp.to_disk(model_path)
    print(f"  ✅ {section_name} model saved to {model_path}")
    
    return model_path

def add_synthetic_section_data(section_data):
    """Add synthetic data for sections with insufficient samples"""
    
    synthetic_data = {
        "education": [
            {"university": "Stanford University", "degree": "Bachelor of Science", "major": "Computer Science"},
            {"university": "MIT", "degree": "Master of Science", "major": "Data Science"},
            {"university": "UC Berkeley", "degree": "PhD", "major": "Artificial Intelligence"},
        ],
        "skills": [
            {"skill": "Python", "technology": "Programming Language"},
            {"skill": "React", "technology": "Frontend Framework"},
            {"skill": "AWS", "technology": "Cloud Platform"},
        ],
        "projects": [
            {"projectName": "E-commerce Platform", "projectTech": "React, Node.js"},
            {"projectName": "Data Analytics Dashboard", "projectTech": "Python, TensorFlow"},
            {"projectName": "Mobile Banking App", "projectTech": "React Native"},
        ],
        "certifications": [
            {"certificationName": "AWS Certified Solutions Architect", "institution": "Amazon"},
            {"certificationName": "Google Cloud Professional", "institution": "Google"},
            {"certificationName": "Microsoft Azure Developer", "institution": "Microsoft"},
        ]
    }
    
    # Add synthetic data to sections with insufficient samples
    for section, data in synthetic_data.items():
        if len(section_data[section]) < 10:
            for item in data:
                synthetic_text = create_synthetic_resume_text(section, item)
                section_data[section].append({
                    "raw_text": synthetic_text,
                    "section_data": [item]
                })
            print(f"  ✅ Added {len(data)} synthetic samples to {section}")
    
    return section_data

def create_synthetic_resume_text(section, item):
    """Create synthetic resume text for a section"""
    
    templates = {
        "education": """
EDUCATION
{university} - {degree} in {major}
Graduated: 2020
GPA: 3.8
        """,
        "skills": """
TECHNICAL SKILLS
• {skill} - {technology}
• {skill} - Expert level
• {skill} - 3 years experience
        """,
        "projects": """
PROJECTS
{projectName}
Technologies: {projectTech}
Description: Led development of enterprise application
        """,
        "certifications": """
CERTIFICATIONS
{certificationName}
Issued by: {institution}
Valid until: 2025
        """
    }
    
    template = templates.get(section, "{item}")
    return template.format(**item)

def main():
    print("🎯 Starting ALL SECTIONS training...")
    
    # Collect data for all sections
    section_data = collect_all_section_data()
    
    # Add synthetic data for sections with insufficient samples
    section_data = add_synthetic_section_data(section_data)
    
    # Train NER models for all sections
    section_models = train_section_ner_models(section_data)
    
    print("\n🎉 ALL SECTIONS training completed!")
    print(f"📁 Models trained: {list(section_models.keys())}")
    
    # Create summary
    total_samples = sum(len(data) for data in section_data.values())
    print(f"📊 Total training samples: {total_samples}")

if __name__ == "__main__":
    main()
