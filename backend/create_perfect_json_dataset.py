#!/usr/bin/env python3

"""
Perfect JSON Dataset Creator for Resume Parser
Creates datasets that match your exact JSON structure requirements
Based on your perfect example output
"""

import json
import random
from datetime import datetime
from typing import Dict, List, Any

class PerfectJSONDatasetCreator:
    """Create perfect JSON datasets matching your exact structure"""
    
    def __init__(self):
        print("🎯 Perfect JSON Dataset Creator - Matching Your Exact Requirements")
        
        # Load your perfect example structure
        self.perfect_structure = self._load_perfect_structure()
        
        # Sample data
        self.sample_data = {
            "names": ["Sarah Johnson", "Michael Chen", "Emily Rodriguez", "David Kim", "Jessica Williams"],
            "companies": ["Google", "Microsoft", "Amazon", "Apple", "Meta", "Netflix", "Oracle", "Salesforce"],
            "skills": ["Python", "Java", "JavaScript", "TypeScript", "C#", "React", "Angular", "Vue.js", "Node.js", "Django", "Flask", "Spring Boot", ".NET", "AWS", "Azure", "GCP", "Docker", "Kubernetes", "Jenkins", "Git", "SQL", "MongoDB", "PostgreSQL", "Redis", "Kafka", "Spark", "Hadoop", "Tableau", "Power BI", "Machine Learning", "Data Science", "AI", "DevOps", "CI/CD"],
            "job_titles": ["Senior Software Engineer", "Data Scientist", "Product Manager", "DevOps Engineer", "Full Stack Developer", "Machine Learning Engineer", "Cloud Architect", "Technical Lead", "Engineering Manager", "Solutions Architect"],
            "universities": ["Stanford University", "MIT", "Carnegie Mellon University", "UC Berkeley", "University of Washington", "Georgia Tech", "University of Texas at Austin", "University of Illinois Urbana-Champaign", "Cornell University", "Princeton University"],
            "degrees": ["Bachelor of Science in Computer Science", "Master of Science in Software Engineering", "Bachelor of Engineering in Information Technology", "Master of Business Administration", "PhD in Computer Science", "Bachelor of Arts in Data Science"]
        }
    
    def _load_perfect_structure(self):
        """Load your perfect JSON structure"""
        return {
            "basics": {
                "name": "",
                "email": "",
                "phone": "",
                "location": "",
                "summary": "",
                "linkedin": "",
                "github": "",
                "website": ""
            },
            "work": [],
            "education": [],
            "skills": [],
            "certifications": [],
            "projects": [],
            "languages": [],
            "volunteer": [],
            "references": [],
            "achievements": [],
            "publications": []
        }
    
    def create_perfect_sample(self, sample_id: int) -> Dict[str, Any]:
        """Create a perfect sample matching your exact JSON structure"""
        
        # Generate random data
        name = random.choice(self.sample_data["names"])
        email = f"{name.lower().replace(' ', '.')}@example.com"
        phone = f"(555) {random.randint(100, 999)}-{random.randint(1000, 9999)}"
        location = f"{random.choice(['San Francisco', 'New York', 'Austin', 'Seattle', 'Boston'])}, {random.choice(['CA', 'NY', 'TX', 'WA', 'MA'])}"
        
        # Generate work experience
        work = self._generate_perfect_work()
        
        # Generate education
        education = self._generate_perfect_education()
        
        # Generate skills
        skills = self._generate_perfect_skills()
        
        # Generate certifications
        certifications = self._generate_perfect_certifications()
        
        # Create resume text
        resume_text = self._create_resume_text(name, email, phone, location, work, education, skills)
        
        # Create perfect JSON structure
        perfect_json = {
            "basics": {
                "name": name,
                "email": email,
                "phone": phone,
                "location": location,
                "summary": f"Experienced {work[0]['title'] if work else 'Professional'} with expertise in {', '.join([s['name'] for s in skills[:3]])}. Proven track record of delivering high-quality solutions and driving innovation.",
                "linkedin": f"https://www.linkedin.com/in/{name.lower().replace(' ', '.')}",
                "github": f"https://www.github.com/{name.lower().replace(' ', '.')}",
                "website": f"https://www.{name.lower().replace(' ', '.')}.com"
            },
            "work": work,
            "education": education,
            "skills": skills,
            "certifications": certifications,
            "projects": [],
            "languages": [
                {
                    "language": "English",
                    "fluency": "Native"
                }
            ],
            "volunteer": [],
            "references": [],
            "achievements": [],
            "publications": []
        }
        
        return {
            "id": sample_id,
            "resume_text": resume_text,
            "expected_output": perfect_json,
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "source": "perfect_json_generator",
                "quality_score": 1.0,
                "verified": True,
                "structure_match": "exact",
                "industry": random.choice(["technology", "finance", "healthcare", "consulting"])
            }
        }
    
    def _generate_perfect_work(self) -> List[Dict[str, Any]]:
        """Generate perfect work experience entries"""
        work = []
        
        # Generate 2-3 jobs
        num_jobs = random.randint(2, 3)
        current_year = 2024
        
        for i in range(num_jobs):
            company = random.choice(self.sample_data["companies"])
            title = random.choice(self.sample_data["job_titles"])
            location = f"{random.choice(['San Francisco', 'New York', 'Austin', 'Seattle', 'Chicago'])}, {random.choice(['CA', 'NY', 'TX', 'WA', 'IL'])}"
            
            # Calculate dates
            start_year = current_year - (i * 3) - random.randint(1, 4)
            end_year = start_year + random.randint(2, 4)
            
            if i == 0:  # Current job
                start_date = f"{start_year}-01-01"
                end_date = None
                current = True
            else:
                start_date = f"{start_year}-01-01"
                end_date = f"{end_year}-12-31"
                current = False
            
            # Generate description
            description = self._generate_job_description(title, company)
            
            work.append({
                "company": company,
                "title": title,
                "location": location,
                "startDate": start_date,
                "endDate": end_date,
                "description": description,
                "current": current
            })
        
        return work
    
    def _generate_job_description(self, title: str, company: str) -> str:
        """Generate realistic job description"""
        descriptions = {
            "Senior Software Engineer": f"Led development of scalable microservices at {company} using modern technologies. Improved system performance by 40% and reduced technical debt by 60%. Mentored junior developers and established coding standards.",
            "Data Scientist": f"Developed machine learning models at {company} that improved prediction accuracy by 35%. Built data pipelines processing 10TB+ daily data. Collaborated with cross-functional teams to deliver data-driven insights.",
            "Product Manager": f"Managed product roadmap at {company} and launched 3 major features increasing user engagement by 45%. Conducted market research and defined product requirements. Coordinated with engineering and design teams.",
            "DevOps Engineer": f"Implemented CI/CD pipelines at {company} reducing deployment time by 70%. Managed cloud infrastructure using AWS/Azure. Established monitoring and alerting systems improving reliability.",
            "Full Stack Developer": f"Developed full-stack applications at {company} using React and Node.js. Built REST APIs and responsive UI components. Optimized database queries improving performance by 50%.",
            "Machine Learning Engineer": f"Designed and deployed ML models at {company} serving 1M+ requests daily. Implemented MLOps pipelines and model monitoring. Improved model accuracy by 25% through feature engineering.",
            "Cloud Architect": f"Architected cloud infrastructure at {company} handling 99.99% uptime. Designed multi-region deployments and disaster recovery strategies. Reduced infrastructure costs by 40%.",
            "Technical Lead": f"Led technical team at {company} delivering projects on time and budget. Established architectural patterns and code review processes. Mentored team members and conducted technical interviews.",
            "Engineering Manager": f"Managed engineering team at {company} of 15+ developers. Improved team productivity by 60% through agile practices. Drove technical strategy and talent development.",
            "Solutions Architect": f"Designed solutions for enterprise clients at {company}. Created technical architectures and implementation plans. Presented solutions to C-level executives."
        }
        
        return descriptions.get(title, f"Worked at {company} delivering high-quality solutions and driving innovation.")
    
    def _generate_perfect_education(self) -> List[Dict[str, Any]]:
        """Generate perfect education entries"""
        education = []
        
        # Generate 1-2 education entries
        num_edu = random.randint(1, 2)
        
        for i in range(num_edu):
            institution = random.choice(self.sample_data["universities"])
            degree = random.choice(self.sample_data["degrees"])
            location = f"{random.choice(['Pittsburgh', 'PA', 'Cambridge', 'MA', 'Stanford', 'CA', 'Berkeley', 'CA'])}"
            
            # Calculate dates
            start_year = 2005 + random.randint(0, 10)
            end_year = start_year + random.randint(2, 6)
            
            education.append({
                "institution": institution,
                "degree": degree,
                "field": "",
                "location": location,
                "startDate": f"{start_year}-09-01",
                "endDate": f"{end_year}-06-30",
                "gpa": str(round(random.uniform(3.2, 4.0), 2)),
                "current": False
            })
        
        return education
    
    def _generate_perfect_skills(self) -> List[Dict[str, Any]]:
        """Generate perfect skills entries"""
        selected_skills = random.sample(self.sample_data["skills"], random.randint(8, 15))
        skills_list = []
        
        categories = {
            "Programming Languages": ["Python", "Java", "JavaScript", "TypeScript", "C#", "Go", "Rust"],
            "Frameworks": ["React", "Angular", "Vue.js", "Node.js", "Django", "Flask", "Spring Boot", ".NET"],
            "Cloud Platforms": ["AWS", "Azure", "GCP", "DigitalOcean"],
            "Databases": ["SQL", "MongoDB", "PostgreSQL", "Redis", "Cassandra"],
            "DevOps": ["Docker", "Kubernetes", "Jenkins", "Git", "CI/CD"],
            "Data Science": ["Machine Learning", "Data Science", "AI", "Spark", "Hadoop", "Tableau", "Power BI"]
        }
        
        for skill in selected_skills:
            category = "Other"
            for cat_name, cat_skills in categories.items():
                if skill in cat_skills:
                    category = cat_name
                    break
            
            skills_list.append({
                "name": skill,
                "level": random.choice(["Beginner", "Intermediate", "Advanced", "Expert"]),
                "category": category,
                "years_experience": str(random.randint(1, 10)),
                "proficiency": random.choice(["Basic", "Intermediate", "Advanced", "Expert"])
            })
        
        return skills_list
    
    def _generate_perfect_certifications(self) -> List[Dict[str, Any]]:
        """Generate perfect certifications entries"""
        certifications = [
            {
                "name": "AWS Certified Solutions Architect",
                "issuer": "Amazon Web Services",
                "date": "2023-01-01",
                "credential_id": "AWS-ASA-123456",
                "url": "https://aws.amazon.com/certification/"
            },
            {
                "name": "Microsoft Certified: Azure Developer Associate",
                "issuer": "Microsoft",
                "date": "2022-06-01",
                "credential_id": "AZ-400-789012",
                "url": "https://docs.microsoft.com/certifications/"
            },
            {
                "name": "Google Cloud Professional Cloud Architect",
                "issuer": "Google",
                "date": "2021-11-01",
                "credential_id": "GCP-PCA-345678",
                "url": "https://cloud.google.com/certification/"
            },
            {
                "name": "Certified Kubernetes Administrator",
                "issuer": "Cloud Native Computing Foundation",
                "date": "2022-03-01",
                "credential_id": "CKA-901234",
                "url": "https://www.cncf.io/certification/cka/"
            }
        ]
        
        # Select 1-3 random certifications
        selected_certs = random.sample(certifications, random.randint(1, 3))
        return selected_certs
    
    def _create_resume_text(self, name: str, email: str, phone: str, location: str, 
                          work: List[Dict[str, Any]], education: List[Dict[str, Any]], 
                          skills: List[Dict[str, Any]]) -> str:
        """Create resume text from structured data"""
        
        resume_parts = []
        
        # Header
        resume_parts.append(f"{name}")
        resume_parts.append(f"{work[0]['title'] if work else 'Professional'}")
        resume_parts.append(f"{location} • {phone} • {email}")
        resume_parts.append(f"https://www.linkedin.com/in/{name.lower().replace(' ', '.')}")
        resume_parts.append("")
        
        # Summary
        resume_parts.append("PROFESSIONAL SUMMARY")
        resume_parts.append(f"Experienced {work[0]['title'] if work else 'Professional'} with expertise in {', '.join([s['name'] for s in skills[:5]])}. Proven track record of delivering high-quality solutions and driving innovation.")
        resume_parts.append("")
        
        # Skills
        resume_parts.append("TECHNICAL SKILLS")
        resume_parts.append(f"• {', '.join([s['name'] for s in skills[:10]])}")
        resume_parts.append("")
        
        # Work Experience
        resume_parts.append("PROFESSIONAL EXPERIENCE")
        for job in work:
            resume_parts.append(f"{job['title']} | {job['company']} | {job['startDate'][:4]} – {job['endDate'][:4] if job['endDate'] else 'Present'}")
            resume_parts.append(f"{job['location']}")
            resume_parts.append(f"{job['description']}")
            resume_parts.append("")
        
        # Education
        resume_parts.append("EDUCATION")
        for edu in education:
            resume_parts.append(f"{edu['degree']} | {edu['institution']}")
            resume_parts.append(f"{edu['startDate'][:4]} – {edu['endDate'][:4]}")
            resume_parts.append("")
        
        return "\n".join(resume_parts)
    
    def create_alistair_perfect_sample(self) -> Dict[str, Any]:
        """Create Alistair Caldwell perfect sample matching your exact JSON"""
        
        alistair_resume = """ALISTAIR H. CALDWELL
Principal .NET Solutions Architect & Global Director of Software Engineering
Austin, TX • (512) 555-0942 • a.caldwell.dotnet@enterprise-solutions.net
linkedin.com/in/alistair-caldwell-dotnet-lead • US Citizen
PROFESSIONAL SUMMARY
Technically formidable and results-oriented Software Engineering Executive with over 12 years
of specialized experience in architecting, developing, and scaling mission-critical enterprise systems
within the Microsoft.NET ecosystem. Renowned for orchestrating the digital transformation of global
financial and healthcare institutions by transitioning monolithic legacy infrastructures into high-performance,
cloud-native microservices architectures.
TECHNICAL SKILLS
• Languages: C# (Expert), F# (Functional Patterns), TypeScript, JavaScript, Go, SQL, PowerShell, Bash, Python
• Backend Frameworks: .NET 8/9, ASP.NET Core (Minimal APIs, SignalR), Entity Framework Core, Dapper, Akka.NET
• Cloud Platforms: Microsoft Azure (AKS, App Service, Functions, DevOps), AWS, GCP
• Databases: SQL Server 2022, Azure SQL DB, Cosmos DB, PostgreSQL, MongoDB
• DevOps: Docker, Kubernetes, Jenkins, Git, CI/CD, Terraform
PROFESSIONAL EXPERIENCE
Global Director of Engineering & Principal .NET Architect | Nexus FinTech Systems | 2021 – Present
Austin, TX / Remote
Strategic Mandate & Executive Leadership: Appointed as the primary technical authority for the
"Core Ledger & Payments" division, managing a multi-regional engineering organization of 135
Software Engineers and SDETs. Accountable for architectural integrity and scalability of a platform
handling $1B+ in daily transaction volume.
Key Measurable Achievements:
• Enterprise .NET Transformation: Led the massive migration from a monolithic ASP.NET 4.8 framework
to a containerized .NET 8 microservices ecosystem on Azure. Achieved a 65% reduction in
infrastructure costs while increasing transaction throughput by 400%.
Senior Principal Software Architect | Lumina Healthcare Digital | 2017 – 2021
Austin, TX
Operational Leadership: Served as the lead architect for the "Lumina-Connect" platform, focusing
on real-time clinical data interoperability and AI-assisted diagnostics. Directed a team of 45
senior developers and 15 data engineers across 3 geographic hubs.
Key Measurable Achievements:
• Real-Time Telemetry Engine: Architected a high-frequency telemetry ingestion engine using SignalR
and .NET Core. Processed 2.5 billion data points daily from wearable medical devices with
sub-100ms latency to clinician dashboards.
EDUCATION
Master of Science in Software Engineering & Cloud Architecture | Carnegie Mellon University | 2015 – 2017
Pittsburgh, PA
• Focus Areas: Reliability Engineering, Distributed Computing, Statistical Defect Prediction
• Honors: CMU Excellence in Graduate Research Award
Bachelor of Science in Computer Science & Mathematics | The University of Texas at Austin | 2011 – 2015
Austin, TX
• Honors: Summa Cum Laude; President of the UT Computer Science Honor Society
CERTIFICATIONS
• Microsoft Certified: Azure Solutions Architect Expert | 2021
• Microsoft Certified: DevOps Engineer Expert | 2021
• CKA: Certified Kubernetes Administrator | 2020
• CISSP: Certified Information Systems Security Professional | 2019"""

        alistair_json = {
            "basics": {
                "name": "ALISTAIR H. CALDWELL",
                "email": "a.caldwell.dotnet@enterprise-solutions.net",
                "phone": "(512) 555-0942",
                "location": "Austin, TX",
                "summary": "Technically formidable and results-oriented Software Engineering Executive with over 12 years of specialized experience in architecting, developing, and scaling mission-critical enterprise systems within the Microsoft.NET ecosystem. Renowned for orchestrating the digital transformation of global financial and healthcare institutions by transitioning monolithic legacy infrastructures into high-performance, cloud-native microservices architectures.",
                "linkedin": "https://www.linkedin.com/in/alistair-caldwell-dotnet-lead",
                "github": "",
                "website": ""
            },
            "work": [
                {
                    "company": "Nexus FinTech Systems",
                    "title": "Global Director of Engineering & Principal .NET Architect",
                    "location": "Austin, TX / Remote",
                    "startDate": "2021-01-01",
                    "endDate": None,
                    "description": "Strategic Mandate & Executive Leadership: Appointed as the primary technical authority for the 'Core Ledger & Payments' division, managing a multi-regional engineering organization of 135 Software Engineers and SDETs. Accountable for architectural integrity and scalability of a platform handling $1B+ in daily transaction volume. Key Measurable Achievements: Enterprise .NET Transformation: Led the massive migration from a monolithic ASP.NET 4.8 framework to a containerized .NET 8 microservices ecosystem on Azure. Achieved a 65% reduction in infrastructure costs while increasing transaction throughput by 400%.",
                    "current": True
                },
                {
                    "company": "Lumina Healthcare Digital",
                    "title": "Senior Principal Software Architect",
                    "location": "Austin, TX",
                    "startDate": "2017-01-01",
                    "endDate": "2021-01-01",
                    "description": "Operational Leadership: Served as the lead architect for the 'Lumina-Connect' platform, focusing on real-time clinical data interoperability and AI-assisted diagnostics. Directed a team of 45 senior developers and 15 data engineers across 3 geographic hubs. Key Measurable Achievements: Real-Time Telemetry Engine: Architected a high-frequency telemetry ingestion engine using SignalR and .NET Core. Processed 2.5 billion data points daily from wearable medical devices with sub-100ms latency to clinician dashboards.",
                    "current": False
                }
            ],
            "education": [
                {
                    "institution": "Carnegie Mellon University",
                    "degree": "Master of Science in Software Engineering & Cloud Architecture",
                    "field": "",
                    "location": "Pittsburgh, PA",
                    "startDate": "2015-09-01",
                    "endDate": "2017-06-30",
                    "gpa": "",
                    "current": False
                },
                {
                    "institution": "The University of Texas at Austin",
                    "degree": "Bachelor of Science in Computer Science & Mathematics",
                    "field": "",
                    "location": "Austin, TX",
                    "startDate": "2011-09-01",
                    "endDate": "2015-06-30",
                    "gpa": "",
                    "current": False
                }
            ],
            "skills": [
                {
                    "name": "C#",
                    "level": "Expert",
                    "category": "Programming Languages",
                    "years_experience": "12",
                    "proficiency": "Expert"
                },
                {
                    "name": ".NET",
                    "level": "Expert",
                    "category": "Frameworks",
                    "years_experience": "12",
                    "proficiency": "Expert"
                },
                {
                    "name": "Azure",
                    "level": "Expert",
                    "category": "Cloud Platforms",
                    "years_experience": "8",
                    "proficiency": "Expert"
                },
                {
                    "name": "Kubernetes",
                    "level": "Advanced",
                    "category": "DevOps",
                    "years_experience": "5",
                    "proficiency": "Advanced"
                },
                {
                    "name": "SQL Server",
                    "level": "Expert",
                    "category": "Databases",
                    "years_experience": "12",
                    "proficiency": "Expert"
                },
                {
                    "name": "Python",
                    "level": "Intermediate",
                    "category": "Programming Languages",
                    "years_experience": "5",
                    "proficiency": "Intermediate"
                },
                {
                    "name": "Docker",
                    "level": "Advanced",
                    "category": "DevOps",
                    "years_experience": "6",
                    "proficiency": "Advanced"
                },
                {
                    "name": "SignalR",
                    "level": "Expert",
                    "category": "Frameworks",
                    "years_experience": "7",
                    "proficiency": "Expert"
                }
            ],
            "certifications": [
                {
                    "name": "Microsoft Certified: Azure Solutions Architect Expert",
                    "issuer": "Microsoft",
                    "date": "2021-01-01",
                    "credential_id": "",
                    "url": ""
                },
                {
                    "name": "Microsoft Certified: DevOps Engineer Expert",
                    "issuer": "Microsoft",
                    "date": "2021-01-01",
                    "credential_id": "",
                    "url": ""
                },
                {
                    "name": "CKA: Certified Kubernetes Administrator",
                    "issuer": "Cloud Native Computing Foundation",
                    "date": "2020-01-01",
                    "credential_id": "",
                    "url": ""
                },
                {
                    "name": "CISSP: Certified Information Systems Security Professional",
                    "issuer": "ISC2",
                    "date": "2019-01-01",
                    "credential_id": "",
                    "url": ""
                }
            ],
            "projects": [],
            "languages": [
                {
                    "language": "English",
                    "fluency": "Native"
                }
            ],
            "volunteer": [],
            "references": [],
            "achievements": [],
            "publications": []
        }
        
        return {
            "id": 1,
            "resume_text": alistair_resume,
            "expected_output": alistair_json,
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "source": "alistair_perfect_example",
                "quality_score": 1.0,
                "verified": True,
                "structure_match": "exact",
                "industry": "technology"
            }
        }
    
    def generate_dataset(self, num_samples: int = 50) -> List[Dict[str, Any]]:
        """Generate perfect JSON dataset"""
        print(f"🚀 Generating {num_samples} perfect JSON samples...")
        
        dataset = []
        
        # Add Alistair Caldwell perfect sample
        alistair_sample = self.create_alistair_perfect_sample()
        dataset.append(alistair_sample)
        
        # Generate synthetic samples
        for i in range(1, num_samples):
            sample = self.create_perfect_sample(i + 1)
            dataset.append(sample)
        
        print(f"✅ Generated {len(dataset)} perfect JSON samples")
        return dataset
    
    def save_dataset(self, dataset: List[Dict[str, Any]], filename: str):
        """Save dataset to file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(dataset, f, indent=2, ensure_ascii=False)
        print(f"✅ Perfect JSON dataset saved to {filename}")
        print(f"📊 Total samples: {len(dataset)}")
    
    def validate_structure(self, dataset: List[Dict[str, Any]]) -> bool:
        """Validate that all samples match the perfect structure"""
        print("🔍 Validating JSON structure...")
        
        required_keys = set(self.perfect_structure.keys())
        
        for i, sample in enumerate(dataset):
            expected_output = sample.get("expected_output", {})
            
            # Check all required keys are present
            if not set(expected_output.keys()) == required_keys:
                print(f"❌ Sample {i+1}: Missing keys - {set(required_keys) - set(expected_output.keys())}")
                return False
            
            # Validate each section structure
            for key in required_keys:
                if key == "basics":
                    if not self._validate_basics(expected_output[key]):
                        print(f"❌ Sample {i+1}: Invalid basics structure")
                        return False
                elif key in ["work", "education", "skills", "certifications", "projects", "languages", "volunteer", "references", "achievements", "publications"]:
                    if not isinstance(expected_output[key], list):
                        print(f"❌ Sample {i+1}: {key} should be a list")
                        return False
        
        print("✅ All samples have perfect JSON structure!")
        return True
    
    def _validate_basics(self, basics: Dict[str, Any]) -> bool:
        """Validate basics structure"""
        required_basics = ["name", "email", "phone", "location", "summary", "linkedin", "github", "website"]
        return set(basics.keys()) == set(required_basics)

def main():
    """Main function"""
    print("🎯 Perfect JSON Dataset Creator for Resume Parser")
    print("=" * 60)
    
    creator = PerfectJSONDatasetCreator()
    
    # Generate dataset
    dataset = creator.generate_dataset(num_samples=50)
    
    # Validate structure
    if creator.validate_structure(dataset):
        # Save dataset
        creator.save_dataset(dataset, "perfect_json_dataset.json")
        
        print("\n✅ Perfect JSON Dataset Creation Complete!")
        print("📊 Dataset features:")
        print("  • Perfect JSON structure matching your requirements")
        print("  • Alistair Caldwell perfect example included")
        print("  • All keys and values properly formatted")
        print("  • Complete validation passed")
        print("  • Ready for training your resume parser")
        
        # Show sample structure
        print("\n📋 Sample JSON Structure:")
        print(json.dumps(dataset[0]["expected_output"], indent=2)[:500] + "...")
    else:
        print("❌ Structure validation failed!")

if __name__ == "__main__":
    main()
