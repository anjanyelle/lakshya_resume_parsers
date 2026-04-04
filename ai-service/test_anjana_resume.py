#!/usr/bin/env python3
"""
Test Anjana's resume parsing to verify DeBERTa section-based extraction.
"""

import sys
import os
from pathlib import Path

# Add the ai-service directory to path
sys.path.append(str(Path(__file__).parent))

from parsers.master_parser import MasterParser

def test_anjana_resume():
    """Test Anjana's resume with the new section-based DeBERTa approach."""
    
    resume_text = """
ANJANA REDDY
Email: anjana.reddy.dev@gmail.com
Phone: +91 98765 43210
Location: Bangalore, India
LinkedIn: linkedin.com/in/anjanareddy
GitHub: github.com/anjanareddy

PROFESSIONAL SUMMARY
Full Stack Developer with 3 years of experience in building scalable web applications using React.js, Node.js, and modern cloud technologies. Experienced in delivering solutions for fintech, e-commerce, and healthcare clients. Strong expertise in REST APIs, microservices, and responsive UI development.

TECHNICAL SKILLS
Frontend: React.js, Next.js, JavaScript, HTML5, CSS3, Tailwind CSS
Backend: Node.js, Express.js
Database: MongoDB, MySQL
Cloud: AWS (EC2, S3, Lambda)
Tools: Git, GitHub, Postman, Docker
Other: REST APIs, JWT, Agile

WORK EXPERIENCE
Full Stack Developer
Infosys, Bangalore
June 2023 – Present
Client: Goldman Sachs
Developed internal financial dashboards for risk analysis using React.js
Built secure backend services with Node.js for transaction processing
Implemented authentication and data encryption for sensitive financial data
Client: HSBC
Created customer onboarding platform
Integrated KYC verification APIs
Improved API response time by 25%

Software Developer
Tata Consultancy Services, Hyderabad
May 2022 – May 2023
Client: Walmart
Developed e-commerce modules for product and order management
Built REST APIs for inventory tracking
Improved UI performance using React optimization techniques
Client: Target
Designed admin dashboards for managing large-scale product catalogs
Implemented advanced filtering and search features

Junior Web Developer
Wipro, Hyderabad
April 2021 – April 2022
Client: UnitedHealth Group
Developed patient management system
Built responsive UI for healthcare dashboards
Assisted in backend API development
Client: Pfizer
Worked on internal medical data tracking applications
Fixed bugs and improved system performance

EDUCATION
Bachelor of Technology (B.Tech) in Computer Science
JNTU Hyderabad
2017 – 2021
CGPA: 7.8/10

PROJECTS
Loan Management System
Built a fintech application for loan lifecycle management
Tech Stack: React.js, Node.js, MongoDB

E-commerce Platform
Developed scalable shopping application
Tech Stack: MERN Stack
"""
    
    print("🧪 TESTING ANJANA'S RESUME PARSING")
    print("=" * 70)
    
    # Initialize MasterParser
    try:
        parser = MasterParser()
        print("✅ MasterParser initialized successfully")
        
        # Check if DeBERTa parser is available
        if hasattr(parser, 'deberta_parser') and parser.deberta_parser:
            if parser.deberta_parser.is_available():
                print("✅ DeBERTa NER Parser is available and loaded")
            else:
                print("⚠️  DeBERTa NER Parser not available - will use fallback")
        
        # Test parsing
        print("\n🔍 Testing resume parsing with section-based DeBERTa...")
        result = parser.parse_text(resume_text, "anjana-reddy-001")
        
        # Display results
        print(f"\n{'='*70}")
        print("📊 PARSING RESULTS")
        print(f"{'='*70}")
        
        print(f"\n👤 Personal Information:")
        print(f"   Name: {result.get('name')}")
        print(f"   Email: {result.get('email')}")
        print(f"   Phone: {result.get('phone')}")
        print(f"   LinkedIn: {result.get('linkedin')}")
        print(f"   GitHub: {result.get('github')}")
        
        print(f"\n🏢 Companies Extracted:")
        companies = result.get('companies', [])
        if companies:
            for i, company in enumerate(companies[:10], 1):
                print(f"   {i}. {company}")
        else:
            print("   ❌ No companies found")
        
        print(f"\n📍 Locations Extracted:")
        locations = result.get('locations', [])
        if locations:
            for i, location in enumerate(locations[:10], 1):
                print(f"   {i}. {location}")
        else:
            print("   ❌ No locations found")
        
        print(f"\n💼 Job Titles Extracted:")
        job_titles = result.get('job_titles', [])
        if job_titles:
            for i, title in enumerate(job_titles[:10], 1):
                print(f"   {i}. {title}")
        else:
            print("   ❌ No job titles found")
        
        print(f"\n💼 Work Experience:")
        work_exp = result.get('work_experience', [])
        if work_exp:
            for i, exp in enumerate(work_exp, 1):
                print(f"\n   Experience {i}:")
                print(f"   Company: {exp.get('company_name', exp.get('company', 'N/A'))}")
                print(f"   Role: {exp.get('job_title', exp.get('role', 'N/A'))}")
                print(f"   Location: {exp.get('location', 'N/A')}")
                print(f"   Duration: {exp.get('start_date', 'N/A')} to {exp.get('end_date', 'Present' if exp.get('is_current') else 'N/A')}")
        else:
            print("   ❌ No work experience found")
        
        print(f"\n🎓 Education:")
        education = result.get('education', [])
        if education:
            for i, edu in enumerate(education, 1):
                print(f"\n   Education {i}:")
                print(f"   Degree: {edu.get('degree', 'N/A')}")
                print(f"   Field: {edu.get('field_of_study', 'N/A')}")
                print(f"   Institution: {edu.get('institution', 'N/A')}")
                print(f"   Year: {edu.get('start_year', 'N/A')} - {edu.get('end_year', 'N/A')}")
        else:
            print("   ❌ No education found")
        
        print(f"\n💻 Skills: {len(result.get('skills', []))} skills")
        
        # Check processing metrics
        print(f"\n⏱️  Processing Metrics:")
        processing_metrics = result.get('processing_metrics', {})
        timing = processing_metrics.get('timing_ms', {})
        print(f"   DeBERTa parsing: {timing.get('deberta_parsing_ms', 0):.1f}ms")
        print(f"   Total processing: {timing.get('total_ms', 0):.1f}ms")
        
        # Expected vs Actual
        print(f"\n{'='*70}")
        print("✅ EXPECTED VALUES:")
        print(f"{'='*70}")
        print("Companies: ['Infosys', 'Tata Consultancy Services', 'Wipro']")
        print("Locations: ['Bangalore', 'Hyderabad']")
        print("Job Titles: ['Full Stack Developer', 'Software Developer', 'Junior Web Developer']")
        print("Clients: ['Goldman Sachs', 'HSBC', 'Walmart', 'Target', 'UnitedHealth Group', 'Pfizer']")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_anjana_resume()
    if success:
        print("\n🎉 Anjana's resume parsing test completed!")
    else:
        print("\n💥 Anjana's resume parsing test failed!")
        sys.exit(1)
