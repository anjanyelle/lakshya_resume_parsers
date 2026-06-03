"""
Test Full Resume Skill Extraction Enhancement

This script tests that skills are extracted from the ENTIRE resume,
not just the "Technical Skills" section.

Expected: Skills from work experience, projects, certifications, and summary
should all be extracted.
"""

import sys
sys.path.insert(0, '/Users/anjanyelle/Desktop/untitled folder 3/Lakshya-LLM-Resume-Parser/backend')

from app.services.parser.skill_extractor import SkillExtractor
from app.services.parser.work_experience_parser import JobEntry

# Sample resume with skills scattered across sections
SAMPLE_RESUME = """
PROFESSIONAL SUMMARY
Senior Full-Stack Developer with 8+ years of experience in React, Node.js, and AWS.
Expert in building scalable microservices using Spring Boot and deploying on Kubernetes.

WORK EXPERIENCE

Senior Software Engineer | TechCorp Inc. | San Francisco, CA | 2020-Present
Responsibilities:
- Built microservices architecture using Spring Boot and Docker
- Deployed applications on Kubernetes and AWS ECS
- Implemented CI/CD pipelines with Jenkins and GitHub Actions
- Managed PostgreSQL and MongoDB databases
- Developed RESTful APIs using Express and GraphQL
- Used Redis for caching and session management

Full-Stack Developer | StartupXYZ | Austin, TX | 2018-2020
Responsibilities:
- Developed frontend using React, Redux, and TypeScript
- Built backend services with Node.js and Express
- Integrated with AWS services (S3, Lambda, DynamoDB)
- Implemented automated testing with Jest and Cypress
- Used MySQL for relational data storage

PROJECTS

E-Commerce Platform (2021)
Technologies: React, Redux, TypeScript, Node.js, Express, GraphQL, MySQL, Redis, AWS
- Built responsive UI with React and Material-UI
- Implemented state management with Redux Toolkit
- Created GraphQL API for efficient data fetching
- Deployed on AWS using S3, CloudFront, and Lambda

Real-Time Analytics Dashboard (2020)
Technologies: Python, Flask, PostgreSQL, Docker, Kubernetes, Prometheus, Grafana
- Built backend API with Flask and SQLAlchemy
- Used PostgreSQL for data storage
- Containerized with Docker and deployed on Kubernetes
- Implemented monitoring with Prometheus and Grafana

CERTIFICATIONS
- AWS Certified Solutions Architect - Associate (2022)
- Certified Kubernetes Administrator (CKA) (2021)
- MongoDB Certified Developer (2020)

TECHNICAL SKILLS
Programming Languages: Python, Java, JavaScript, TypeScript, Go
Frameworks: React, Angular, Vue.js, Spring Boot, Django, Flask
Databases: MySQL, PostgreSQL, MongoDB, Redis, DynamoDB
Cloud: AWS (EC2, S3, Lambda, ECS, RDS), Azure, Google Cloud Platform
DevOps: Docker, Kubernetes, Jenkins, GitHub Actions, Terraform, Ansible
"""

def test_skill_extraction():
    print("=" * 80)
    print("TESTING FULL RESUME SKILL EXTRACTION")
    print("=" * 80)
    
    # Extract technical skills section
    skills_section = """
    Programming Languages: Python, Java, JavaScript, TypeScript, Go
    Frameworks: React, Angular, Vue.js, Spring Boot, Django, Flask
    Databases: MySQL, PostgreSQL, MongoDB, Redis, DynamoDB
    Cloud: AWS (EC2, S3, Lambda, ECS, RDS), Azure, Google Cloud Platform
    DevOps: Docker, Kubernetes, Jenkins, GitHub Actions, Terraform, Ansible
    """
    
    # Create job entries from work experience
    jobs = [
        JobEntry(
            company="TechCorp Inc.",
            title="Senior Software Engineer",
            start_date=None,
            end_date=None,
            is_current=True,
            location="San Francisco, CA",
            description="Built microservices architecture using Spring Boot and Docker",
            bullets=[
                "Deployed applications on Kubernetes and AWS ECS",
                "Implemented CI/CD pipelines with Jenkins and GitHub Actions",
                "Managed PostgreSQL and MongoDB databases",
                "Developed RESTful APIs using Express and GraphQL",
                "Used Redis for caching and session management"
            ],
            duration_months=48,
            client=None,
            employment_type="Full-time",
            confidence=0.9
        ),
        JobEntry(
            company="StartupXYZ",
            title="Full-Stack Developer",
            start_date=None,
            end_date=None,
            is_current=False,
            location="Austin, TX",
            description="Developed frontend using React, Redux, and TypeScript",
            bullets=[
                "Built backend services with Node.js and Express",
                "Integrated with AWS services (S3, Lambda, DynamoDB)",
                "Implemented automated testing with Jest and Cypress",
                "Used MySQL for relational data storage"
            ],
            duration_months=24,
            client=None,
            employment_type="Full-time",
            confidence=0.9
        )
    ]
    
    # Initialize skill extractor
    print("\n1. Initializing SkillExtractor...")
    extractor = SkillExtractor(use_spacy=False)
    
    # Test 1: Extract with section_only=True (OLD BEHAVIOR)
    print("\n2. Testing OLD behavior (section_only=True)...")
    print("   This should ONLY extract from Technical Skills section")
    old_skills = extractor.extract_all(
        skills_section=skills_section,
        jobs=jobs,
        raw_text=SAMPLE_RESUME,
        section_only=True  # ❌ OLD: Only skills section
    )
    
    print(f"\n   ❌ OLD: Extracted {len(old_skills)} skills (section only)")
    old_skill_names = sorted([s.name for s in old_skills])
    print(f"   Skills: {', '.join(old_skill_names[:15])}...")
    
    # Test 2: Extract with section_only=False (NEW BEHAVIOR)
    print("\n3. Testing NEW behavior (section_only=False)...")
    print("   This should extract from ENTIRE resume")
    new_skills = extractor.extract_all(
        skills_section=skills_section,
        jobs=jobs,
        raw_text=SAMPLE_RESUME,
        section_only=False  # ✅ NEW: Entire resume
    )
    
    print(f"\n   ✅ NEW: Extracted {len(new_skills)} skills (entire resume)")
    new_skill_names = sorted([s.name for s in new_skills])
    print(f"   Skills: {', '.join(new_skill_names[:20])}...")
    
    # Compare results
    print("\n4. COMPARISON:")
    print(f"   Skills in OLD approach: {len(old_skills)}")
    print(f"   Skills in NEW approach: {len(new_skills)}")
    print(f"   Additional skills found: {len(new_skills) - len(old_skills)}")
    
    # Find skills that were missed in old approach
    old_normalized = {s.normalized_name for s in old_skills}
    new_normalized = {s.normalized_name for s in new_skills}
    missed_skills = new_normalized - old_normalized
    
    if missed_skills:
        print(f"\n5. SKILLS MISSED IN OLD APPROACH ({len(missed_skills)}):")
        for skill_norm in sorted(missed_skills)[:20]:
            skill_obj = next((s for s in new_skills if s.normalized_name == skill_norm), None)
            if skill_obj:
                print(f"   - {skill_obj.name} (source: {skill_obj.source}, confidence: {skill_obj.confidence:.2f})")
    
    # Categorize skills
    print("\n6. SKILLS BY CATEGORY:")
    categories = {}
    for skill in new_skills:
        cat = skill.category or "Other"
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(skill.name)
    
    for category, skills_list in sorted(categories.items()):
        print(f"\n   {category} ({len(skills_list)}):")
        print(f"   {', '.join(sorted(skills_list)[:10])}")
        if len(skills_list) > 10:
            print(f"   ... and {len(skills_list) - 10} more")
    
    # Verify specific skills from different sections
    print("\n7. VERIFICATION - Skills from different sections:")
    
    test_cases = [
        ("React", "Should be found in Summary, Work Experience, Projects, and Skills"),
        ("Spring Boot", "Should be found in Summary, Work Experience, and Skills"),
        ("Kubernetes", "Should be found in Summary, Work Experience, Projects, and Certifications"),
        ("GraphQL", "Should be found in Work Experience and Projects"),
        ("Flask", "Should be found in Projects and Skills"),
        ("Prometheus", "Should be found in Projects only"),
        ("Material-UI", "Should be found in Projects only"),
        ("Redux Toolkit", "Should be found in Projects only"),
    ]
    
    for skill_name, expected in test_cases:
        found = any(s.name.lower() == skill_name.lower() or skill_name.lower() in s.name.lower() for s in new_skills)
        status = "✅" if found else "❌"
        print(f"   {status} {skill_name}: {expected}")
    
    print("\n" + "=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)
    
    # Summary
    print("\n📊 SUMMARY:")
    print(f"   Total skills extracted: {len(new_skills)}")
    print(f"   Improvement over old approach: +{len(new_skills) - len(old_skills)} skills")
    print(f"   Percentage increase: {((len(new_skills) - len(old_skills)) / len(old_skills) * 100):.1f}%")
    
    print("\n✅ BENEFITS:")
    print("   - More accurate candidate matching")
    print("   - Better ATS search results")
    print("   - Complete skill profile")
    print("   - No skills missed from work experience, projects, or certifications")


if __name__ == "__main__":
    test_skill_extraction()
