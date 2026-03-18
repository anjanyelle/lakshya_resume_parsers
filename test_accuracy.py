#!/usr/bin/env python3

import sys
import os
import json
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app.services.enhanced_pipeline_final import EnhancedResumePipelineFinal

# Test with multiple resume formats
test_resumes = [
    {
        "name": "Standard Header Format",
        "resume": '''
## PROFESSIONAL EXPERIENCE

Amazon Web Services | Seattle, WA
Senior Software Engineer | June 2020 - Present
- Led development of cloud infrastructure
- Managed team of 5 engineers

Microsoft | Redmond, WA
Software Engineer | January 2018 - May 2020
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
    },
    {
        "name": "Client Format (Ramu Gara)",
        "resume": '''
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
January 2018 - May 2020
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
    },
    {
        "name": "Company Date Format",
        "resume": '''
## PROFESSIONAL EXPERIENCE

Amazon: June 2020 - Present (Location: Seattle, WA)
Senior Software Engineer
- Led development of cloud infrastructure
- Managed team of 5 engineers

Microsoft: January 2018 - May 2020 (Location: Redmond, WA)
Software Engineer
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
    },
    {
        "name": "No Headers Format",
        "resume": '''
John Doe
john.doe@email.com
(555) 123-4567

Senior Software Engineer with 5+ years of experience in cloud computing and full-stack development.

Amazon Web Services
Seattle, WA
Senior Software Engineer
June 2020 - Present
- Led development of cloud infrastructure
- Managed team of 5 engineers

Microsoft
Redmond, WA
Software Engineer
January 2018 - May 2020
- Developed Azure services
- Improved system performance by 40%

University of Washington
Bachelor of Science in Computer Science
2014 - 2018

Skills: Python, Java, AWS, Azure, Docker

Certifications:
AWS Certified Solutions Architect - 2021
Microsoft Certified: Azure Developer Associate - 2019
        '''
    }
]

def test_accuracy():
    print("🧪 Testing Resume Parser Accuracy with Multiple Formats...")
    parser = EnhancedResumePipelineFinal()
    
    total_tests = len(test_resumes)
    successful_tests = 0
    
    for i, test_case in enumerate(test_resumes):
        print(f"\n📋 Test {i+1}/{total_tests}: {test_case['name']}")
        print("=" * 50)
        
        try:
            result = parser.parse_resume_complete(test_case['resume'])
            
            # Evaluate results
            work_count = len(result.get("work", []))
            education_count = len(result.get("education", []))
            skills_count = len(result.get("skills", []))
            cert_count = len(result.get("certifications", []))
            data_quality = result.get("metadata", {}).get("data_quality", 0)
            
            print(f"✅ Work Entries: {work_count}")
            print(f"✅ Education Entries: {education_count}")
            print(f"✅ Skills: {skills_count}")
            print(f"✅ Certifications: {cert_count}")
            print(f"✅ Data Quality: {data_quality}/100")
            
            # Check for expected results
            expected_work = 2
            expected_education = 1
            expected_skills = 5
            expected_certs = 2
            
            score = 0
            if work_count >= expected_work:
                score += 25
                print(f"  ✅ Work extraction: SUCCESS")
            else:
                print(f"  ❌ Work extraction: FAILED (expected {expected_work}, got {work_count})")
            
            if education_count >= expected_education:
                score += 25
                print(f"  ✅ Education extraction: SUCCESS")
            else:
                print(f"  ❌ Education extraction: FAILED (expected {expected_education}, got {education_count})")
            
            if skills_count >= expected_skills:
                score += 25
                print(f"  ✅ Skills extraction: SUCCESS")
            else:
                print(f"  ❌ Skills extraction: FAILED (expected {expected_skills}, got {skills_count})")
            
            if cert_count >= expected_certs:
                score += 25
                print(f"  ✅ Certifications extraction: SUCCESS")
            else:
                print(f"  ❌ Certifications extraction: FAILED (expected {expected_certs}, got {cert_count})")
            
            if score >= 75:
                successful_tests += 1
                print(f"  🎯 Overall: SUCCESS ({score}/100)")
            else:
                print(f"  ❌ Overall: FAILED ({score}/100)")
                
        except Exception as e:
            print(f"  ❌ Parsing Error: {e}")
    
    print(f"\n🏆 Final Results:")
    print(f"Successful Tests: {successful_tests}/{total_tests}")
    print(f"Accuracy: {(successful_tests/total_tests)*100:.1f}%")
    
    return successful_tests == total_tests

if __name__ == "__main__":
    success = test_accuracy()
    sys.exit(0 if success else 1)
