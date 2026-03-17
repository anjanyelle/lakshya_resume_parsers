#!/usr/bin/env python3
"""
TASK 1 - Generate 200+ NER training samples - CORRECT METHOD
"""

import spacy
import json
import os
from spacy.training import offsets_to_biluo_tags

def make_example(text, entity_text, label):
    """Make training example with proper alignment"""
    start = text.find(entity_text)
    if start == -1:
        return None
    end = start + len(entity_text)
    doc = spacy.blank("en").make_doc(text)
    tags = offsets_to_biluo_tags(doc, [(start, end, label)])
    if '-' in str(tags):
        return None
    return (text, {"entities": [(start, end, label)]})

def generate_ner_training_correct():
    """Generate 200+ NER training samples correctly"""
    
    print("🔧 TASK 1 - GENERATING 200+ NER TRAINING SAMPLES (CORRECT)")
    print("=" * 60)
    
    # SKILL examples (60)
    skill_sentences = [
        ("Used Python for data processing", "Python", "SKILL"),
        ("Expert in Java development", "Java", "SKILL"),
        ("Skilled in JavaScript frameworks", "JavaScript", "SKILL"),
        ("Experience with Node backend", "Node", "SKILL"),
        ("Knowledge of SQL databases", "SQL", "SKILL"),
        ("Used Redis for caching", "Redis", "SKILL"),
        ("Deployed Docker containers", "Docker", "SKILL"),
        ("Managed Kubernetes clusters", "Kubernetes", "SKILL"),
        ("Worked with AWS cloud", "AWS", "SKILL"),
        ("Built Azure pipelines", "Azure", "SKILL"),
        ("Used GCP platform", "GCP", "SKILL"),
        ("Wrote Terraform scripts", "Terraform", "SKILL"),
        ("Configured Jenkins CI", "Jenkins", "SKILL"),
        ("Used Git version control", "Git", "SKILL"),
        ("Managed Linux servers", "Linux", "SKILL"),
        ("Installed Apache web server", "Apache", "SKILL"),
        ("Configured Nginx proxy", "Nginx", "SKILL"),
        ("Used Spark big data", "Spark", "SKILL"),
        ("Worked with Hadoop", "Hadoop", "SKILL"),
        ("Used Kafka streaming", "Kafka", "SKILL"),
        ("Built Elasticsearch search", "Elasticsearch", "SKILL"),
        ("Trained TensorFlow models", "TensorFlow", "SKILL"),
        ("Used PyTorch framework", "PyTorch", "SKILL"),
        ("Applied Scikit learn", "Scikit-learn", "SKILL"),
        ("Analyzed with Pandas", "Pandas", "SKILL"),
        ("Computed with NumPy", "NumPy", "SKILL"),
        ("Created Power reports", "Power", "SKILL"),
        ("Built Tableau dashboards", "Tableau", "SKILL"),
        ("Used Excel spreadsheets", "Excel", "SKILL"),
        ("Wrote VBA macros", "VBA", "SKILL"),
        ("Programmed in Python", "Python", "SKILL"),
        ("Automated with Python", "Python", "SKILL"),
        ("Used AWS Glue", "AWS Glue", "SKILL"),
        ("Processed with PySpark", "PySpark", "SKILL"),
        ("Queried Snowflake", "Snowflake", "SKILL"),
        ("Analyzed with Databricks", "Databricks", "SKILL"),
        ("Orchestrated Airflow", "Airflow", "SKILL"),
        ("Streamed with Kafka", "Kafka", "SKILL"),
        ("Transformed with Dbt", "Dbt", "SKILL"),
        ("Automated GitHub Actions", "GitHub Actions", "SKILL"),
        ("Implemented DevOps", "DevOps", "SKILL"),
        ("Built MicroStrategy", "MicroStrategy", "SKILL"),
        ("Analyzed with Looker", "Looker", "SKILL"),
        ("Used Power BI", "Power BI", "SKILL"),
        ("Streamed with Beam", "Beam", "SKILL"),
        ("Processed with Spark", "Spark", "SKILL"),
        ("Automated Jenkins", "Jenkins", "SKILL"),
        ("Managed GitLab", "GitLab", "SKILL"),
        ("Used Bitbucket", "Bitbucket", "SKILL"),
        ("Containerized with Docker", "Docker", "SKILL"),
        ("Orchestrated Kubernetes", "Kubernetes", "SKILL"),
        ("Wrote Terraform", "Terraform", "SKILL"),
        ("Configured Ansible", "Ansible", "SKILL"),
        ("Automated with Puppet", "Puppet", "SKILL"),
        ("Used Chef", "Chef", "SKILL"),
        ("Monitored Prometheus", "Prometheus", "SKILL"),
        ("Built Grafana", "Grafana", "SKILL"),
        ("Logged with ELK", "ELK", "SKILL"),
        ("Visualized with Kibana", "Kibana", "SKILL"),
        ("Processed with Logstash", "Logstash", "SKILL"),
        ("Used React", "React", "SKILL"),
        ("Built Angular", "Angular", "SKILL"),
        ("Created Vue", "Vue", "SKILL"),
        ("Used Express", "Express", "SKILL"),
        ("Applied Spring", "Spring", "SKILL"),
    ]
    
    # TITLE examples (50)
    title_sentences = [
        ("Working as Senior Data Analyst", "Senior Data Analyst", "TITLE"),
        ("Hired as Sr Data Analyst", "Sr Data Analyst", "TITLE"),
        ("Title is Principal Data Analyst", "Principal Data Analyst", "TITLE"),
        ("Senior Java Developer needed", "Senior Java Developer", "TITLE"),
        ("Sr Java Developer position", "Sr Java Developer", "TITLE"),
        ("Senior Software Engineer", "Senior Software Engineer", "TITLE"),
        ("Sr Software Engineer job", "Sr Software Engineer", "TITLE"),
        ("Machine Learning Engineer", "Machine Learning Engineer", "TITLE"),
        ("ML Engineer position", "ML Engineer", "TITLE"),
        ("Senior ML Engineer role", "Senior ML Engineer", "TITLE"),
        ("Sr ML Engineer needed", "Sr ML Engineer", "TITLE"),
        ("DevOps Engineer position", "DevOps Engineer", "TITLE"),
        ("Data Scientist role", "Data Scientist", "TITLE"),
        ("Senior Data Scientist position", "Senior Data Scientist", "TITLE"),
        ("Sr Data Scientist needed", "Sr Data Scientist", "TITLE"),
        ("Business Analyst job", "Business Analyst", "TITLE"),
        ("Senior Business Analyst role", "Senior Business Analyst", "TITLE"),
        ("Software Engineer position", "Software Engineer", "TITLE"),
        ("Full Stack Developer needed", "Full Stack Developer", "TITLE"),
        ("Backend Developer role", "Backend Developer", "TITLE"),
        ("Frontend Developer position", "Frontend Developer", "TITLE"),
        ("Data Engineer job", "Data Engineer", "TITLE"),
        ("Senior Data Engineer needed", "Senior Data Engineer", "TITLE"),
        ("Product Manager position", "Product Manager", "TITLE"),
        ("Senior Product Manager role", "Senior Product Manager", "TITLE"),
        ("Project Manager needed", "Project Manager", "TITLE"),
        ("Technical Lead position", "Technical Lead", "TITLE"),
        ("Engineering Manager role", "Engineering Manager", "TITLE"),
        ("Solutions Architect needed", "Solutions Architect", "TITLE"),
        ("Cloud Architect position", "Cloud Architect", "TITLE"),
        ("Security Engineer job", "Security Engineer", "TITLE"),
        ("QA Engineer position", "QA Engineer", "TITLE"),
        ("Data Analyst internship", "Data Analyst", "TITLE"),
        ("Junior Developer position", "Junior Developer", "TITLE"),
        ("Entry Level Engineer role", "Entry Level Engineer", "TITLE"),
    ]
    
    # COMPANY examples (40)
    company_sentences = [
        ("Worked at Google", "Google", "COMPANY"),
        ("Employed by Microsoft", "Microsoft", "COMPANY"),
        ("Job at Amazon", "Amazon", "COMPANY"),
        ("Position at Apple", "Apple", "COMPANY"),
        ("Role at Facebook", "Facebook", "COMPANY"),
        ("Experience at Netflix", "Netflix", "COMPANY"),
        ("Work at IBM", "IBM", "COMPANY"),
        ("Job at Oracle", "Oracle", "COMPANY"),
        ("Position at Cisco", "Cisco", "COMPANY"),
        ("Role at Intel", "Intel", "COMPANY"),
        ("Experience at NVIDIA", "NVIDIA", "COMPANY"),
        ("Work at Salesforce", "Salesforce", "COMPANY"),
        ("Job at Adobe", "Adobe", "COMPANY"),
        ("Position at Twitter", "Twitter", "COMPANY"),
        ("Role at LinkedIn", "LinkedIn", "COMPANY"),
        ("Experience at Uber", "Uber", "COMPANY"),
        ("Work at Airbnb", "Airbnb", "COMPANY"),
        ("Job at Spotify", "Spotify", "COMPANY"),
        ("Position at Slack", "Slack", "COMPANY"),
        ("Role at Zoom", "Zoom", "COMPANY"),
        ("Experience at Dropbox", "Dropbox", "COMPANY"),
        ("Work at GitHub", "GitHub", "COMPANY"),
        ("Job at GitLab", "GitLab", "COMPANY"),
        ("Position at Docker", "Docker", "COMPANY"),
        ("Experience at RedHat", "RedHat", "COMPANY"),
        ("Work at VMware", "VMware", "COMPANY"),
        ("Job at Citrix", "Citrix", "COMPANY"),
        ("Position at Palantir", "Palantir", "COMPANY"),
        ("Role at HomeDepot", "HomeDepot", "COMPANY"),
        ("Work at Huntington", "Huntington", "COMPANY"),
        ("Job at Walgreens", "Walgreens", "COMPANY"),
        ("Position at TMobile", "TMobile", "COMPANY"),
        ("Experience at Ceva", "Ceva", "COMPANY"),
    ]
    
    # CLIENT: format examples
    client_sentences = [
        ("CLIENT HomeDepot", "HomeDepot", "COMPANY"),
        ("CLIENT Huntington", "Huntington", "COMPANY"),
        ("CLIENT Walgreens", "Walgreens", "COMPANY"),
        ("CLIENT TMobile", "TMobile", "COMPANY"),
        ("CLIENT Ceva", "Ceva", "COMPANY"),
    ]
    
    # ROLE: format examples
    role_sentences = [
        ("ROLE Senior Data Analyst", "Senior Data Analyst", "TITLE"),
        ("ROLE Principal Data Analyst", "Principal Data Analyst", "TITLE"),
        ("ROLE Senior Data Analyst", "Senior Data Analyst", "TITLE"),
        ("ROLE Data Analyst", "Data Analyst", "TITLE"),
        ("ROLE Junior Data Analyst", "Junior Data Analyst", "TITLE"),
        ("ROLE Senior Software Engineer", "Senior Software Engineer", "TITLE"),
    ]
    
    # DATE examples (30)
    date_sentences = [
        ("Started in June 2023", "June 2023", "DATE"),
        ("Worked from 2023 to Current", "2023", "DATE"),
        ("June 2023 to Present", "June 2023", "DATE"),
        ("Present", "Present", "DATE"),
        ("Period from 2023 to 2024", "2023", "DATE"),
        ("Joined in January 2020", "January 2020", "DATE"),
        ("Worked from 2020 to 2022", "2020", "DATE"),
        ("Started August 2020", "August 2020", "DATE"),
        ("Left in May 2023", "May 2023", "DATE"),
        ("Employed October 2017", "October 2017", "DATE"),
        ("Resigned September 2017", "September 2017", "DATE"),
        ("Started December 2015", "December 2015", "DATE"),
        ("Worked until May 2014", "May 2014", "DATE"),
        ("Education from 2010 to 2014", "2010", "DATE"),
        ("Valid from 2024 to 2027", "2024", "DATE"),
        ("Hired in 2021", "2021", "DATE"),
        ("Promoted in 2022", "2022", "DATE"),
        ("Graduated in 2019", "2019", "DATE"),
        ("Certified in 2020", "2020", "DATE"),
        ("Trained in 2021", "2021", "DATE"),
        ("Launched in 2023", "2023", "DATE"),
        ("Released in 2024", "2024", "DATE"),
        ("Updated in 2023", "2023", "DATE"),
        ("Published in 2022", "2022", "DATE"),
        ("Presented in 2021", "2021", "DATE"),
        ("Awarded in 2020", "2020", "DATE"),
        ("Recognized in 2019", "2019", "DATE"),
        ("Achieved in 2018", "2018", "DATE"),
        ("Completed in 2017", "2017", "DATE"),
    ]
    
    # EDUCATION examples (25)
    education_sentences = [
        ("Bachelor of Technology degree", "Bachelor of Technology", "EDUCATION"),
        ("BTech in Computer Science", "BTech", "EDUCATION"),
        ("Master of Business Administration", "Master of Business Administration", "EDUCATION"),
        ("MBA degree completed", "MBA", "EDUCATION"),
        ("Master of Science in CS", "Master of Science in CS", "EDUCATION"),
        ("MS Computer Engineering", "MS Computer Engineering", "EDUCATION"),
        ("Bachelor of Science degree", "Bachelor of Science degree", "EDUCATION"),
        ("BS in Mathematics", "BS in Mathematics", "EDUCATION"),
        ("PhD in Computer Science", "PhD in Computer Science", "EDUCATION"),
        ("PhD research completed", "PhD", "EDUCATION"),
        ("Master of Computer Science", "Master of Computer Science", "EDUCATION"),
        ("Bachelor of Engineering", "Bachelor of Engineering", "EDUCATION"),
        ("BE Electrical Engineering", "BE Electrical Engineering", "EDUCATION"),
        ("ME Software Engineering", "ME Software Engineering", "EDUCATION"),
        ("Associate Degree completed", "Associate Degree", "EDUCATION"),
        ("Diploma in IT completed", "Diploma in IT", "EDUCATION"),
        ("Certificate in Data Science", "Certificate in Data Science", "EDUCATION"),
        ("Postgraduate studies", "Postgraduate studies", "EDUCATION"),
        ("Graduate program completed", "Graduate program completed", "EDUCATION"),
        ("Undergraduate degree", "Undergraduate degree", "EDUCATION"),
        ("Doctoral degree earned", "Doctoral degree", "EDUCATION"),
        ("Professional certification", "Professional certification", "EDUCATION"),
        ("Technical degree obtained", "Technical degree", "EDUCATION"),
    ]
    
    # CERTIFICATION examples (25)
    cert_sentences = [
        ("AWS Certified Solutions Architect", "AWS Certified Solutions Architect", "CERTIFICATION"),
        ("AWS certification completed", "AWS certification", "CERTIFICATION"),
        ("AWS cert 2024 to 2027", "AWS cert", "CERTIFICATION"),
        ("PMP Project Management Professional", "PMP Project Management Professional", "CERTIFICATION"),
        ("CISSP Information Security", "CISSP Information Security", "CERTIFICATION"),
        ("CPA Certified Public Accountant", "CPA Certified Public Accountant", "CERTIFICATION"),
        ("CFA Chartered Financial Analyst", "CFA Chartered Financial Analyst", "CERTIFICATION"),
        ("Azure Data Engineer certification", "Azure Data Engineer certification", "CERTIFICATION"),
        ("Google Cloud Professional", "Google Cloud Professional", "CERTIFICATION"),
        ("Microsoft Certified Expert", "Microsoft Certified Expert", "CERTIFICATION"),
        ("Oracle Certified Professional", "Oracle Certified Professional", "CERTIFICATION"),
        ("Cisco Certified Network Associate", "Cisco Certified Network Associate", "CERTIFICATION"),
        ("CompTIA A certification", "CompTIA A certification", "CERTIFICATION"),
        ("Scrum Master Certified", "Scrum Master Certified", "CERTIFICATION"),
        ("ITIL Foundation certification", "ITIL Foundation certification", "CERTIFICATION"),
        ("Linux Professional Institute", "Linux Professional Institute", "CERTIFICATION"),
        ("RedHat Certified Engineer", "RedHat Certified Engineer", "CERTIFICATION"),
        ("VMware Certified Professional", "VMware Certified Professional", "CERTIFICATION"),
        ("Docker Certified Associate", "Docker Certified Associate", "CERTIFICATION"),
        ("Kubernetes Certified Administrator", "Kubernetes Certified Administrator", "CERTIFICATION"),
        ("Terraform Associate certification", "Terraform Associate certification", "CERTIFICATION"),
        ("Jenkins Certified Engineer", "Jenkins Certified Engineer", "CERTIFICATION"),
        ("GitLab Certified Professional", "GitLab Certified Professional", "CERTIFICATION"),
        ("GitHub Actions certification", "GitHub Actions certification", "CERTIFICATION"),
    ]
    
    # Generate all examples
    all_sentences = (
        skill_sentences + 
        title_sentences + 
        company_sentences + 
        client_sentences + 
        role_sentences + 
        date_sentences + 
        education_sentences + 
        cert_sentences
    )
    
    print(f"🎯 Generated {len(all_sentences)} training examples")
    
    # Validate and create training data
    TRAIN_DATA = []
    skipped = 0
    
    for text, entity_text, label in all_sentences:
        example = make_example(text, entity_text, label)
        if example:
            TRAIN_DATA.append(example)
        else:
            skipped += 1
    
    print(f"✅ Valid examples: {len(TRAIN_DATA)}")
    print(f"❌ Skipped examples: {skipped}")
    print(f"📊 Total: {len(all_sentences)}")
    
    # Save training data
    os.makedirs("training_data", exist_ok=True)
    
    with open("training_data/ner_train.json", "w", encoding="utf-8") as f:
        json.dump(TRAIN_DATA, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Saved {len(TRAIN_DATA)} training examples to training_data/ner_train.json")
    
    return len(TRAIN_DATA)

if __name__ == "__main__":
    valid_count = generate_ner_training_correct()
    print(f"\n✅ TASK 1 COMPLETE: {valid_count} valid NER training samples generated")
