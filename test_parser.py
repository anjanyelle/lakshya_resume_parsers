#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app.services.enhanced_pipeline_final import EnhancedResumePipelineFinal

# Test with a sample resume text
sample_resume = '''
## PROFESSIONAL EXPERIENCE

Client: Amazon
Location: Seattle, WA
Role: Senior Software Engineer
June 2020 - Present
- Led development of cloud infrastructure
- Managed team of 5 engineers

Client: Microsoft
Location: Redmond, WA
Role: Software Engineer
Jan 2018 - May 2020
- Developed Azure services
- Improved system performance by 40%

## EDUCATION

University of Washington - Bachelor of Science in Computer Science
2014 - 2018

## SKILLS

Python, Java, AWS, Azure, Docker

## CERTIFICATIONS

AWS Certified Solutions Architect - 2021
Microsoft Certified: Azure Developer Associate - 2019
'''

def test_parsing():
    print("🧪 Testing optimized resume parser...")
    parser = EnhancedResumePipelineFinal()
    
    try:
        result = parser.parse_resume_complete(sample_resume)
        print('✅ Parsing completed successfully!')
        print(f'Work entries: {len(result.get("work", []))}')
        print(f'Education entries: {len(result.get("education", []))}')
        print(f'Skills entries: {len(result.get("skills", []))}')
        print(f'Certifications: {len(result.get("certifications", []))}')
        
        # Print detailed results
        print("\n📋 Work Experience:")
        for i, work in enumerate(result.get("work", [])):
            print(f"  {i+1}. {work.get('company', 'Unknown')} - {work.get('title', 'Unknown')}")
        
        print("\n🎓 Education:")
        for i, edu in enumerate(result.get("education", [])):
            print(f"  {i+1}. {edu.get('institution', 'Unknown')} - {edu.get('degree', 'Unknown')}")
        
        print("\n🏆 Certifications:")
        for i, cert in enumerate(result.get("certifications", [])):
            print(f"  {i+1}. {cert.get('name', 'Unknown')}")
            print(f"      Issuer: {cert.get('issuer', 'Unknown')}")
            print(f"      Date: {cert.get('date', 'Unknown')}")
            print(f"      Credential ID: {cert.get('credential_id', 'Unknown')}")
            print(f"      Status: {cert.get('status', 'Unknown')}")
            print(f"      Description: {cert.get('description', 'Unknown')[:50]}...")
            if cert.get('url'):
                print(f"      URL: {cert.get('url')}")
        
        return True
        
    except Exception as e:
        print(f'❌ Error: {e}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_parsing()
    sys.exit(0 if success else 1)
