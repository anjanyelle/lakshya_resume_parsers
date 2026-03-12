#!/usr/bin/env python3
"""
Resume Parser Accuracy Comparison Tool
Compare accuracy before and after enhanced datasets integration
"""

import json
import pandas as pd
from pathlib import Path
from typing import Dict, List, Tuple
from enhanced_work_cert_parser import WorkExperienceParser, CertificationParser
from enhanced_resume_integration import EnhancedResumeParser

class AccuracyComparison:
    """Compare parsing accuracy before and after enhancement"""
    
    def __init__(self):
        self.enhanced_parser = EnhancedResumeParser()
        self.test_results = {
            "before_enhancement": [],
            "after_enhancement": []
        }
    
    def load_test_resumes(self, resume_file: str = None, sample_text: str = None) -> List[Dict]:
        """Load test resumes for comparison"""
        
        if sample_text:
            return [{"text": sample_text, "id": "sample_1"}]
        
        # Use sample resume data
        sample_resumes = [
            {
                "id": "test_1",
                "text": """
                JOHN DOE
                Senior Software Engineer
                john.doe@email.com | (555) 123-4567 | LinkedIn: johndoe
                
                WORK EXPERIENCE
                Senior Software Engineer
                Google
                Mountain View, CA
                Jan 2020 - Present
                
                • Developed scalable web applications using React and Node.js
                • Led team of 5 engineers on cloud migration project
                • Implemented CI/CD pipelines with Jenkins and Docker
                • Worked with AWS and Kubernetes for deployment
                
                Software Engineer
                Microsoft
                Redmond, WA
                Jun 2018 - Dec 2019
                
                • Built RESTful APIs using Python and Django
                • Optimized database queries improving performance by 40%
                • Collaborated with cross-functional teams on feature development
                
                CERTIFICATIONS
                AWS Certified Solutions Architect
                Amazon Web Services
                Issued: June 2023 Expires: June 2026
                ID: AWS-123456
                
                Google Cloud Professional Architect
                Google Cloud
                Issued: March 2022 Expires: March 2025
                ID: GCP-789012
                
                EDUCATION
                Bachelor of Science in Computer Science
                Stanford University
                2014-2018
                
                SKILLS
                Python, JavaScript, React, Node.js, AWS, Docker, Kubernetes, 
                Jenkins, Git, SQL, NoSQL, MongoDB, PostgreSQL
                """
            },
            {
                "id": "test_2", 
                "text": """
                JANE SMITH
                Data Scientist
                jane.smith@email.com | (555) 987-6543
                
                WORK EXPERIENCE
                Senior Data Scientist
                IBM
                Armonk, NY
                Mar 2019 - Present
                
                • Developed machine learning models for fraud detection
                • Led data science team of 3 analysts
                • Implemented predictive analytics using Python and TensorFlow
                • Created data pipelines using Apache Spark
                
                Data Analyst
                Amazon
                Seattle, WA
                Aug 2017 - Feb 2019
                
                • Analyzed large datasets using SQL and Python
                • Built dashboards using Tableau and Power BI
                • Generated insights for business strategy
                
                CERTIFICATIONS
                IBM Data Science Professional
                IBM
                Issued: Nov 2021
                
                Google Data Analytics Professional Certificate
                Google
                Issued: May 2020
                
                Microsoft Certified: Azure Data Scientist
                Microsoft
                Issued: Aug 2022
                """
            }
        ]
        
        return sample_resumes
    
    def parse_with_basic_method(self, resume_text: str) -> Dict:
        """Simulate basic parsing (before enhancement)"""
        
        # Basic keyword-based extraction (simplified)
        basic_result = {
            "work_experience": [],
            "certifications": [],
            "skills": [],
            "parsing_method": "basic_keyword"
        }
        
        lines = resume_text.split('\n')
        current_section = None
        current_entry = {}
        
        for line in lines:
            line = line.strip()
            
            if "WORK EXPERIENCE" in line.upper():
                current_section = "work"
                continue
            elif "CERTIFICATIONS" in line.upper():
                current_section = "certifications"
                continue
            elif "SKILLS" in line.upper():
                current_section = "skills"
                continue
            
            if current_section == "work" and line:
                if not any(char.isdigit() for char in line):  # Not a date line
                    if "Engineer" in line or "Scientist" in line or "Analyst" in line:
                        current_entry["job_title"] = line
                    elif "Google" in line or "Microsoft" in line or "IBM" in line or "Amazon" in line:
                        current_entry["company"] = line
                        basic_result["work_experience"].append(current_entry.copy())
                        current_entry = {}
            
            elif current_section == "certifications" and line:
                if "Certified" in line or "Professional" in line:
                    basic_result["certifications"].append({
                        "name": line,
                        "issuer": "Unknown",
                        "confidence": 0.6
                    })
            
            elif current_section == "skills" and line:
                skills = [skill.strip() for skill in line.split(',')]
                basic_result["skills"].extend(skills)
        
        return basic_result
    
    def parse_with_enhanced_method(self, resume_text: str) -> Dict:
        """Parse with enhanced method (after enhancement)"""
        
        enhanced_result = self.enhanced_parser.parse_resume_sections(resume_text)
        enhanced_result["parsing_method"] = "enhanced_kickresume"
        
        return enhanced_result
    
    def evaluate_accuracy(self, parsed_result: Dict, expected_result: Dict) -> Dict:
        """Evaluate parsing accuracy against expected results"""
        
        metrics = {
            "work_experience_accuracy": 0.0,
            "certifications_accuracy": 0.0,
            "skills_accuracy": 0.0,
            "overall_accuracy": 0.0,
            "details": {
                "work_experience": {"correct": 0, "total": 0},
                "certifications": {"correct": 0, "total": 0},
                "skills": {"correct": 0, "total": 0}
            }
        }
        
        # Evaluate work experience
        parsed_work = parsed_result.get("work_experience", [])
        expected_work = expected_result.get("work_experience", [])
        
        work_correct = 0
        for exp in expected_work:
            for parsed_exp in parsed_work:
                if (self._normalize_text(exp.get("job_title", "")) in 
                    self._normalize_text(parsed_exp.get("job_title", "")) and
                    self._normalize_text(exp.get("company", "")) in 
                    self._normalize_text(parsed_exp.get("company", ""))):
                    work_correct += 1
                    break
        
        metrics["details"]["work_experience"]["correct"] = work_correct
        metrics["details"]["work_experience"]["total"] = len(expected_work)
        metrics["work_experience_accuracy"] = work_correct / len(expected_work) if expected_work else 0
        
        # Evaluate certifications
        parsed_certs = parsed_result.get("certifications", [])
        expected_certs = expected_result.get("certifications", [])
        
        cert_correct = 0
        for cert in expected_certs:
            for parsed_cert in parsed_certs:
                if (self._normalize_text(cert.get("name", "")) in 
                    self._normalize_text(parsed_cert.get("name", ""))):
                    cert_correct += 1
                    break
        
        metrics["details"]["certifications"]["correct"] = cert_correct
        metrics["details"]["certifications"]["total"] = len(expected_certs)
        metrics["certifications_accuracy"] = cert_correct / len(expected_certs) if expected_certs else 0
        
        # Calculate overall accuracy
        total_correct = (metrics["details"]["work_experience"]["correct"] + 
                        metrics["details"]["certifications"]["correct"])
        total_items = (metrics["details"]["work_experience"]["total"] + 
                      metrics["details"]["certifications"]["total"])
        
        metrics["overall_accuracy"] = total_correct / total_items if total_items > 0 else 0
        
        return metrics
    
    def _normalize_text(self, text: str) -> str:
        """Normalize text for comparison"""
        if not text:
            return ""
        return text.lower().replace(" ", "").replace(",", "").replace(".", "")
    
    def run_comparison(self, sample_text: str = None) -> Dict:
        """Run full accuracy comparison"""
        
        print("🔍 Running Resume Parser Accuracy Comparison...")
        print("=" * 60)
        
        # Load test resumes
        test_resumes = self.load_test_resumes(sample_text=sample_text)
        
        # Expected results (ground truth)
        expected_results = {
            "test_1": {
                "work_experience": [
                    {"job_title": "Senior Software Engineer", "company": "Google"},
                    {"job_title": "Software Engineer", "company": "Microsoft"}
                ],
                "certifications": [
                    {"name": "AWS Certified Solutions Architect"},
                    {"name": "Google Cloud Professional Architect"}
                ]
            },
            "test_2": {
                "work_experience": [
                    {"job_title": "Senior Data Scientist", "company": "IBM"},
                    {"job_title": "Data Analyst", "company": "Amazon"}
                ],
                "certifications": [
                    {"name": "IBM Data Science Professional"},
                    {"name": "Google Data Analytics Professional Certificate"},
                    {"name": "Microsoft Certified: Azure Data Scientist"}
                ]
            }
        }
        
        comparison_results = {
            "test_cases": [],
            "summary": {
                "before_enhancement": {"avg_accuracy": 0.0, "work_exp": 0.0, "certs": 0.0},
                "after_enhancement": {"avg_accuracy": 0.0, "work_exp": 0.0, "certs": 0.0},
                "improvement": {"overall": 0.0, "work_exp": 0.0, "certs": 0.0}
            }
        }
        
        for resume in test_resumes:
            resume_id = resume["id"]
            resume_text = resume["text"]
            expected = expected_results.get(resume_id, {})
            
            print(f"\n📄 Testing Resume: {resume_id}")
            print("-" * 40)
            
            # Parse with basic method
            basic_result = self.parse_with_basic_method(resume_text)
            basic_metrics = self.evaluate_accuracy(basic_result, expected)
            
            # Parse with enhanced method
            enhanced_result = self.parse_with_enhanced_method(resume_text)
            enhanced_metrics = self.evaluate_accuracy(enhanced_result, expected)
            
            # Store results
            test_result = {
                "resume_id": resume_id,
                "before_enhancement": {
                    "metrics": basic_metrics,
                    "parsed": basic_result
                },
                "after_enhancement": {
                    "metrics": enhanced_metrics,
                    "parsed": enhanced_result
                },
                "improvement": {
                    "overall": enhanced_metrics["overall_accuracy"] - basic_metrics["overall_accuracy"],
                    "work_experience": enhanced_metrics["work_experience_accuracy"] - basic_metrics["work_experience_accuracy"],
                    "certifications": enhanced_metrics["certifications_accuracy"] - basic_metrics["certifications_accuracy"]
                }
            }
            
            comparison_results["test_cases"].append(test_result)
            
            # Print results for this test case
            print(f"📊 Before Enhancement:")
            print(f"   Overall Accuracy: {basic_metrics['overall_accuracy']:.2%}")
            print(f"   Work Experience: {basic_metrics['work_experience_accuracy']:.2%}")
            print(f"   Certifications: {basic_metrics['certifications_accuracy']:.2%}")
            
            print(f"📊 After Enhancement:")
            print(f"   Overall Accuracy: {enhanced_metrics['overall_accuracy']:.2%}")
            print(f"   Work Experience: {enhanced_metrics['work_experience_accuracy']:.2%}")
            print(f"   Certifications: {enhanced_metrics['certifications_accuracy']:.2%}")
            
            print(f"📈 Improvement:")
            print(f"   Overall: +{test_result['improvement']['overall']:.2%}")
            print(f"   Work Experience: +{test_result['improvement']['work_experience']:.2%}")
            print(f"   Certifications: +{test_result['improvement']['certifications']:.2%}")
        
        # Calculate summary statistics
        total_before_accuracy = sum(case["before_enhancement"]["metrics"]["overall_accuracy"] for case in comparison_results["test_cases"])
        total_after_accuracy = sum(case["after_enhancement"]["metrics"]["overall_accuracy"] for case in comparison_results["test_cases"])
        total_before_work = sum(case["before_enhancement"]["metrics"]["work_experience_accuracy"] for case in comparison_results["test_cases"])
        total_after_work = sum(case["after_enhancement"]["metrics"]["work_experience_accuracy"] for case in comparison_results["test_cases"])
        total_before_certs = sum(case["before_enhancement"]["metrics"]["certifications_accuracy"] for case in comparison_results["test_cases"])
        total_after_certs = sum(case["after_enhancement"]["metrics"]["certifications_accuracy"] for case in comparison_results["test_cases"])
        
        num_tests = len(comparison_results["test_cases"])
        
        comparison_results["summary"]["before_enhancement"]["avg_accuracy"] = total_before_accuracy / num_tests
        comparison_results["summary"]["after_enhancement"]["avg_accuracy"] = total_after_accuracy / num_tests
        comparison_results["summary"]["before_enhancement"]["work_exp"] = total_before_work / num_tests
        comparison_results["summary"]["after_enhancement"]["work_exp"] = total_after_work / num_tests
        comparison_results["summary"]["before_enhancement"]["certs"] = total_before_certs / num_tests
        comparison_results["summary"]["after_enhancement"]["certs"] = total_after_certs / num_tests
        
        comparison_results["summary"]["improvement"]["overall"] = (
            comparison_results["summary"]["after_enhancement"]["avg_accuracy"] - 
            comparison_results["summary"]["before_enhancement"]["avg_accuracy"]
        )
        comparison_results["summary"]["improvement"]["work_exp"] = (
            comparison_results["summary"]["after_enhancement"]["work_exp"] - 
            comparison_results["summary"]["before_enhancement"]["work_exp"]
        )
        comparison_results["summary"]["improvement"]["certs"] = (
            comparison_results["summary"]["after_enhancement"]["certs"] - 
            comparison_results["summary"]["before_enhancement"]["certs"]
        )
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 SUMMARY COMPARISON")
        print("=" * 60)
        print(f"📈 Overall Accuracy Improvement: {comparison_results['summary']['improvement']['overall']:.2%}")
        print(f"   Before: {comparison_results['summary']['before_enhancement']['avg_accuracy']:.2%}")
        print(f"   After:  {comparison_results['summary']['after_enhancement']['avg_accuracy']:.2%}")
        
        print(f"\n💼 Work Experience Accuracy Improvement: {comparison_results['summary']['improvement']['work_exp']:.2%}")
        print(f"   Before: {comparison_results['summary']['before_enhancement']['work_exp']:.2%}")
        print(f"   After:  {comparison_results['summary']['after_enhancement']['work_exp']:.2%}")
        
        print(f"\n🎓 Certification Accuracy Improvement: {comparison_results['summary']['improvement']['certs']:.2%}")
        print(f"   Before: {comparison_results['summary']['before_enhancement']['certs']:.2%}")
        print(f"   After:  {comparison_results['summary']['after_enhancement']['certs']:.2%}")
        
        return comparison_results
    
    def save_results(self, results: Dict, filename: str = "accuracy_comparison_results.json"):
        """Save comparison results to file"""
        
        output_path = Path("data/results") / filename
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n💾 Results saved to: {output_path}")


def main():
    """Main function to run accuracy comparison"""
    
    # You can either:
    # 1. Test with sample resumes (default)
    # 2. Test with your own resume text
    
    # Option 1: Test with sample resumes
    comparison = AccuracyComparison()
    results = comparison.run_comparison()
    comparison.save_results(results)
    
    # Option 2: Test with your own resume
    # your_resume_text = """
    # Paste your resume text here...
    # """
    # comparison = AccuracyComparison()
    # results = comparison.run_comparison(sample_text=your_resume_text)
    # comparison.save_results(results)


if __name__ == "__main__":
    main()
