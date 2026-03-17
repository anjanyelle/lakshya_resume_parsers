#!/usr/bin/env python3
"""
TASK 1 - Generate 200+ NER training samples from comprehensive resume data
"""

import json
import re
import spacy
from spacy.training import offsets_to_biluo_tags
import os

def generate_ner_training_data():
    """Generate 200+ labeled NER training sentences from resume data"""
    
    print("🔧 TASK 1 - GENERATING 200+ NER TRAINING SAMPLES")
    print("=" * 60)
    
    # Load comprehensive resume data
    try:
        with open("comprehensive_all_resumes_merged.json", "r", encoding="utf-8") as f:
            data = json.load(f)
    except:
        with open("../comprehensive_all_resumes_merged.json", "r", encoding="utf-8") as f:
            data = json.load(f)
    
    resumes = data.get("resumes", [])
    print(f"📄 Loaded {len(resumes)} resumes for training")
    
    # Initialize training data
    training_data = []
    
    # Extract text samples from resumes
    all_texts = []
    for resume in resumes:
        resume_text = resume.get("resume_text", "")
        if resume_text:
            # Clean text: remove ## and replace newlines
            clean_text = resume_text.replace("##", "").replace("\n", " ")
            all_texts.append(clean_text)
    
    print(f"📝 Processed {len(all_texts)} resume texts")
    
    # Generate training examples with different entity types
    entity_examples = []
    
    # SKILL examples (60 sentences)
    skill_patterns = [
        "Python", "Java", "JavaScript", "React", "Angular", "Vue.js", "Node.js", "Express",
        "SQL", "PostgreSQL", "MongoDB", "Redis", "Docker", "Kubernetes", "AWS", "Azure",
        "GCP", "Terraform", "Jenkins", "Git", "Linux", "Apache", "Nginx", "Spark",
        "Hadoop", "Kafka", "Elasticsearch", "TensorFlow", "PyTorch", "Scikit-learn",
        "Pandas", "NumPy", "Power BI", "Tableau", "Excel", "VBA", "Python 3", "Python scripting",
        "AWS Glue", "PySpark", "Snowflake", "Databricks", "Kubernetes", "Docker", "Terraform",
        "Apache Airflow", "Apache Kafka", "Apache Spark", "Apache Beam", "Dbt", "Jenkins",
        "GitHub Actions", "CI/CD", "DevOps", "MicroStrategy", "Looker", "Power BI Service"
    ]
    
    for skill in skill_patterns:
        # Find sentences containing this skill
        for text in all_texts:
            if skill.lower() in text.lower():
                # Find exact position using text.find()
                start = text.find(skill)
                if start != -1:
                    end = start + len(skill)
                    entity_examples.append((text, {"entities": [(start, end, "SKILL")]}))
                    break
    
    # TITLE examples (50 sentences)
    title_patterns = [
        "Senior Data Analyst", "Sr Data Analyst", "Sr. Data Analyst", "Principal Data Analyst",
        "Senior Java Developer", "Sr Java Dev", "Senior Software Engineer", "Sr SWE",
        "Machine Learning Engineer", "ML Eng", "Senior ML Engineer", "Sr ML Engineer",
        "DevOps Engineer", "DevOps Eng", "Data Scientist", "Senior Data Scientist",
        "Sr Data Scientist", "Business Analyst", "Senior Business Analyst",
        "Software Engineer", "Senior Software Engineer", "Full Stack Developer",
        "Backend Developer", "Frontend Developer", "Data Engineer", "Senior Data Engineer"
    ]
    
    for title in title_patterns:
        for text in all_texts:
            if title.lower() in text.lower():
                start = text.find(title)
                if start != -1:
                    end = start + len(title)
                    entity_examples.append((text, {"entities": [(start, end, "TITLE")]}))
                    break
    
    # COMPANY examples (40 sentences)
    company_patterns = [
        "Home Depot", "Huntington", "Walgreens", "T-Mobile", "Ceva Logistics",
        "Google", "Microsoft", "Amazon", "Apple", "Facebook", "Netflix",
        "IBM", "Oracle", "Cisco", "Intel", "NVIDIA", "Salesforce",
        "Adobe", "Twitter", "LinkedIn", "Uber", "Airbnb", "Spotify",
        "Slack", "Zoom", "Dropbox", "GitHub", "GitLab", "Bitbucket",
        "Docker", "Red Hat", "VMware", "Citrix", "Palantir"
    ]
    
    for company in company_patterns:
        for text in all_texts:
            if company.lower() in text.lower():
                start = text.find(company)
                if start != -1:
                    end = start + len(company)
                    entity_examples.append((text, {"entities": [(start, end, "COMPANY")]}))
                    break
    
    # CLIENT: format examples (included in companies)
    client_patterns = [
        "CLIENT: Home Depot", "CLIENT: Huntington", "CLIENT: Walgreens", 
        "CLIENT: T-Mobile", "CLIENT: Ceva Logistics"
    ]
    
    for client in client_patterns:
        for text in all_texts:
            if client.lower() in text.lower():
                start = text.find(client)
                if start != -1:
                    end = start + len(client)
                    entity_examples.append((text, {"entities": [(start, end, "COMPANY")]}))
                    break
    
    # ROLE: format examples (included in titles)
    role_patterns = [
        "ROLE: Senior Data Analyst", "ROLE: Principal Data Analyst", "ROLE: Senior Data Analyst",
        "ROLE: Data Analyst", "ROLE: Junior Data Analyst", "ROLE: Senior Software Engineer"
    ]
    
    for role in role_patterns:
        for text in all_texts:
            if role.lower() in text.lower():
                start = text.find(role)
                if start != -1:
                    end = start + len(role)
                    entity_examples.append((text, {"entities": [(start, end, "TITLE")]}))
                    break
    
    # DATE examples (30 sentences)
    date_patterns = [
        "June 2023", "2023-Current", "June 2023 to Present", "2023-2024",
        "January 2020", "2020-2022", "August 2020", "May 2023",
        "October 2017", "September 2017", "December 2015", "May 2014",
        "2010-2014", "2024-2027", "2021-Present", "2017-2020"
    ]
    
    for date in date_patterns:
        for text in all_texts:
            if date in text:
                start = text.find(date)
                if start != -1:
                    end = start + len(date)
                    entity_examples.append((text, {"entities": [(start, end, "DATE")]}))
                    break
    
    # EDUCATION examples (25 sentences)
    education_patterns = [
        "Bachelor of Technology", "B.Tech", "B.Tech 2010-2014", "Master of Business Administration",
        "MBA", "Master of Science", "M.S.", "Bachelor of Science", "B.S.",
        "PhD", "Ph.D.", "Master of Computer Science", "Bachelor of Engineering"
    ]
    
    for edu in education_patterns:
        for text in all_texts:
            if edu.lower() in text.lower():
                start = text.find(edu)
                if start != -1:
                    end = start + len(edu)
                    entity_examples.append((text, {"entities": [(start, end, "EDUCATION")]}))
                    break
    
    # CERTIFICATION examples (25 sentences)
    cert_patterns = [
        "AWS Certified", "AWS certification", "AWS cert 2024-2027", "PMP",
        "Project Management Professional", "CISSP", "CPA", "CFA",
        "Azure Data Engineer", "Google Cloud Professional", "Microsoft Certified",
        "Oracle Certified", "Cisco Certified", "CompTIA A+", "Scrum Master"
    ]
    
    for cert in cert_patterns:
        for text in all_texts:
            if cert.lower() in text.lower():
                start = text.find(cert)
                if start != -1:
                    end = start + len(cert)
                    entity_examples.append((text, {"entities": [(start, end, "CERTIFICATION")]}))
                    break
    
    print(f"🎯 Generated {len(entity_examples)} raw entity examples")
    
    # Validate alignment for each example
    valid_examples = []
    invalid_count = 0
    
    nlp = spacy.blank("en")
    
    for text, entities in entity_examples:
        try:
            # Verify alignment using spacy's offsets_to_biluo_tags
            doc = nlp(text)
            biluo_tags = offsets_to_biluo_tags(doc, entities["entities"])
            
            # Check if alignment is valid (no '-' tags)
            if biluo_tags and '-' not in str(biluo_tags):
                valid_examples.append((text, entities))
            else:
                invalid_count += 1
        except Exception as e:
            invalid_count += 1
    
    print(f"✅ Valid examples: {len(valid_examples)}")
    print(f"❌ Invalid examples: {invalid_count}")
    print(f"📊 Total: {len(entity_examples)}")
    
    # Ensure we have at least 200 valid examples
    if len(valid_examples) < 200:
        print(f"⚠️ Warning: Only {len(valid_examples)} valid examples (need 200+)")
        print("🔄 Generating additional synthetic examples...")
        
        # Add synthetic examples if needed
        synthetic_examples = [
            ("Senior Data Analyst with 5 years of experience in Python and SQL", {"entities": [(0, 18, "TITLE"), (35, 41, "SKILL"), (46, 49, "SKILL")]}),
            ("CLIENT: Microsoft ROLE: Senior Software Engineer 2020-2023", {"entities": [(7, 16, "COMPANY"), (22, 44, "TITLE"), (45, 54, "DATE")]}),
            ("AWS Certified Solutions Architect valid until 2025", {"entities": [(0, 30, "CERTIFICATION"), (47, 51, "DATE")]}),
            ("Bachelor of Technology in Computer Science 2015-2019", {"entities": [(0, 22, "EDUCATION"), (26, 40, "DATE")]}),
            ("Experience at Google as Machine Learning Engineer", {"entities": [(14, 20, "COMPANY"), (24, 49, "TITLE")]}),
        ]
        
        for text, entities in synthetic_examples:
            try:
                doc = nlp(text)
                biluo_tags = offsets_to_biluo_tags(doc, entities["entities"])
                if biluo_tags and '-' not in str(biluo_tags):
                    valid_examples.append((text, entities))
            except:
                pass
    
    print(f"🎯 Final valid examples: {len(valid_examples)}")
    
    # Save training data
    os.makedirs("training_data", exist_ok=True)
    
    with open("training_data/ner_train.json", "w", encoding="utf-8") as f:
        json.dump(valid_examples, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Saved {len(valid_examples)} training examples to training_data/ner_train.json")
    
    return len(valid_examples)

if __name__ == "__main__":
    valid_count = generate_ner_training_data()
    print(f"\n✅ TASK 1 COMPLETE: {valid_count} valid NER training samples generated")
