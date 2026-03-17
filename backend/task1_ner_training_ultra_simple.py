#!/usr/bin/env python3
"""
TASK 1 - Generate 200+ NER training samples - ULTRA SIMPLE
"""

import json
import spacy
from spacy.training import offsets_to_biluo_tags
import os

def generate_ner_training_ultra_simple():
    """Generate 200+ NER training samples - single words only"""
    
    print("🔧 TASK 1 - GENERATING 200+ NER TRAINING SAMPLES (ULTRA SIMPLE)")
    print("=" * 60)
    
    # Ultra simple training examples
    training_examples = []
    
    # SKILL examples (60) - Single words only
    skill_examples = [
        ("I know Python", {"entities": [(7, 13, "SKILL")]}),
        ("Expert in Java", {"entities": [(10, 14, "SKILL")]}),
        ("Skilled in JavaScript", {"entities": [(12, 22, "SKILL")]}),
        ("Experience with Node", {"entities": [(15, 19, "SKILL")]}),
        ("Knowledge of SQL", {"entities": [(14, 17, "SKILL")]}),
        ("Used Redis cache", {"entities": [(9, 14, "SKILL")]}),
        ("Deployed Docker", {"entities": [(9, 15, "SKILL")]}),
        ("Managed Kubernetes", {"entities": [(8, 19, "SKILL")]}),
        ("Worked with AWS", {"entities": [(12, 15, "SKILL")]}),
        ("Built Azure pipelines", {"entities": [(6, 11, "SKILL")]}),
        ("Used GCP platform", {"entities": [(5, 8, "SKILL")]}),
        ("Wrote Terraform code", {"entities": [(6, 15, "SKILL")]}),
        ("Configured Jenkins", {"entities": [(12, 19, "SKILL")]}),
        ("Used Git control", {"entities": [(5, 8, "SKILL")]}),
        ("Managed Linux servers", {"entities": [(8, 13, "SKILL")]}),
        ("Installed Apache", {"entities": [(10, 16, "SKILL")]}),
        ("Configured Nginx", {"entities": [(12, 17, "SKILL")]}),
        ("Used Spark processing", {"entities": [(5, 10, "SKILL")]}),
        ("Worked with Hadoop", {"entities": [(14, 20, "SKILL")]}),
        ("Used Kafka messaging", {"entities": [(5, 10, "SKILL")]}),
        ("Built Elasticsearch", {"entities": [(6, 19, "SKILL")]}),
        ("Trained TensorFlow models", {"entities": [(8, 18, "SKILL")]}),
        ("Used PyTorch framework", {"entities": [(5, 12, "SKILL")]}),
        ("Applied Scikit learn", {"entities": [(8, 20, "SKILL")]}),
        ("Analyzed with Pandas", {"entities": [(14, 20, "SKILL")]}),
        ("Computed with NumPy", {"entities": [(13, 17, "SKILL")]}),
        ("Created Power reports", {"entities": [(9, 14, "SKILL")]}),
        ("Built Tableau dashboards", {"entities": [(6, 13, "SKILL")]}),
        ("Used Excel spreadsheets", {"entities": [(5, 10, "SKILL")]}),
        ("Wrote VBA macros", {"entities": [(6, 9, "SKILL")]}),
        ("Programmed in Python", {"entities": [(13, 19, "SKILL")]}),
        ("Automated with Python", {"entities": [(13, 19, "SKILL")]}),
        ("Used AWS Glue", {"entities": [(5, 13, "SKILL")]}),
        ("Processed with PySpark", {"entities": [(14, 21, "SKILL")]}),
        ("Queried Snowflake", {"entities": [(9, 18, "SKILL")]}),
        ("Analyzed with Databricks", {"entities": [(14, 24, "SKILL")]}),
        ("Orchestrated Airflow", {"entities": [(14, 22, "SKILL")]}),
        ("Streamed with Kafka", {"entities": [(14, 19, "SKILL")]}),
        ("Transformed with Dbt", {"entities": [(14, 17, "SKILL")]}),
        ("Automated GitHub Actions", {"entities": [(11, 18, "SKILL")]}),
        ("Implemented DevOps", {"entities": [(13, 20, "SKILL")]}),
        ("Built MicroStrategy reports", {"entities": [(6, 18, "SKILL")]}),
        ("Analyzed with Looker", {"entities": [(14, 20, "SKILL")]}),
        ("Used Power Service", {"entities": [(5, 9, "SKILL"), (10, 17, "SKILL")]}),
        ("Streamed with Beam", {"entities": [(14, 18, "SKILL")]}),
        ("Processed with Spark", {"entities": [(14, 19, "SKILL")]}),
        ("Automated Jenkins pipelines", {"entities": [(11, 18, "SKILL")]}),
        ("Managed GitLab repos", {"entities": [(8, 15, "SKILL")]}),
        ("Used Bitbucket for code", {"entities": [(6, 15, "SKILL")]}),
        ("Containerized with Docker", {"entities": [(16, 22, "SKILL")]}),
        ("Orchestrated Kubernetes", {"entities": [(14, 26, "SKILL")]}),
        ("Wrote Terraform scripts", {"entities": [(6, 16, "SKILL")]}),
        ("Configured Ansible", {"entities": [(13, 20, "SKILL")]}),
        ("Automated with Puppet", {"entities": [(14, 20, "SKILL")]}),
        ("Used Chef for config", {"entities": [(6, 10, "SKILL")]}),
        ("Monitored Prometheus", {"entities": [(11, 21, "SKILL")]}),
        ("Built Grafana dashboards", {"entities": [(6, 14, "SKILL")]}),
        ("Logged with ELK stack", {"entities": [(10, 18, "SKILL")]}),
        ("Visualized with Kibana", {"entities": [(14, 21, "SKILL")]}),
        ("Processed with Logstash", {"entities": [(14, 22, "SKILL")]}),
    ]
    
    # TITLE examples (50) - Simple titles
    title_examples = [
        ("Senior Data Analyst", {"entities": [(0, 18, "TITLE")]}),
        ("Sr Data Analyst", {"entities": [(0, 14, "TITLE")]}),
        ("Principal Data Analyst", {"entities": [(0, 22, "TITLE")]}),
        ("Senior Java Developer", {"entities": [(0, 20, "TITLE")]}),
        ("Sr Java Developer", {"entities": [(0, 16, "TITLE")]}),
        ("Senior Software Engineer", {"entities": [(0, 22, "TITLE")]}),
        ("Sr Software Engineer", {"entities": [(0, 19, "TITLE")]}),
        ("Machine Learning Engineer", {"entities": [(0, 23, "TITLE")]}),
        ("ML Engineer", {"entities": [(0, 12, "TITLE")]}),
        ("Senior ML Engineer", {"entities": [(0, 18, "TITLE")]}),
        ("Sr ML Engineer", {"entities": [(0, 13, "TITLE")]}),
        ("DevOps Engineer", {"entities": [(0, 16, "TITLE")]}),
        ("Data Scientist", {"entities": [(0, 14, "TITLE")]}),
        ("Senior Data Scientist", {"entities": [(0, 21, "TITLE")]}),
        ("Sr Data Scientist", {"entities": [(0, 16, "TITLE")]}),
        ("Business Analyst", {"entities": [(0, 15, "TITLE")]}),
        ("Senior Business Analyst", {"entities": [(0, 22, "TITLE")]}),
        ("Software Engineer", {"entities": [(0, 17, "TITLE")]}),
        ("Full Stack Developer", {"entities": [(0, 19, "TITLE")]}),
        ("Backend Developer", {"entities": [(0, 17, "TITLE")]}),
        ("Frontend Developer", {"entities": [(0, 18, "TITLE")]}),
        ("Data Engineer", {"entities": [(0, 13, "TITLE")]}),
        ("Senior Data Engineer", {"entities": [(0, 20, "TITLE")]}),
        ("Product Manager", {"entities": [(0, 15, "TITLE")]}),
        ("Senior Product Manager", {"entities": [(0, 22, "TITLE")]}),
        ("Project Manager", {"entities": [(0, 15, "TITLE")]}),
        ("Technical Lead", {"entities": [(0, 13, "TITLE")]}),
        ("Engineering Manager", {"entities": [(0, 19, "TITLE")]}),
        ("Solutions Architect", {"entities": [(0, 20, "TITLE")]}),
        ("Cloud Architect", {"entities": [(0, 15, "TITLE")]}),
        ("Security Engineer", {"entities": [(0, 17, "TITLE")]}),
        ("QA Engineer", {"entities": [(0, 12, "TITLE")]}),
        ("Data Analyst", {"entities": [(0, 13, "TITLE")]}),
        ("Junior Developer", {"entities": [(0, 16, "TITLE")]}),
        ("Entry Level Engineer", {"entities": [(0, 19, "TITLE")]}),
    ]
    
    # COMPANY examples (40) - Single words
    company_examples = [
        ("Worked at Google", {"entities": [(10, 16, "COMPANY")]}),
        ("Employed by Microsoft", {"entities": [(12, 21, "COMPANY")]}),
        ("Job at Amazon", {"entities": [(7, 13, "COMPANY")]}),
        ("Position at Apple", {"entities": [(12, 17, "COMPANY")]}),
        ("Role at Facebook", {"entities": [(9, 17, "COMPANY")]}),
        ("Experience at Netflix", {"entities": [(14, 21, "COMPANY")]}),
        ("Work at IBM", {"entities": [(8, 11, "COMPANY")]}),
        ("Job at Oracle", {"entities": [(7, 13, "COMPANY")]}),
        ("Position at Cisco", {"entities": [(12, 17, "COMPANY")]}),
        ("Role at Intel", {"entities": [(8, 13, "COMPANY")]}),
        ("Experience at NVIDIA", {"entities": [(14, 20, "COMPANY")]}),
        ("Work at Salesforce", {"entities": [(8, 18, "COMPANY")]}),
        ("Job at Adobe", {"entities": [(7, 12, "COMPANY")]}),
        ("Position at Twitter", {"entities": [(12, 19, "COMPANY")]}),
        ("Role at LinkedIn", {"entities": [(8, 16, "COMPANY")]}),
        ("Experience at Uber", {"entities": [(14, 18, "COMPANY")]}),
        ("Work at Airbnb", {"entities": [(8, 14, "COMPANY")]}),
        ("Job at Spotify", {"entities": [(7, 15, "COMPANY")]}),
        ("Position at Slack", {"entities": [(12, 17, "COMPANY")]}),
        ("Role at Zoom", {"entities": [(8, 12, "COMPANY")]}),
        ("Experience at Dropbox", {"entities": [(14, 21, "COMPANY")]}),
        ("Work at GitHub", {"entities": [(8, 14, "COMPANY")]}),
        ("Job at GitLab", {"entities": [(7, 13, "COMPANY")]}),
        ("Position at Docker", {"entities": [(12, 18, "COMPANY")]}),
        ("Experience at RedHat", {"entities": [(14, 20, "COMPANY")]}),
        ("Work at VMware", {"entities": [(8, 15, "COMPANY")]}),
        ("Job at Citrix", {"entities": [(7, 13, "COMPANY")]}),
        ("Position at Palantir", {"entities": [(12, 20, "COMPANY")]}),
        ("Role at HomeDepot", {"entities": [(8, 16, "COMPANY")]}),
        ("Work at Huntington", {"entities": [(8, 17, "COMPANY")]}),
        ("Job at Walgreens", {"entities": [(7, 16, "COMPANY")]}),
        ("Position at TMobile", {"entities": [(12, 19, "COMPANY")]}),
        ("Experience at Ceva", {"entities": [(14, 18, "COMPANY")]}),
    ]
    
    # CLIENT: format examples
    client_examples = [
        ("CLIENT HomeDepot", {"entities": [(7, 16, "COMPANY")]}),
        ("CLIENT Huntington", {"entities": [(7, 16, "COMPANY")]}),
        ("CLIENT Walgreens", {"entities": [(7, 16, "COMPANY")]}),
        ("CLIENT TMobile", {"entities": [(7, 15, "COMPANY")]}),
        ("CLIENT Ceva", {"entities": [(7, 11, "COMPANY")]}),
    ]
    
    # ROLE: format examples
    role_examples = [
        ("ROLE Senior Data Analyst", {"entities": [(5, 23, "TITLE")]}),
        ("ROLE Principal Data Analyst", {"entities": [(5, 27, "TITLE")]}),
        ("ROLE Senior Data Analyst", {"entities": [(5, 25, "TITLE")]}),
        ("ROLE Data Analyst", {"entities": [(5, 18, "TITLE")]}),
        ("ROLE Junior Data Analyst", {"entities": [(5, 24, "TITLE")]}),
        ("ROLE Senior Software Engineer", {"entities": [(5, 27, "TITLE")]}),
    ]
    
    # DATE examples (30) - Simple dates
    date_examples = [
        ("Started in June 2023", {"entities": [(12, 22, "DATE")]}),
        ("Worked from 2023 to Current", {"entities": [(14, 18, "DATE"), (23, 30, "DATE")]}),
        ("June 2023 to Present", {"entities": [(0, 10, "DATE"), (14, 21, "DATE")]}),
        ("Period from 2023 to 2024", {"entities": [(14, 18, "DATE"), (23, 27, "DATE")]}),
        ("Joined in January 2020", {"entities": [(11, 24, "DATE")]}),
        ("Worked from 2020 to 2022", {"entities": [(14, 18, "DATE"), (23, 27, "DATE")]}),
        ("Started August 2020", {"entities": [(9, 21, "DATE")]}),
        ("Left in May 2023", {"entities": [(8, 17, "DATE")]}),
        ("Employed October 2017", {"entities": [(11, 26, "DATE")]}),
        ("Resigned September 2017", {"entities": [(11, 27, "DATE")]}),
        ("Started December 2015", {"entities": [(9, 25, "DATE")]}),
        ("Worked until May 2014", {"entities": [(13, 22, "DATE")]}),
        ("Education from 2010 to 2014", {"entities": [(16, 20, "DATE"), (25, 29, "DATE")]}),
        ("Valid from 2024 to 2027", {"entities": [(11, 15, "DATE"), (20, 24, "DATE")]}),
        ("Hired in 2021", {"entities": [(9, 13, "DATE")]}),
        ("Promoted in 2022", {"entities": [(10, 14, "DATE")]}),
        ("Graduated in 2019", {"entities": [(11, 15, "DATE")]}),
        ("Certified in 2020", {"entities": [(11, 15, "DATE")]}),
        ("Trained in 2021", {"entities": [(9, 13, "DATE")]}),
        ("Launched in 2023", {"entities": [(10, 14, "DATE")]}),
        ("Released in 2024", {"entities": [(10, 14, "DATE")]}),
        ("Updated in 2023", {"entities": [(9, 13, "DATE")]}),
        ("Published in 2022", {"entities": [(12, 16, "DATE")]}),
        ("Presented in 2021", {"entities": [(11, 15, "DATE")]}),
        ("Awarded in 2020", {"entities": [(9, 13, "DATE")]}),
        ("Recognized in 2019", {"entities": [(12, 16, "DATE")]}),
        ("Achieved in 2018", {"entities": [(10, 14, "DATE")]}),
        ("Completed in 2017", {"entities": [(11, 15, "DATE")]}),
    ]
    
    # EDUCATION examples (25) - Simple education
    education_examples = [
        ("Bachelor of Technology", {"entities": [(0, 22, "EDUCATION")]}),
        ("BTech in Computer Science", {"entities": [(0, 5, "EDUCATION")]}),
        ("Master of Business Administration", {"entities": [(0, 29, "EDUCATION")]}),
        ("MBA degree completed", {"entities": [(0, 3, "EDUCATION")]}),
        ("Master of Science in CS", {"entities": [(0, 16, "EDUCATION")]}),
        ("MS Computer Engineering", {"entities": [(0, 2, "EDUCATION")]}),
        ("Bachelor of Science degree", {"entities": [(0, 20, "EDUCATION")]}),
        ("BS in Mathematics", {"entities": [(0, 2, "EDUCATION")]}),
        ("PhD in Computer Science", {"entities": [(0, 3, "EDUCATION")]}),
        ("PhD research completed", {"entities": [(0, 3, "EDUCATION")]}),
        ("Master of Computer Science", {"entities": [(0, 24, "EDUCATION")]}),
        ("Bachelor of Engineering", {"entities": [(0, 21, "EDUCATION")]}),
        ("BE Electrical Engineering", {"entities": [(0, 2, "EDUCATION")]}),
        ("ME Software Engineering", {"entities": [(0, 2, "EDUCATION")]}),
        ("Associate Degree completed", {"entities": [(0, 15, "EDUCATION")]}),
        ("Diploma in IT completed", {"entities": [(0, 8, "EDUCATION")]}),
        ("Certificate in Data Science", {"entities": [(0, 12, "EDUCATION")]}),
        ("Postgraduate studies", {"entities": [(0, 18, "EDUCATION")]}),
        ("Graduate program completed", {"entities": [(0, 25, "EDUCATION")]}),
        ("Undergraduate degree", {"entities": [(0, 19, "EDUCATION")]}),
        ("Doctoral degree earned", {"entities": [(0, 17, "EDUCATION")]}),
        ("Professional certification", {"entities": [(0, 23, "EDUCATION")]}),
        ("Technical degree obtained", {"entities": [(0, 16, "EDUCATION")]}),
    ]
    
    # CERTIFICATION examples (25) - Simple certifications
    cert_examples = [
        ("AWS Certified Solutions Architect", {"entities": [(0, 30, "CERTIFICATION")]}),
        ("AWS certification completed", {"entities": [(0, 19, "CERTIFICATION")]}),
        ("AWS cert 2024 to 2027", {"entities": [(0, 8, "CERTIFICATION")]}),
        ("PMP Project Management Professional", {"entities": [(0, 33, "CERTIFICATION")]}),
        ("CISSP Information Security", {"entities": [(0, 5, "CERTIFICATION")]}),
        ("CPA Certified Public Accountant", {"entities": [(0, 4, "CERTIFICATION")]}),
        ("CFA Chartered Financial Analyst", {"entities": [(0, 4, "CERTIFICATION")]}),
        ("Azure Data Engineer certification", {"entities": [(0, 29, "CERTIFICATION")]}),
        ("Google Cloud Professional", {"entities": [(0, 24, "CERTIFICATION")]}),
        ("Microsoft Certified Expert", {"entities": [(0, 22, "CERTIFICATION")]}),
        ("Oracle Certified Professional", {"entities": [(0, 26, "CERTIFICATION")]}),
        ("Cisco Certified Network Associate", {"entities": [(0, 6, "CERTIFICATION")]}),
        ("CompTIA A certification", {"entities": [(0, 9, "CERTIFICATION")]}),
        ("Scrum Master Certified", {"entities": [(0, 22, "CERTIFICATION")]}),
        ("ITIL Foundation certification", {"entities": [(0, 5, "CERTIFICATION")]}),
        ("Linux Professional Institute", {"entities": [(0, 8, "CERTIFICATION")]}),
        ("RedHat Certified Engineer", {"entities": [(0, 5, "CERTIFICATION")]}),
        ("VMware Certified Professional", {"entities": [(0, 6, "CERTIFICATION")]}),
        ("Docker Certified Associate", {"entities": [(0, 6, "CERTIFICATION")]}),
        ("Kubernetes Certified Administrator", {"entities": [(0, 13, "CERTIFICATION")]}),
        ("Terraform Associate certification", {"entities": [(0, 9, "CERTIFICATION")]}),
        ("Jenkins Certified Engineer", {"entities": [(0, 8, "CERTIFICATION")]}),
        ("GitLab Certified Professional", {"entities": [(0, 6, "CERTIFICATION")]}),
        ("GitHub Actions certification", {"entities": [(0, 6, "CERTIFICATION")]}),
    ]
    
    # Combine all examples
    all_examples = (
        skill_examples + 
        title_examples + 
        company_examples + 
        client_examples + 
        role_examples + 
        date_examples + 
        education_examples + 
        cert_examples
    )
    
    print(f"🎯 Generated {len(all_examples)} training examples")
    
    # Validate all examples
    nlp = spacy.blank("en")
    valid_examples = []
    invalid_count = 0
    
    for text, entities in all_examples:
        try:
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
    print(f"📊 Total: {len(all_examples)}")
    
    # Save training data
    os.makedirs("training_data", exist_ok=True)
    
    with open("training_data/ner_train.json", "w", encoding="utf-8") as f:
        json.dump(valid_examples, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Saved {len(valid_examples)} training examples to training_data/ner_train.json")
    
    return len(valid_examples)

if __name__ == "__main__":
    valid_count = generate_ner_training_ultra_simple()
    print(f"\n✅ TASK 1 COMPLETE: {valid_count} valid NER training samples generated")
