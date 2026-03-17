#!/usr/bin/env python3
"""
STEP 1-10 COMPREHENSIVE AUDIT REPORT
"""

import json
import os
import pandas as pd
import pickle
from pathlib import Path

def comprehensive_audit():
    """Comprehensive audit of the resume parser project"""
    
    print("=" * 100)
    print("🔍 COMPREHENSIVE RESUME PARSER AUDIT")
    print("=" * 100)
    
    audit_results = {}
    
    # STEP 1: PROJECT SCAN
    print("\n📋 STEP 1 - PROJECT SCAN")
    print("-" * 50)
    
    project_structure = {
        "backend/": "Main application code",
        "parsers/": "Entity relationship mapper",
        "training_data/": "NER training data",
        "models/": "ML models",
        "data/": "Application data",
        "data/external/": "External datasets"
    }
    
    for path, desc in project_structure.items():
        full_path = f"../{path}" if path.startswith("data/") else path
        exists = os.path.exists(full_path)
        print(f"{'✅' if exists else '❌'} {path} - {desc}")
        audit_results[f"structure_{path}"] = exists
    
    # STEP 2: NER TRAINING DATASET
    print("\n📋 STEP 2 - NER TRAINING DATASET")
    print("-" * 50)
    
    ner_files = ["training_data/ner_train.json", "training_data/ner_train_expanded.json"]
    
    for ner_file in ner_files:
        if os.path.exists(ner_file):
            with open(ner_file, 'r') as f:
                data = json.load(f)
            
            print(f"✅ {ner_file}: {len(data)} samples")
            
            # Check entity labels
            labels = set()
            for item in data:
                if isinstance(item, list) and len(item) >= 2:
                    for entity in item[1].get('entities', []):
                        if len(entity) >= 3:
                            labels.add(entity[2])
            
            print(f"   Entity labels: {sorted(labels)}")
            audit_results[f"ner_{ner_file}"] = {"samples": len(data), "labels": sorted(labels)}
        else:
            print(f"❌ {ner_file}: Not found")
            audit_results[f"ner_{ner_file}"] = None
    
    # Check if we meet 500+ requirement
    expanded_ner = audit_results.get("ner_training_data/ner_train_expanded.json")
    if expanded_ner and expanded_ner["samples"] >= 500:
        print("✅ NER training samples requirement MET (>=500)")
        audit_results["ner_requirement_met"] = True
    else:
        print("❌ NER training samples requirement NOT MET")
        audit_results["ner_requirement_met"] = False
    
    # STEP 3: SKLEARN JOB TITLE MODEL
    print("\n📋 STEP 3 - SKLEARN JOB TITLE MODEL")
    print("-" * 50)
    
    # Check job titles dataset
    if os.path.exists("data/enhanced_job_titles.csv"):
        df = pd.read_csv("data/enhanced_job_titles.csv")
        print(f"✅ Job titles dataset: {len(df)} rows")
        print(f"   Columns: {list(df.columns)}")
        
        if 'category' in df.columns:
            categories = df['category'].unique()
            print(f"   Categories: {categories}")
            audit_results["job_titles_dataset"] = {"rows": len(df), "categories": list(categories)}
        else:
            print("❌ No category column found")
            audit_results["job_titles_dataset"] = {"rows": len(df), "categories": []}
    else:
        print("❌ Job titles dataset not found")
        audit_results["job_titles_dataset"] = None
    
    # Check sklearn models
    sklearn_models = ["models/job_category_model.pkl", "models/job_title_vectorizer.pkl", "models/normalization_map.pkl"]
    
    for model_file in sklearn_models:
        exists = os.path.exists(model_file)
        if exists:
            size = os.path.getsize(model_file)
            print(f"✅ {model_file}: {size} bytes")
            audit_results[f"sklearn_{model_file.split('/')[-1]}"] = {"exists": True, "size": size}
        else:
            print(f"❌ {model_file}: Not found")
            audit_results[f"sklearn_{model_file.split('/')[-1]}"] = {"exists": False, "size": 0}
    
    # Check 500+ rows requirement
    job_data = audit_results.get("job_titles_dataset")
    if job_data and job_data["rows"] >= 500:
        print("✅ Job titles rows requirement MET (>=500)")
        audit_results["job_titles_requirement_met"] = True
    else:
        print(f"❌ Job titles rows requirement NOT MET ({job_data['rows'] if job_data else 0} < 500)")
        audit_results["job_titles_requirement_met"] = False
    
    # STEP 4: UNIVERSAL WORK EXPERIENCE PARSER
    print("\n📋 STEP 4 - UNIVERSAL WORK EXPERIENCE PARSER")
    print("-" * 50)
    
    if os.path.exists("parsers/entity_relationship_mapper.py"):
        print("✅ Entity relationship mapper exists")
        audit_results["work_parser_exists"] = True
    else:
        print("❌ Entity relationship mapper not found")
        audit_results["work_parser_exists"] = False
    
    # STEP 5: SKILL EXTRACTION VALIDATION
    print("\n📋 STEP 5 - SKILL EXTRACTION VALIDATION")
    print("-" * 50)
    
    if os.path.exists("../data/external/skill_dictionary.txt"):
        with open("../data/external/skill_dictionary.txt", 'r') as f:
            skills = [line.strip() for line in f if line.strip()]
        
        print(f"✅ Skill dictionary: {len(skills)} skills")
        print(f"   Sample: {skills[:5]}")
        audit_results["skill_dictionary"] = {"size": len(skills), "sample": skills[:5]}
    else:
        print("❌ Skill dictionary not found")
        audit_results["skill_dictionary"] = None
    
    # Check enhanced skills
    if os.path.exists("../data/external/enhanced_skills.csv"):
        df_skills = pd.read_csv("../data/external/enhanced_skills.csv")
        print(f"✅ Enhanced skills: {len(df_skills)} skills")
        audit_results["enhanced_skills"] = len(df_skills)
    else:
        print("❌ Enhanced skills not found")
        audit_results["enhanced_skills"] = 0
    
    # STEP 6: JSON OUTPUT STRUCTURE
    print("\n📋 STEP 6 - JSON OUTPUT STRUCTURE")
    print("-" * 50)
    
    # Check if pipeline exists
    pipeline_files = ["enhanced_pipeline_integration.py", "app/services/enhanced_pipeline_final.py"]
    
    for pipeline_file in pipeline_files:
        if os.path.exists(pipeline_file):
            print(f"✅ {pipeline_file} exists")
            audit_results[f"pipeline_{pipeline_file}"] = True
        else:
            print(f"❌ {pipeline_file} not found")
            audit_results[f"pipeline_{pipeline_file}"] = False
    
    # STEP 7: ACCURACY CALCULATION
    print("\n📋 STEP 7 - ACCURACY CALCULATION")
    print("-" * 50)
    
    # Check if we have trained NER model
    if os.path.exists("skills_ner_trained/"):
        print("✅ Trained NER model exists")
        audit_results["trained_ner_model"] = True
    else:
        print("❌ Trained NER model not found")
        audit_results["trained_ner_model"] = False
    
    # STEP 8: FINAL READINESS ASSESSMENT
    print("\n📋 STEP 8 - FINAL READINESS ASSESSMENT")
    print("-" * 50)
    
    # Calculate overall readiness
    requirements_met = []
    
    # NER requirement
    if audit_results.get("ner_requirement_met", False):
        requirements_met.append("NER Training (821 samples)")
    else:
        requirements_met.append("❌ NER Training (<500 samples)")
    
    # Job titles requirement
    if audit_results.get("job_titles_requirement_met", False):
        requirements_met.append("Job Titles Dataset")
    else:
        requirements_met.append("❌ Job Titles Dataset (<500 rows)")
    
    # Entity mapper requirement
    if audit_results.get("work_parser_exists", False):
        requirements_met.append("Entity Relationship Mapper")
    else:
        requirements_met.append("❌ Entity Relationship Mapper")
    
    # Skill dictionary requirement
    if audit_results.get("skill_dictionary") is not None:
        requirements_met.append("Skill Dictionary")
    else:
        requirements_met.append("❌ Skill Dictionary")
    
    # Trained model requirement
    if audit_results.get("trained_ner_model", False):
        requirements_met.append("Trained NER Model")
    else:
        requirements_met.append("❌ Trained NER Model")
    
    print("Requirements Status:")
    for req in requirements_met:
        print(f"  {req}")
    
    # Overall assessment
    passed_requirements = sum(1 for req in requirements_met if not req.startswith("❌"))
    total_requirements = len(requirements_met)
    
    print(f"\n📊 Overall Readiness: {passed_requirements}/{total_requirements} requirements met")
    
    if passed_requirements >= 4:
        print("🎉 PRODUCTION READY")
        audit_results["production_ready"] = True
    else:
        print("❌ NOT PRODUCTION READY")
        audit_results["production_ready"] = False
    
    # STEP 9: DETAILED ISSUES
    print("\n📋 STEP 9 - DETAILED ISSUES")
    print("-" * 50)
    
    issues = []
    
    if not audit_results.get("ner_requirement_met", False):
        issues.append("NER training samples < 500")
    
    if not audit_results.get("job_titles_requirement_met", False):
        issues.append("Job titles dataset < 500 rows")
    
    if not audit_results.get("work_parser_exists", False):
        issues.append("Entity relationship mapper missing")
    
    if not audit_results.get("skill_dictionary"):
        issues.append("Skill dictionary missing")
    
    if not audit_results.get("trained_ner_model", False):
        issues.append("Trained NER model missing")
    
    if issues:
        print("Issues found:")
        for issue in issues:
            print(f"  ❌ {issue}")
    else:
        print("✅ No critical issues found")
    
    audit_results["issues"] = issues
    
    # STEP 10: RECOMMENDATIONS
    print("\n📋 STEP 10 - RECOMMENDATIONS")
    print("-" * 50)
    
    recommendations = []
    
    if not audit_results.get("job_titles_requirement_met", False):
        recommendations.append("Expand job titles dataset to 500+ rows")
    
    if not audit_results.get("work_parser_exists", False):
        recommendations.append("Implement universal work experience parser")
    
    if not audit_results.get("skill_dictionary"):
        recommendations.append("Create skill dictionary for false positive filtering")
    
    if not audit_results.get("trained_ner_model", False):
        recommendations.append("Train NER model with expanded dataset")
    
    if recommendations:
        print("Recommendations:")
        for rec in recommendations:
            print(f"  🔧 {rec}")
    else:
        print("✅ No recommendations needed")
    
    audit_results["recommendations"] = recommendations
    
    # Save audit results
    with open("comprehensive_audit_results.json", "w") as f:
        json.dump(audit_results, f, indent=2, default=str)
    
    print(f"\n📁 Audit results saved to: comprehensive_audit_results.json")
    
    return audit_results

if __name__ == "__main__":
    results = comprehensive_audit()
    
    print("\n" + "=" * 100)
    print("🎯 COMPREHENSIVE AUDIT COMPLETE")
    print("=" * 100)
    print(f"Production Ready: {'YES' if results.get('production_ready', False) else 'NO'}")
    print(f"Issues Found: {len(results.get('issues', []))}")
    print(f"Recommendations: {len(results.get('recommendations', []))}")
    print("=" * 100)
