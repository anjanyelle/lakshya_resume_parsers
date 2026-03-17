#!/usr/bin/env python3
"""
Add Pavan Kumar's resume data to all training datasets
"""

import json
import os
from datetime import datetime

def add_pavan_to_datasets():
    """Add Pavan's resume data to all dataset files"""
    
    # Pavan's complete resume data
    pavan_data = {
        "id": "pavan_kumar_2024",
        "name": "Pavan Kumar",
        "resume_text": """Pavan Kumar
https://www.linkedin.com/in/pavan-kumar-10rad/ | +1(859) 567-9177 | pavan03248@gmail.com

## PROFESSIONAL EXPERIENCE
Bank of America North Carolina
Sr. Full Stack Developer July 2021 - Present
• Developed and maintained full-stack applications using Java, Spring Boot, Angular, and React
• Led a team of 5 developers in implementing microservices architecture
• Improved application performance by 40% through optimization techniques

Starbucks California
Full Stack Developer Jan 2019 - July 2021
• Built RESTful APIs using Java Spring Boot and Node.js
• Implemented responsive web applications using React and Angular
• Collaborated with cross-functional teams to deliver projects on time

Credit Karma San Francisco
Software Engineer June 2018 - Jan 2019
• Developed consumer-facing features using Java and React
• Worked on credit scoring algorithms and data processing
• Participated in agile development methodology

Amazon Hyderabad, India
SDE-II (Java Full Stack Developer) 2016 - 2018
• Built scalable web applications for Amazon's retail platform
• Implemented microservices using Java Spring Boot
• Worked with AWS services for cloud deployment

ADP Hyderabad, India
Java Developer 2014 - 2016
• Developed enterprise applications using Java and Spring frameworks
• Maintained and enhanced existing software systems
• Provided technical support and troubleshooting

## TECHNICAL SKILLS
Java, Spring Boot, Angular, React, Docker, Kubernetes, AWS, Microservices, REST APIs, Node.js, Python, SQL, NoSQL, Git, Jenkins

## EDUCATION
Bharath University - Bachelor of Technology Computer Science August 2010 to May 2014

## CERTIFICATIONS
AWS Certified Developer - Associate
Oracle Certified Professional, Java SE Programmer
Microsoft Certified: Azure Developer Associate
""",
        "parsed_data": {
            "basics": {
                "name": "Pavan Kumar",
                "email": "pavan03248@gmail.com",
                "phone": "+1(859) 567-9177",
                "linkedin": "https://www.linkedin.com/in/pavan-kumar-10rad/",
                "location": "North Carolina"
            },
            "work": [
                {
                    "company": "Bank of America",
                    "title": "Sr. Full Stack Developer",
                    "location": "North Carolina",
                    "date_range": "July 2021 - Present",
                    "description": "Developed and maintained full-stack applications using Java, Spring Boot, Angular, and React. Led a team of 5 developers in implementing microservices architecture. Improved application performance by 40% through optimization techniques."
                },
                {
                    "company": "Starbucks",
                    "title": "Full Stack Developer",
                    "location": "California",
                    "date_range": "Jan 2019 - July 2021",
                    "description": "Built RESTful APIs using Java Spring Boot and Node.js. Implemented responsive web applications using React and Angular. Collaborated with cross-functional teams to deliver projects on time."
                },
                {
                    "company": "Credit Karma",
                    "title": "Software Engineer",
                    "location": "San Francisco",
                    "date_range": "June 2018 - Jan 2019",
                    "description": "Developed consumer-facing features using Java and React. Worked on credit scoring algorithms and data processing. Participated in agile development methodology."
                },
                {
                    "company": "Amazon",
                    "title": "SDE-II (Java Full Stack Developer)",
                    "location": "Hyderabad, India",
                    "date_range": "2016 - 2018",
                    "description": "Built scalable web applications for Amazon's retail platform. Implemented microservices using Java Spring Boot. Worked with AWS services for cloud deployment."
                },
                {
                    "company": "ADP",
                    "title": "Java Developer",
                    "location": "Hyderabad, India",
                    "date_range": "2014 - 2016",
                    "description": "Developed enterprise applications using Java and Spring frameworks. Maintained and enhanced existing software systems. Provided technical support and troubleshooting."
                }
            ],
            "education": [
                {
                    "institution": "Bharath University",
                    "degree": "Bachelor of Technology Computer Science",
                    "location": "",
                    "date_range": "August 2010 to May 2014",
                    "description": ""
                }
            ],
            "skills": [
                {"name": "Java", "level": "Expert", "category": "Programming"},
                {"name": "Spring Boot", "level": "Expert", "category": "Framework"},
                {"name": "Angular", "level": "Advanced", "category": "Framework"},
                {"name": "React", "level": "Advanced", "category": "Framework"},
                {"name": "Docker", "level": "Intermediate", "category": "DevOps"},
                {"name": "Kubernetes", "level": "Intermediate", "category": "DevOps"},
                {"name": "AWS", "level": "Advanced", "category": "Cloud"},
                {"name": "Microservices", "level": "Advanced", "category": "Architecture"},
                {"name": "REST APIs", "level": "Expert", "category": "API"},
                {"name": "Node.js", "level": "Intermediate", "category": "Programming"},
                {"name": "Python", "level": "Intermediate", "category": "Programming"},
                {"name": "SQL", "level": "Advanced", "category": "Database"},
                {"name": "NoSQL", "level": "Intermediate", "category": "Database"},
                {"name": "Git", "level": "Advanced", "category": "Version Control"},
                {"name": "Jenkins", "level": "Intermediate", "category": "DevOps"}
            ],
            "certifications": [
                {"name": "AWS Certified Developer - Associate", "issuer": "Amazon", "date": "", "description": ""},
                {"name": "Oracle Certified Professional, Java SE Programmer", "issuer": "Oracle", "date": "", "description": ""},
                {"name": "Microsoft Certified: Azure Developer Associate", "issuer": "Microsoft", "date": "", "description": ""}
            ]
        }
    }
    
    # Dataset files to update
    dataset_files = [
        "comprehensive_all_resumes_dataset_updated.json",
        "comprehensive_all_resumes_dataset.json",
        "perfect_json_dataset.json",
        "comprehensive_resume_dataset.json"
    ]
    
    for dataset_file in dataset_files:
        if os.path.exists(dataset_file):
            try:
                # Load existing dataset
                with open(dataset_file, 'r', encoding='utf-8') as f:
                    dataset = json.load(f)
                
                # Add Pavan's data
                if isinstance(dataset, list):
                    # Check if Pavan already exists
                    pavan_exists = any(item.get('id') == 'pavan_kumar_2024' for item in dataset)
                    if not pavan_exists:
                        dataset.append(pavan_data)
                        print(f"✅ Added Pavan's data to {dataset_file}")
                    else:
                        print(f"⚠️ Pavan's data already exists in {dataset_file}")
                elif isinstance(dataset, dict) and 'resumes' in dataset:
                    # Check if Pavan already exists
                    pavan_exists = any(item.get('id') == 'pavan_kumar_2024' for item in dataset['resumes'])
                    if not pavan_exists:
                        dataset['resumes'].append(pavan_data)
                        print(f"✅ Added Pavan's data to {dataset_file}")
                    else:
                        print(f"⚠️ Pavan's data already exists in {dataset_file}")
                
                # Save updated dataset
                with open(dataset_file, 'w', encoding='utf-8') as f:
                    json.dump(dataset, f, indent=2, ensure_ascii=False)
                
            except Exception as e:
                print(f"❌ Error updating {dataset_file}: {e}")
        else:
            print(f"⚠️ Dataset file not found: {dataset_file}")

if __name__ == "__main__":
    print("🔧 Adding Pavan Kumar's data to all training datasets...")
    add_pavan_to_datasets()
    print("✅ Dataset update complete!")
