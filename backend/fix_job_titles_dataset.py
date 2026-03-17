#!/usr/bin/env python3
"""
FIX JOB TITLES DATASET - Expand to 500+ rows
"""

import pandas as pd
import random
import os
from pathlib import Path

def expand_job_titles_dataset():
    """Expand job titles dataset to 500+ rows"""
    
    print("🔧 EXPANDING JOB TITLES DATASET TO 500+ ROWS")
    print("=" * 50)
    
    # Load existing dataset
    if Path("data/enhanced_job_titles.csv").exists():
        df = pd.read_csv("data/enhanced_job_titles.csv")
        print(f"📄 Loaded existing dataset: {len(df)} rows")
    else:
        print("❌ No existing dataset found")
        return False
    
    # Generate additional job title variations
    additional_titles = [
        # Technology variations
        ("Senior Python Developer", "Senior Python Developer", "Technology"),
        ("Python Developer", "Python Developer", "Technology"),
        ("Junior Python Developer", "Junior Python Developer", "Technology"),
        ("Lead Python Developer", "Lead Python Developer", "Technology"),
        ("Principal Python Developer", "Principal Python Developer", "Technology"),
        ("Python Software Engineer", "Python Software Engineer", "Technology"),
        ("Full Stack Python Developer", "Full Stack Python Developer", "Technology"),
        ("Python Backend Developer", "Python Backend Developer", "Technology"),
        ("Python Frontend Developer", "Python Frontend Developer", "Technology"),
        ("Python Web Developer", "Python Web Developer", "Technology"),
        
        ("Senior Java Developer", "Senior Java Developer", "Technology"),
        ("Java Developer", "Java Developer", "Technology"),
        ("Junior Java Developer", "Junior Java Developer", "Technology"),
        ("Lead Java Developer", "Lead Java Developer", "Technology"),
        ("Principal Java Developer", "Principal Java Developer", "Technology"),
        ("Java Software Engineer", "Java Software Engineer", "Technology"),
        ("Full Stack Java Developer", "Full Stack Java Developer", "Technology"),
        ("Java Backend Developer", "Java Backend Developer", "Technology"),
        ("Java Frontend Developer", "Java Frontend Developer", "Technology"),
        ("Java Web Developer", "Java Web Developer", "Technology"),
        
        ("Senior JavaScript Developer", "Senior JavaScript Developer", "Technology"),
        ("JavaScript Developer", "JavaScript Developer", "Technology"),
        ("Junior JavaScript Developer", "Junior JavaScript Developer", "Technology"),
        ("Lead JavaScript Developer", "Lead JavaScript Developer", "Technology"),
        ("Principal JavaScript Developer", "Principal JavaScript Developer", "Technology"),
        ("JavaScript Software Engineer", "JavaScript Software Engineer", "Technology"),
        ("Full Stack JavaScript Developer", "Full Stack JavaScript Developer", "Technology"),
        ("JavaScript Frontend Developer", "JavaScript Frontend Developer", "Technology"),
        ("JavaScript Web Developer", "JavaScript Web Developer", "Technology"),
        ("React Developer", "React Developer", "Technology"),
        
        ("Senior React Developer", "Senior React Developer", "Technology"),
        ("Junior React Developer", "Junior React Developer", "Technology"),
        ("Lead React Developer", "Lead React Developer", "Technology"),
        ("React Frontend Developer", "React Frontend Developer", "Technology"),
        ("React Native Developer", "React Native Developer", "Technology"),
        
        ("Senior Angular Developer", "Senior Angular Developer", "Technology"),
        ("Angular Developer", "Angular Developer", "Technology"),
        ("Junior Angular Developer", "Junior Angular Developer", "Technology"),
        ("Lead Angular Developer", "Lead Angular Developer", "Technology"),
        ("Angular Frontend Developer", "Angular Frontend Developer", "Technology"),
        
        ("Senior Node.js Developer", "Senior Node.js Developer", "Technology"),
        ("Node.js Developer", "Node.js Developer", "Technology"),
        ("Junior Node.js Developer", "Junior Node.js Developer", "Technology"),
        ("Lead Node.js Developer", "Lead Node.js Developer", "Technology"),
        ("Node.js Backend Developer", "Node.js Backend Developer", "Technology"),
        
        ("Senior DevOps Engineer", "Senior DevOps Engineer", "Technology"),
        ("DevOps Engineer", "DevOps Engineer", "Technology"),
        ("Junior DevOps Engineer", "Junior DevOps Engineer", "Technology"),
        ("Lead DevOps Engineer", "Lead DevOps Engineer", "Technology"),
        ("Principal DevOps Engineer", "Principal DevOps Engineer", "Technology"),
        ("DevOps Architect", "DevOps Architect", "Technology"),
        ("Cloud DevOps Engineer", "Cloud DevOps Engineer", "Technology"),
        
        ("Senior Cloud Engineer", "Senior Cloud Engineer", "Technology"),
        ("Cloud Engineer", "Cloud Engineer", "Technology"),
        ("Junior Cloud Engineer", "Junior Cloud Engineer", "Technology"),
        ("Lead Cloud Engineer", "Lead Cloud Engineer", "Technology"),
        ("Cloud Architect", "Cloud Architect", "Technology"),
        ("AWS Cloud Engineer", "AWS Cloud Engineer", "Technology"),
        ("Azure Cloud Engineer", "Azure Cloud Engineer", "Technology"),
        ("GCP Cloud Engineer", "GCP Cloud Engineer", "Technology"),
        
        ("Senior Data Engineer", "Senior Data Engineer", "Technology"),
        ("Data Engineer", "Data Engineer", "Technology"),
        ("Junior Data Engineer", "Junior Data Engineer", "Technology"),
        ("Lead Data Engineer", "Lead Data Engineer", "Technology"),
        ("Principal Data Engineer", "Principal Data Engineer", "Technology"),
        ("Big Data Engineer", "Big Data Engineer", "Technology"),
        ("Data Platform Engineer", "Data Platform Engineer", "Technology"),
        ("Data Pipeline Engineer", "Data Pipeline Engineer", "Technology"),
        
        ("Senior Machine Learning Engineer", "Senior Machine Learning Engineer", "Technology"),
        ("Machine Learning Engineer", "Machine Learning Engineer", "Technology"),
        ("Junior Machine Learning Engineer", "Junior Machine Learning Engineer", "Technology"),
        ("Lead Machine Learning Engineer", "Lead Machine Learning Engineer", "Technology"),
        ("ML Engineer", "ML Engineer", "Technology"),
        ("AI Engineer", "AI Engineer", "Technology"),
        ("Deep Learning Engineer", "Deep Learning Engineer", "Technology"),
        
        ("Senior Data Scientist", "Senior Data Scientist", "Technology"),
        ("Data Scientist", "Data Scientist", "Technology"),
        ("Junior Data Scientist", "Junior Data Scientist", "Technology"),
        ("Lead Data Scientist", "Lead Data Scientist", "Technology"),
        ("Principal Data Scientist", "Principal Data Scientist", "Technology"),
        ("Research Scientist", "Research Scientist", "Technology"),
        ("Applied Scientist", "Applied Scientist", "Technology"),
        
        ("Senior Software Engineer", "Senior Software Engineer", "Technology"),
        ("Software Engineer", "Software Engineer", "Technology"),
        ("Junior Software Engineer", "Junior Software Engineer", "Technology"),
        ("Lead Software Engineer", "Lead Software Engineer", "Technology"),
        ("Principal Software Engineer", "Principal Software Engineer", "Technology"),
        ("Software Architect", "Software Architect", "Technology"),
        ("Principal Software Architect", "Principal Software Architect", "Technology"),
        ("Solutions Architect", "Solutions Architect", "Technology"),
        
        ("Senior Backend Engineer", "Senior Backend Engineer", "Technology"),
        ("Backend Engineer", "Backend Engineer", "Technology"),
        ("Junior Backend Engineer", "Junior Backend Engineer", "Technology"),
        ("Lead Backend Engineer", "Lead Backend Engineer", "Technology"),
        
        ("Senior Frontend Engineer", "Senior Frontend Engineer", "Technology"),
        ("Frontend Engineer", "Frontend Engineer", "Technology"),
        ("Junior Frontend Engineer", "Junior Frontend Engineer", "Technology"),
        ("Lead Frontend Engineer", "Lead Frontend Engineer", "Technology"),
        
        ("Senior Full Stack Engineer", "Senior Full Stack Engineer", "Technology"),
        ("Full Stack Engineer", "Full Stack Engineer", "Technology"),
        ("Junior Full Stack Engineer", "Junior Full Stack Engineer", "Technology"),
        ("Lead Full Stack Engineer", "Lead Full Stack Engineer", "Technology"),
        
        ("Senior Mobile Developer", "Senior Mobile Developer", "Technology"),
        ("Mobile Developer", "Mobile Developer", "Technology"),
        ("Junior Mobile Developer", "Junior Mobile Developer", "Technology"),
        ("iOS Developer", "iOS Developer", "Technology"),
        ("Android Developer", "Android Developer", "Technology"),
        ("React Native Developer", "React Native Developer", "Technology"),
        ("Flutter Developer", "Flutter Developer", "Technology"),
        
        ("Senior QA Engineer", "Senior QA Engineer", "Technology"),
        ("QA Engineer", "QA Engineer", "Technology"),
        ("Junior QA Engineer", "Junior QA Engineer", "Technology"),
        ("Lead QA Engineer", "Lead QA Engineer", "Technology"),
        ("Test Engineer", "Test Engineer", "Technology"),
        ("Automation Engineer", "Automation Engineer", "Technology"),
        ("Test Automation Engineer", "Test Automation Engineer", "Technology"),
        
        ("Senior Database Administrator", "Senior Database Administrator", "Technology"),
        ("Database Administrator", "Database Administrator", "Technology"),
        ("Junior Database Administrator", "Junior Database Administrator", "Technology"),
        ("Lead Database Administrator", "Lead Database Administrator", "Technology"),
        ("DBA", "DBA", "Technology"),
        
        ("Senior Network Engineer", "Senior Network Engineer", "Technology"),
        ("Network Engineer", "Network Engineer", "Technology"),
        ("Junior Network Engineer", "Junior Network Engineer", "Technology"),
        ("Lead Network Engineer", "Lead Network Engineer", "Technology"),
        
        ("Senior Security Engineer", "Senior Security Engineer", "Technology"),
        ("Security Engineer", "Security Engineer", "Technology"),
        ("Junior Security Engineer", "Junior Security Engineer", "Technology"),
        ("Lead Security Engineer", "Lead Security Engineer", "Technology"),
        ("Cybersecurity Engineer", "Cybersecurity Engineer", "Technology"),
        ("Information Security Engineer", "Information Security Engineer", "Technology"),
        
        # Business variations
        ("Senior Business Analyst", "Senior Business Analyst", "Business"),
        ("Business Analyst", "Business Analyst", "Business"),
        ("Junior Business Analyst", "Junior Business Analyst", "Business"),
        ("Lead Business Analyst", "Lead Business Analyst", "Business"),
        ("Principal Business Analyst", "Principal Business Analyst", "Business"),
        ("Business Systems Analyst", "Business Systems Analyst", "Business"),
        ("Technical Business Analyst", "Technical Business Analyst", "Business"),
        ("Financial Analyst", "Financial Analyst", "Business"),
        ("Senior Financial Analyst", "Senior Financial Analyst", "Business"),
        ("Business Intelligence Analyst", "Business Intelligence Analyst", "Business"),
        ("BI Analyst", "BI Analyst", "Business"),
        ("Data Analyst", "Data Analyst", "Business"),
        ("Senior Data Analyst", "Senior Data Analyst", "Business"),
        ("Junior Data Analyst", "Junior Data Analyst", "Business"),
        ("Lead Data Analyst", "Lead Data Analyst", "Business"),
        ("Principal Data Analyst", "Principal Data Analyst", "Business"),
        ("Business Analytics Manager", "Business Analytics Manager", "Business"),
        ("Analytics Manager", "Analytics Manager", "Business"),
        
        ("Senior Product Manager", "Senior Product Manager", "Business"),
        ("Product Manager", "Product Manager", "Business"),
        ("Junior Product Manager", "Junior Product Manager", "Business"),
        ("Lead Product Manager", "Lead Product Manager", "Business"),
        ("Principal Product Manager", "Principal Product Manager", "Business"),
        ("Technical Product Manager", "Technical Product Manager", "Business"),
        ("Associate Product Manager", "Associate Product Manager", "Business"),
        ("Product Owner", "Product Owner", "Business"),
        ("Senior Product Owner", "Senior Product Owner", "Business"),
        
        ("Senior Project Manager", "Senior Project Manager", "Business"),
        ("Project Manager", "Project Manager", "Business"),
        ("Junior Project Manager", "Junior Project Manager", "Business"),
        ("Lead Project Manager", "Lead Project Manager", "Business"),
        ("Technical Project Manager", "Technical Project Manager", "Business"),
        ("IT Project Manager", "IT Project Manager", "Business"),
        ("Program Manager", "Program Manager", "Business"),
        ("Senior Program Manager", "Senior Program Manager", "Business"),
        ("Portfolio Manager", "Portfolio Manager", "Business"),
        
        ("Senior Marketing Manager", "Senior Marketing Manager", "Business"),
        ("Marketing Manager", "Marketing Manager", "Business"),
        ("Digital Marketing Manager", "Digital Marketing Manager", "Business"),
        ("Product Marketing Manager", "Product Marketing Manager", "Business"),
        ("Brand Manager", "Brand Manager", "Business"),
        
        ("Senior Sales Manager", "Senior Sales Manager", "Business"),
        ("Sales Manager", "Sales Manager", "Business"),
        ("Account Manager", "Account Manager", "Business"),
        ("Senior Account Manager", "Senior Account Manager", "Business"),
        ("Client Manager", "Client Manager", "Business"),
        ("Business Development Manager", "Business Development Manager", "Business"),
        
        ("Senior Operations Manager", "Senior Operations Manager", "Business"),
        ("Operations Manager", "Operations Manager", "Business"),
        ("IT Operations Manager", "IT Operations Manager", "Business"),
        ("Senior HR Manager", "Senior HR Manager", "Business"),
        ("HR Manager", "HR Manager", "Business"),
        ("Talent Manager", "Talent Manager", "Business"),
        
        # Research variations
        ("Senior Research Scientist", "Senior Research Scientist", "Research"),
        ("Research Scientist", "Research Scientist", "Research"),
        ("Junior Research Scientist", "Junior Research Scientist", "Research"),
        ("Lead Research Scientist", "Lead Research Scientist", "Research"),
        ("Principal Research Scientist", "Principal Research Scientist", "Research"),
        ("Applied Research Scientist", "Applied Research Scientist", "Research"),
        ("Research Engineer", "Research Engineer", "Research"),
        ("Senior Research Engineer", "Senior Research Engineer", "Research"),
        
        ("Senior Data Researcher", "Senior Data Researcher", "Research"),
        ("Data Researcher", "Data Researcher", "Research"),
        ("Market Researcher", "Market Researcher", "Research"),
        ("Senior Market Researcher", "Senior Market Researcher", "Research"),
        ("Research Analyst", "Research Analyst", "Research"),
        ("Senior Research Analyst", "Senior Research Analyst", "Research"),
        
        ("Senior Academic Researcher", "Senior Academic Researcher", "Research"),
        ("Academic Researcher", "Academic Researcher", "Research"),
        ("Postdoctoral Researcher", "Postdoctoral Researcher", "Research"),
        ("Research Associate", "Research Associate", "Research"),
        ("Senior Research Associate", "Senior Research Associate", "Research"),
        
        # Executive variations
        ("Senior Director", "Senior Director", "Executive"),
        ("Director", "Director", "Executive"),
        ("Executive Director", "Executive Director", "Executive"),
        ("Managing Director", "Managing Director", "Executive"),
        ("Senior Vice President", "Senior Vice President", "Executive"),
        ("Vice President", "Vice President", "Executive"),
        ("Executive Vice President", "Executive Vice President", "Executive"),
        ("Chief Executive Officer", "Chief Executive Officer", "Executive"),
        ("CEO", "CEO", "Executive"),
        ("Chief Operating Officer", "Chief Operating Officer", "Executive"),
        ("COO", "COO", "Executive"),
        ("Chief Technology Officer", "Chief Technology Officer", "Executive"),
        ("CTO", "CTO", "Executive"),
        ("Chief Information Officer", "Chief Information Officer", "Executive"),
        ("CIO", "CIO", "Executive"),
        ("Chief Financial Officer", "Chief Financial Officer", "Executive"),
        ("CFO", "CFO", "Executive"),
        ("Chief Marketing Officer", "Chief Marketing Officer", "Executive"),
        ("CMO", "CMO", "Executive"),
        ("Chief Human Resources Officer", "Chief Human Resources Officer", "Executive"),
        ("CHRO", "CHRO", "Executive"),
        
        # Education variations
        ("Senior Professor", "Senior Professor", "Education"),
        ("Professor", "Professor", "Education"),
        ("Associate Professor", "Associate Professor", "Education"),
        ("Assistant Professor", "Assistant Professor", "Education"),
        ("Senior Lecturer", "Senior Lecturer", "Education"),
        ("Lecturer", "Lecturer", "Education"),
        ("Senior Instructor", "Senior Instructor", "Education"),
        ("Instructor", "Instructor", "Education"),
        
        ("Senior Teacher", "Senior Teacher", "Education"),
        ("Teacher", "Teacher", "Education"),
        ("Lead Teacher", "Lead Teacher", "Education"),
        ("Principal", "Principal", "Education"),
        ("Vice Principal", "Vice Principal", "Education"),
        ("School Administrator", "School Administrator", "Education"),
        ("Education Administrator", "Education Administrator", "Education"),
        
        ("Senior Researcher", "Senior Researcher", "Education"),
        ("Researcher", "Researcher", "Education"),
        ("Academic Researcher", "Academic Researcher", "Education"),
        ("Senior Academic Researcher", "Senior Academic Researcher", "Education"),
        
        # Certification variations
        ("Senior Trainer", "Senior Trainer", "Certification"),
        ("Trainer", "Trainer", "Certification"),
        ("Lead Trainer", "Lead Trainer", "Certification"),
        ("Corporate Trainer", "Corporate Trainer", "Certification"),
        ("Technical Trainer", "Technical Trainer", "Certification"),
        ("Training Manager", "Training Manager", "Certification"),
        ("Senior Training Manager", "Senior Training Manager", "Certification"),
        
        ("Senior Consultant", "Senior Consultant", "Certification"),
        ("Consultant", "Consultant", "Certification"),
        ("Lead Consultant", "Lead Consultant", "Certification"),
        ("Principal Consultant", "Principal Consultant", "Certification"),
        ("Senior Management Consultant", "Senior Management Consultant", "Certification"),
        ("Management Consultant", "Management Consultant", "Certification"),
        ("Technical Consultant", "Technical Consultant", "Certification"),
        ("Senior Technical Consultant", "Senior Technical Consultant", "Certification"),
        
        ("Senior Auditor", "Senior Auditor", "Certification"),
        ("Auditor", "Auditor", "Certification"),
        ("Lead Auditor", "Lead Auditor", "Certification"),
        ("Senior Internal Auditor", "Senior Internal Auditor", "Certification"),
        ("Internal Auditor", "Internal Auditor", "Certification"),
        ("Senior External Auditor", "Senior External Auditor", "Certification"),
        ("External Auditor", "External Auditor", "Certification"),
    ]
    
    # Create DataFrame for additional titles
    additional_df = pd.DataFrame(additional_titles, columns=['raw_title', 'normalized_title', 'category'])
    
    # Combine with existing dataset
    combined_df = pd.concat([df, additional_df], ignore_index=True)
    
    # Remove duplicates
    combined_df = combined_df.drop_duplicates(subset=['raw_title'], keep='first')
    
    # Shuffle the dataset
    combined_df = combined_df.sample(frac=1, random_state=42).reset_index(drop=True)
    
    print(f"📊 Combined dataset: {len(combined_df)} rows")
    print(f"📊 Categories: {combined_df['category'].value_counts().to_dict()}")
    
    # Save expanded dataset
    combined_df.to_csv("data/enhanced_job_titles_expanded.csv", index=False)
    print(f"💾 Saved expanded dataset to: data/enhanced_job_titles_expanded.csv")
    
    # Retrain sklearn models
    print("\n🤖 RETRAINING SKLEARN MODELS")
    print("-" * 40)
    
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score, classification_report
    import pickle
    
    # Prepare data
    X = combined_df['raw_title']
    y = combined_df['category']
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Create TF-IDF vectorizer
    vectorizer = TfidfVectorizer(
        ngram_range=(1, 3),
        max_features=1000,
        stop_words='english',
        lowercase=True
    )
    
    # Fit and transform
    X_train_tfidf = vectorizer.fit_transform(X_train)
    X_test_tfidf = vectorizer.transform(X_test)
    
    # Train Logistic Regression
    model = LogisticRegression(
        max_iter=2000,
        random_state=42
    )
    
    model.fit(X_train_tfidf, y_train)
    
    # Predict and evaluate
    y_pred = model.predict(X_test_tfidf)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"📊 Test accuracy: {accuracy:.4f}")
    print(f"📊 Test accuracy: {accuracy:.2%}")
    
    # Check if accuracy meets requirement
    if accuracy >= 0.92:
        print("✅ Accuracy requirement met (>=92%)")
        success = True
    else:
        print(f"❌ Accuracy requirement not met ({accuracy:.2%} < 92%)")
        success = False
    
    # Save models
    os.makedirs("models", exist_ok=True)
    
    with open("models/job_category_model_expanded.pkl", "wb") as f:
        pickle.dump(model, f)
    
    with open("models/job_title_vectorizer_expanded.pkl", "wb") as f:
        pickle.dump(vectorizer, f)
    
    # Save normalization map
    normalization_map = dict(zip(combined_df['raw_title'], combined_df['normalized_title']))
    with open("models/normalization_map_expanded.pkl", "wb") as f:
        pickle.dump(normalization_map, f)
    
    print("💾 Models saved:")
    print("  - models/job_category_model_expanded.pkl")
    print("  - models/job_title_vectorizer_expanded.pkl")
    print("  - models/normalization_map_expanded.pkl")
    
    return success, len(combined_df), accuracy

if __name__ == "__main__":
    success, rows, accuracy = expand_job_titles_dataset()
    
    print("\n" + "=" * 60)
    print("JOB TITLES DATASET EXPANSION COMPLETE")
    print("=" * 60)
    print(f"Total rows: {rows}")
    print(f"Model accuracy: {accuracy:.2%}")
    print(f"Success: {'YES' if success else 'NO'}")
    print("=" * 60)
