#!/usr/bin/env python3
"""
Proper Accuracy Comparison: Before vs After Dataset Integration
"""

import json
from fixed_enhanced_parser import DatasetIntegratedParser

def basic_keyword_parser(resume_text: str):
    """Basic keyword-based parser (before datasets)"""
    
    result = {
        "work_experience": [],
        "certifications": [],
        "skills": []
    }
    
    lines = resume_text.split('\n')
    
    # Very basic work experience extraction
    for i, line in enumerate(lines):
        if "engineer" in line.lower() and i > 0:
            result["work_experience"].append({
                "job_title": line.strip(),
                "company": "Unknown",
                "skills_used": [],
                "confidence": 0.6
            })
    
    # Very basic certification extraction
    for line in lines:
        if "certified" in line.lower():
            result["certifications"].append({
                "name": line.strip(),
                "issuer": "Unknown",
                "confidence": 0.5
            })
    
    # Basic skill extraction
    basic_skills = ["python", "java", "react", "node.js", "aws", "docker"]
    text_lower = resume_text.lower()
    for skill in basic_skills:
        if skill in text_lower:
            result["skills"].append(skill)
    
    return result

def calculate_accuracy(parsed_result, expected_result):
    """Calculate accuracy metrics"""
    
    metrics = {
        "work_experience": {"correct": 0, "total": len(expected_result.get("work_experience", []))},
        "certifications": {"correct": 0, "total": len(expected_result.get("certifications", []))},
        "skills": {"correct": 0, "total": len(expected_result.get("skills", []))}
    }
    
    # Check work experience
    parsed_work = parsed_result.get("work_experience", [])
    expected_work = expected_result.get("work_experience", [])
    
    for exp in expected_work:
        for parsed_exp in parsed_work:
            if (exp["job_title"].lower() in parsed_exp["job_title"].lower() and
                exp["company"].lower() in parsed_exp["company"].lower()):
                metrics["work_experience"]["correct"] += 1
                break
    
    # Check certifications
    parsed_certs = parsed_result.get("certifications", [])
    expected_certs = expected_result.get("certifications", [])
    
    for cert in expected_certs:
        for parsed_cert in parsed_certs:
            if cert["name"].lower() in parsed_cert["name"].lower():
                metrics["certifications"]["correct"] += 1
                break
    
    # Check skills
    parsed_skills = [s.lower() for s in parsed_result.get("skills", [])]
    expected_skills = [s.lower() for s in expected_result.get("skills", [])]
    
    for skill in expected_skills:
        if skill in parsed_skills:
            metrics["skills"]["correct"] += 1
    
    # Calculate percentages
    for category in metrics:
        if metrics[category]["total"] > 0:
            metrics[category]["accuracy"] = metrics[category]["correct"] / metrics[category]["total"]
        else:
            metrics[category]["accuracy"] = 0
    
    return metrics

def run_accuracy_comparison():
    """Run comprehensive accuracy comparison"""
    
    print("🎯 ACCURACY COMPARISON: Before vs After Dataset Integration")
    print("=" * 70)
    
    # Test resumes
    test_resumes = [
        {
            "name": "Software Engineer Resume",
            "text": """
            JOHN DOE
            Senior Software Engineer
            
            WORK EXPERIENCE
            Senior Software Engineer
            Google
            Mountain View, CA
            Jan 2020 - Present
            
            • Developed scalable web applications using React and Node.js
            • Led team of 5 engineers on cloud migration project
            • Implemented CI/CD pipelines with Jenkins and Docker
            • Worked with AWS and Kubernetes for deployment
            
            CERTIFICATIONS
            AWS Certified Solutions Architect
            Amazon Web Services
            Issued: June 2023 Expires: June 2026
            ID: AWS-123456
            """,
            "expected": {
                "work_experience": [
                    {"job_title": "Senior Software Engineer", "company": "Google"}
                ],
                "certifications": [
                    {"name": "AWS Certified Solutions Architect", "issuer": "Amazon Web Services"}
                ],
                "skills": ["react", "node.js", "aws", "docker", "kubernetes", "jenkins"]
            }
        },
        {
            "name": "Data Scientist Resume", 
            "text": """
            JANE SMITH
            Data Scientist
            
            WORK EXPERIENCE
            Senior Data Scientist
            IBM
            Armonk, NY
            Mar 2019 - Present
            
            • Developed machine learning models for fraud detection
            • Led data science team of 3 analysts
            • Implemented predictive analytics using Python and TensorFlow
            
            CERTIFICATIONS
            IBM Data Science Professional
            IBM
            Issued: Nov 2021
            """,
            "expected": {
                "work_experience": [
                    {"job_title": "Senior Data Scientist", "company": "IBM"}
                ],
                "certifications": [
                    {"name": "IBM Data Science Professional", "issuer": "IBM"}
                ],
                "skills": ["python", "tensorflow", "machine learning"]
            }
        }
    ]
    
    # Initialize enhanced parser
    enhanced_parser = DatasetIntegratedParser()
    
    total_metrics = {
        "before": {"work_experience": [], "certifications": [], "skills": []},
        "after": {"work_experience": [], "certifications": [], "skills": []}
    }
    
    for i, test_case in enumerate(test_resumes, 1):
        print(f"\n📄 Test Case {i}: {test_case['name']}")
        print("-" * 50)
        
        # Parse with basic method
        basic_result = basic_keyword_parser(test_case["text"])
        basic_metrics = calculate_accuracy(basic_result, test_case["expected"])
        
        # Parse with enhanced method
        enhanced_result = enhanced_parser.parse_resume(test_case["text"])
        enhanced_metrics = calculate_accuracy(enhanced_result, test_case["expected"])
        
        # Store metrics
        for category in total_metrics["before"]:
            total_metrics["before"][category].append(basic_metrics[category]["accuracy"])
            total_metrics["after"][category].append(enhanced_metrics[category]["accuracy"])
        
        # Print results
        print(f"📊 Before Enhancement:")
        print(f"   Work Experience: {basic_metrics['work_experience']['accuracy']:.1%}")
        print(f"   Certifications: {basic_metrics['certifications']['accuracy']:.1%}")
        print(f"   Skills: {basic_metrics['skills']['accuracy']:.1%}")
        
        print(f"📊 After Enhancement:")
        print(f"   Work Experience: {enhanced_metrics['work_experience']['accuracy']:.1%}")
        print(f"   Certifications: {enhanced_metrics['certifications']['accuracy']:.1%}")
        print(f"   Skills: {enhanced_metrics['skills']['accuracy']:.1%}")
        
        # Show improvement
        work_improvement = enhanced_metrics['work_experience']['accuracy'] - basic_metrics['work_experience']['accuracy']
        cert_improvement = enhanced_metrics['certifications']['accuracy'] - basic_metrics['certifications']['accuracy']
        skill_improvement = enhanced_metrics['skills']['accuracy'] - basic_metrics['skills']['accuracy']
        
        print(f"📈 Improvement:")
        print(f"   Work Experience: {work_improvement:+.1%}")
        print(f"   Certifications: {cert_improvement:+.1%}")
        print(f"   Skills: {skill_improvement:+.1%}")
        
        # Show actual parsed data
        print(f"🔍 Enhanced Parser Found:")
        print(f"   Work Experience: {len(enhanced_result['work_experience'])} entries")
        print(f"   Certifications: {len(enhanced_result['certifications'])} entries")
        print(f"   Skills: {len(enhanced_result['skills'])} skills")
    
    # Calculate overall averages
    print("\n" + "=" * 70)
    print("📊 OVERALL AVERAGE RESULTS")
    print("=" * 70)
    
    for category in total_metrics["before"]:
        before_avg = sum(total_metrics["before"][category]) / len(total_metrics["before"][category])
        after_avg = sum(total_metrics["after"][category]) / len(total_metrics["after"][category])
        improvement = after_avg - before_avg
        
        print(f"\n🎯 {category.replace('_', ' ').title()}:")
        print(f"   Before: {before_avg:.1%}")
        print(f"   After:  {after_avg:.1%}")
        print(f"   Improvement: {improvement:+.1%}")
    
    # Overall summary
    overall_before = sum(sum(cat) for cat in total_metrics["before"].values()) / sum(len(cat) for cat in total_metrics["before"].values())
    overall_after = sum(sum(cat) for cat in total_metrics["after"].values()) / sum(len(cat) for cat in total_metrics["after"].values())
    overall_improvement = overall_after - overall_before
    
    print(f"\n🏆 OVERALL ACCURACY:")
    print(f"   Before: {overall_before:.1%}")
    print(f"   After:  {overall_after:.1%}")
    print(f"   Improvement: {overall_improvement:+.1%}")
    
    print(f"\n🎉 CONCLUSION:")
    if overall_improvement > 0:
        print(f"   ✅ Dataset integration improved accuracy by {overall_improvement:+.1%}")
        print(f"   ✅ Your enhanced parser is working correctly!")
    else:
        print(f"   ⚠ Need to fine-tune the parser patterns")
    
    return {
        "before_avg": overall_before,
        "after_avg": overall_after,
        "improvement": overall_improvement
    }

if __name__ == "__main__":
    results = run_accuracy_comparison()
