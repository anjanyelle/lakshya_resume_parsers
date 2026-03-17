#!/usr/bin/env python3

from app.services.enhanced_pipeline_final import EnhancedResumePipelineFinal

pipeline = EnhancedResumePipelineFinal()

test_text = '''Pavan Kumar
https://www.linkedin.com/in/pavan-kumar-10rad/ | +1(859) 567-9177 | pavan03248@gmail.com

## PROFESSIONAL EXPERIENCE
Bank of America North Carolina
Sr. Full Stack Developer July 2021 - Present

## TECHNICAL SKILLS
Java, Spring Boot, Angular, React, Docker, Kubernetes

## EDUCATION
Bharath University - Bachelor of Technology Computer Science August 2010 to May 2014

## CERTIFICATIONS
AWS Certified Developer - Associate
'''

print("🔍 Testing Comprehensive Parsing...")
try:
    result = pipeline.parse_resume_complete(test_text)
    print("✅ COMPREHENSIVE PARSING SUCCESS!")
    print(f"Work entries: {len(result.get('work', []))}")
    print(f"Education entries: {len(result.get('education', []))}")
    print(f"Skills entries: {len(result.get('skills', []))}")
    print(f"Certifications: {len(result.get('certifications', []))}")
    print(f"Achievements: {len(result.get('achievements', []))}")
    
    # Show first work entry
    if result.get('work'):
        work = result['work'][0]
        print(f"First work entry: {work}")
    
except Exception as e:
    print(f"❌ COMPREHENSIVE PARSING FAILED: {e}")
    print("🔄 Falling back to basic parsing...")
