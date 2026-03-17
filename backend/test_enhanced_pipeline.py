#!/usr/bin/env python3
"""
Test the enhanced pipeline with all fixes implemented
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.enhanced_pipeline_final import EnhancedResumePipelineFinal

def test_enhanced_pipeline():
    """Test the enhanced pipeline with Pavan's resume"""
    
    # Pavan's resume text
    pavan_resume = """Pavan Kumar
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
"""
    
    print("🚀 Testing Enhanced Pipeline with All Fixes")
    print("=" * 50)
    
    try:
        # Initialize the enhanced parser
        parser = EnhancedResumePipelineFinal()
        
        # Parse the resume
        result = parser.parse_resume_complete(pavan_resume)
        
        print("✅ Enhanced Pipeline Parsing Complete!")
        print("\n📊 RESULTS:")
        print(f"👤 Name: {result.get('basics', {}).get('name', 'N/A')}")
        print(f"📧 Email: {result.get('basics', {}).get('email', 'N/A')}")
        print(f"📞 Phone: {result.get('basics', {}).get('phone', 'N/A')}")
        print(f"💼 Work Entries: {len(result.get('work', []))}")
        print(f"🎓 Education Entries: {len(result.get('education', []))}")
        print(f"🔧 Skills: {len(result.get('skills', []))}")
        print(f"🏆 Certifications: {len(result.get('certifications', []))}")
        
        print("\n💼 WORK EXPERIENCE:")
        for i, work in enumerate(result.get('work', []), 1):
            print(f"  {i}. {work.get('company', 'N/A')} - {work.get('title', 'N/A')}")
            print(f"     📍 {work.get('location', 'N/A')}")
            print(f"     📅 {work.get('date_range', 'N/A')}")
            print(f"     📝 {work.get('description', 'N/A')[:100]}...")
            print()
        
        print("\n🔧 SKILLS:")
        for skill in result.get('skills', [])[:10]:
            print(f"  • {skill.get('name', 'N/A')}")
        
        print("\n🏆 CERTIFICATIONS:")
        for cert in result.get('certifications', []):
            print(f"  • {cert.get('name', 'N/A')}")
        
        # Calculate accuracy score
        expected_companies = ["Bank of America", "Starbucks", "Credit Karma", "Amazon", "ADP"]
        extracted_companies = [work.get('company', '').strip() for work in result.get('work', [])]
        
        company_matches = sum(1 for company in expected_companies if company in extracted_companies)
        company_accuracy = (company_matches / len(expected_companies)) * 100
        
        print(f"\n🎯 ACCURACY SCORE:")
        print(f"  🏢 Company Extraction: {company_accuracy:.1f}% ({company_matches}/{len(expected_companies)})")
        
        if company_accuracy >= 80:
            print("  ✅ EXCELLENT: Company extraction accuracy ≥ 80%")
        elif company_accuracy >= 60:
            print("  ⚠️ GOOD: Company extraction accuracy ≥ 60%")
        else:
            print("  ❌ NEEDS IMPROVEMENT: Company extraction accuracy < 60%")
        
        return result
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    test_enhanced_pipeline()
