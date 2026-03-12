#!/usr/bin/env python3
"""
Fixed Enhanced Resume Parser with Dataset Integration
Actually uses the downloaded datasets for better accuracy
"""

import json
import pandas as pd
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

class DatasetIntegratedParser:
    """Enhanced parser that actually uses the downloaded datasets"""
    
    def __init__(self):
        self.load_datasets()
        self.setup_patterns()
    
    def load_datasets(self):
        """Load all downloaded datasets"""
        base_path = Path("data/external")
        
        # Load certification datasets
        try:
            self.coursera_df = pd.read_csv(base_path / "certifications" / "coursera_courses.csv")
            self.sample_certs_df = pd.read_csv(base_path / "certifications" / "sample_certifications.csv")
            print(f"✅ Loaded {len(self.coursera_df)} Coursera courses")
            print(f"✅ Loaded {len(self.sample_certs_df)} sample certifications")
        except Exception as e:
            print(f"⚠ Could not load certification datasets: {e}")
            self.coursera_df = pd.DataFrame()
            self.sample_certs_df = pd.DataFrame()
        
        # Load work experience dataset
        try:
            self.resume_df = pd.read_csv(base_path / "work_experience" / "resume_classification_dataset" / "Dataset.csv")
            print(f"✅ Loaded {len(self.resume_df)} resume samples")
        except Exception as e:
            print(f"⚠ Could not load resume dataset: {e}")
            self.resume_df = pd.DataFrame()
        
        # Load company data
        try:
            fortune500_path = base_path / "companies" / "fortune500_companies" / "csv" / "fortune500-2019.csv"
            self.companies_df = pd.read_csv(fortune500_path)
            print(f"✅ Loaded {len(self.companies_df)} Fortune 500 companies")
        except Exception as e:
            print(f"⚠ Could not load company dataset: {e}")
            self.companies_df = pd.DataFrame()
        
        # Load skills data
        try:
            self.skills_df = pd.read_csv(base_path / "skills" / "job_matching_skills.csv")
            print(f"✅ Loaded {len(self.skills_df)} job-skill mappings")
        except Exception as e:
            print(f"⚠ Could not load skills dataset: {e}")
            self.skills_df = pd.DataFrame()
    
    def setup_patterns(self):
        """Setup parsing patterns using datasets"""
        
        # Build certification patterns from datasets
        self.certification_patterns = {}
        if not self.coursera_df.empty:
            for _, row in self.coursera_df.iterrows():
                cert_name = str(row.get('course_title', '')).strip()
                if cert_name:
                    self.certification_patterns[cert_name.lower()] = cert_name
        
        if not self.sample_certs_df.empty:
            for _, row in self.sample_certs_df.iterrows():
                cert_name = str(row.get('certification_name', '')).strip()
                if cert_name:
                    self.certification_patterns[cert_name.lower()] = cert_name
        
        # Build company patterns from dataset
        self.company_patterns = {}
        if not self.companies_df.empty:
            for _, row in self.companies_df.iterrows():
                company = str(row.get('company', '')).strip()
                if company:
                    self.company_patterns[company.lower()] = company
        
        # Build job title patterns from resume dataset
        self.job_title_patterns = {}
        if not self.resume_df.empty:
            categories = self.resume_df['Category'].value_counts()
            for category in categories.index:
                self.job_title_patterns[category.lower()] = category
    
    def normalize_job_title(self, title: str) -> str:
        """Normalize job title using dataset patterns"""
        if not title:
            return ""
        
        title_lower = title.lower().strip()
        
        # Check against known job titles from dataset
        for known_title in self.job_title_patterns:
            if known_title in title_lower or title_lower in known_title:
                return self.job_title_patterns[known_title]
        
        # Common normalization rules
        title = title.replace("Sr.", "Senior").replace("Jr.", "Junior")
        title = title.replace("Mgr.", "Manager").replace("Dir.", "Director")
        
        return title.strip()
    
    def normalize_company_name(self, company: str) -> str:
        """Normalize company name using dataset patterns"""
        if not company:
            return ""
        
        company_lower = company.lower().strip()
        
        # Check against known companies from dataset
        for known_company in self.company_patterns:
            if known_company in company_lower or company_lower in known_company:
                return self.company_patterns[known_company]
        
        # Common company name mappings
        mappings = {
            "aws": "Amazon Web Services",
            "google": "Google",
            "microsoft": "Microsoft", 
            "apple": "Apple",
            "meta": "Meta",
            "facebook": "Meta",
            "ibm": "IBM",
            "oracle": "Oracle"
        }
        
        for key, value in mappings.items():
            if key in company_lower:
                return value
        
        return company.strip()
    
    def normalize_certification_name(self, name: str) -> str:
        """Normalize certification name using dataset patterns"""
        if not name:
            return ""
        
        name_lower = name.lower().strip()
        
        # Check against known certifications from datasets
        for known_cert in self.certification_patterns:
            if known_cert in name_lower or name_lower in known_cert:
                return self.certification_patterns[known_cert]
        
        return name.strip()
    
    def extract_certification_issuer(self, cert_name: str) -> str:
        """Extract issuer using dataset patterns"""
        if not cert_name:
            return ""
        
        cert_lower = cert_name.lower()
        
        # Check Coursera dataset for issuer
        if not self.coursera_df.empty:
            for _, row in self.coursera_df.iterrows():
                course_title = str(row.get('course_title', '')).lower()
                organization = str(row.get('course_organization', '')).strip()
                if course_title in cert_lower and organization:
                    return organization
        
        # Check sample certifications for issuer
        if not self.sample_certs_df.empty:
            for _, row in self.sample_certs_df.iterrows():
                cert_name_match = str(row.get('certification_name', '')).lower()
                issuer = str(row.get('issuer', '')).strip()
                if cert_name_match in cert_lower and issuer:
                    return issuer
        
        # Common issuer patterns
        issuer_patterns = {
            "amazon": "Amazon Web Services",
            "google": "Google",
            "microsoft": "Microsoft",
            "ibm": "IBM",
            "oracle": "Oracle",
            "comptia": "CompTIA",
            "pmi": "PMI",
            "cisco": "Cisco"
        }
        
        for pattern, issuer in issuer_patterns.items():
            if pattern in cert_lower:
                return issuer
        
        return "Unknown"
    
    def extract_skills_from_text(self, text: str) -> List[str]:
        """Extract skills using dataset patterns"""
        if not text:
            return []
        
        text_lower = text.lower()
        found_skills = []
        
        # Extract skills from job descriptions dataset
        if not self.skills_df.empty:
            for _, row in self.skills_df.iterrows():
                job_desc = str(row.get('Job Description', '')).lower()
                # Look for skill patterns in job descriptions
                words = job_desc.split()
                for word in words:
                    if len(word) > 3 and word in text_lower and word not in found_skills:
                        found_skills.append(word)
        
        # Common technical skills
        tech_skills = [
            "python", "java", "javascript", "react", "angular", "vue", "node.js",
            "aws", "azure", "gcp", "docker", "kubernetes", "jenkins", "git",
            "sql", "nosql", "mongodb", "postgresql", "mysql", "oracle",
            "tensorflow", "pytorch", "keras", "scikit-learn", "pandas", "numpy",
            "html", "css", "typescript", "linux", "ubuntu", "windows"
        ]
        
        for skill in tech_skills:
            if skill in text_lower and skill not in found_skills:
                found_skills.append(skill)
        
        return found_skills[:10]  # Limit to top 10 skills
    
    def parse_work_experience(self, resume_text: str) -> List[Dict]:
        """Parse work experience using dataset-enhanced patterns"""
        experiences = []
        
        # Split by work experience section
        lines = resume_text.split('\n')
        in_work_section = False
        current_exp = {}
        
        for line in lines:
            line = line.strip()
            
            if "WORK EXPERIENCE" in line.upper() or "EXPERIENCE" in line.upper():
                in_work_section = True
                continue
            elif "CERTIFICATIONS" in line.upper() or "EDUCATION" in line.upper() or "SKILLS" in line.upper():
                if current_exp:
                    experiences.append(current_exp)
                in_work_section = False
                continue
            
            if in_work_section and line:
                # Look for job titles
                if any(keyword in line.lower() for keyword in ["engineer", "scientist", "analyst", "manager", "developer", "architect"]):
                    if current_exp:
                        experiences.append(current_exp)
                    current_exp = {
                        "job_title": self.normalize_job_title(line),
                        "company": "",
                        "skills_used": [],
                        "responsibilities": []
                    }
                # Look for company names
                elif current_exp and not current_exp.get("company"):
                    current_exp["company"] = self.normalize_company_name(line)
                # Look for responsibilities
                elif current_exp and current_exp.get("company") and (line.startswith('•') or line.startswith('-')):
                    responsibility = line.lstrip('•-*').strip()
                    current_exp["responsibilities"].append(responsibility)
                    # Extract skills from responsibility
                    skills = self.extract_skills_from_text(responsibility)
                    current_exp["skills_used"].extend(skills)
        
        if current_exp:
            experiences.append(current_exp)
        
        # Remove duplicates from skills
        for exp in experiences:
            exp["skills_used"] = list(set(exp["skills_used"]))
        
        return experiences
    
    def parse_certifications(self, resume_text: str) -> List[Dict]:
        """Parse certifications using dataset-enhanced patterns"""
        certifications = []
        
        lines = resume_text.split('\n')
        in_cert_section = False
        current_cert = {}
        
        for line in lines:
            line = line.strip()
            
            if "CERTIFICATIONS" in line.upper():
                in_cert_section = True
                continue
            elif "EDUCATION" in line.upper() or "SKILLS" in line.upper() or "WORK EXPERIENCE" in line.upper():
                if current_cert:
                    certifications.append(current_cert)
                in_cert_section = False
                continue
            
            if in_cert_section and line:
                # Look for certification names
                if any(keyword in line.lower() for keyword in ["certified", "professional", "certificate", "architect", "engineer", "solutions"]):
                    if current_cert:
                        certifications.append(current_cert)
                    cert_name = self.normalize_certification_name(line)
                    current_cert = {
                        "name": cert_name,
                        "issuer": self.extract_certification_issuer(line),
                        "issue_date": None,
                        "expiration_date": None,
                        "credential_id": None
                    }
                # Look for issuer information
                elif current_cert and not current_cert.get("issuer") or current_cert["issuer"] == "Unknown":
                    issuer = self.extract_certification_issuer(line)
                    if issuer != "Unknown":
                        current_cert["issuer"] = issuer
                # Look for dates
                elif current_cert and any(keyword in line.lower() for keyword in ["issued", "expires", "valid", "id:"]):
                    if "issued:" in line.lower():
                        date_match = re.search(r'(\w{3,9}\s+\d{4})', line)
                        if date_match:
                            current_cert["issue_date"] = date_match.group(1)
                    elif "expires:" in line.lower():
                        date_match = re.search(r'(\w{3,9}\s+\d{4})', line)
                        if date_match:
                            current_cert["expiration_date"] = date_match.group(1)
                    elif "id:" in line.lower():
                        id_match = re.search(r'ID:\s*(\w+-?\w*)', line, re.IGNORECASE)
                        if id_match:
                            current_cert["credential_id"] = id_match.group(1)
        
        if current_cert:
            certifications.append(current_cert)
        
        return certifications
    
    def parse_resume(self, resume_text: str) -> Dict:
        """Parse complete resume using dataset-enhanced patterns"""
        
        result = {
            "work_experience": self.parse_work_experience(resume_text),
            "certifications": self.parse_certifications(resume_text),
            "skills": self.extract_skills_from_text(resume_text),
            "parsing_method": "dataset_enhanced"
        }
        
        return result


def test_enhanced_parser():
    """Test the dataset-enhanced parser"""
    
    print("🚀 Testing Dataset-Enhanced Resume Parser")
    print("=" * 60)
    
    parser = DatasetIntegratedParser()
    
    # Test resume
    test_resume = """
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
    
    Software Engineer
    Microsoft
    Redmond, WA
    Jun 2018 - Dec 2019
    
    • Built RESTful APIs using Python and Django
    • Optimized database queries improving performance by 40%
    
    CERTIFICATIONS
    AWS Certified Solutions Architect
    Amazon Web Services
    Issued: June 2023 Expires: June 2026
    ID: AWS-123456
    
    Google Cloud Professional Architect
    Google Cloud
    Issued: March 2022 Expires: March 2025
    ID: GCP-789012
    """
    
    print("📄 Test Resume Input:")
    print("-" * 40)
    print(test_resume[:300] + "...")
    print()
    
    # Parse with enhanced parser
    result = parser.parse_resume(test_resume)
    
    print("📊 Enhanced Parser Results:")
    print("-" * 40)
    
    print("✅ Work Experience:")
    for i, exp in enumerate(result["work_experience"], 1):
        print(f"   {i}. {exp['job_title']} at {exp['company']}")
        print(f"      Skills: {', '.join(exp['skills_used'])}")
        print(f"      Responsibilities: {len(exp['responsibilities'])} items")
    
    print(f"\n✅ Certifications:")
    for i, cert in enumerate(result["certifications"], 1):
        print(f"   {i}. {cert['name']}")
        print(f"      Issuer: {cert['issuer']}")
        print(f"      Valid: {cert['issue_date']} to {cert['expiration_date']}")
        print(f"      ID: {cert['credential_id']}")
    
    print(f"\n✅ Overall Skills: {', '.join(result['skills'])}")
    
    print(f"\n📈 Accuracy Metrics:")
    print(f"   Work Experience Found: {len(result['work_experience'])}")
    print(f"   Certifications Found: {len(result['certifications'])}")
    print(f"   Skills Identified: {len(result['skills'])}")
    
    return result


if __name__ == "__main__":
    test_enhanced_parser()
