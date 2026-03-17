#!/usr/bin/env python3

from app.services.enhanced_pipeline_final import EnhancedResumePipelineFinal

pipeline = EnhancedResumePipelineFinal()

test_text = '''Pavan Kumar
https://www.linkedin.com/in/pavan-kumar-10rad/ | +1(859) 567-9177 | pavan03248@gmail.com

## PROFESSIONAL EXPERIENCE
Bank of America North Carolina
Sr. Full Stack Developer July 2021 - Present

EDUCATION
Bharath University - Bachelor of Technology Computer Science August 2010 to May 2014
'''

print("🔍 Testing Enhanced Pipeline...")
result = pipeline.parse_resume_complete(test_text)

print(f"Work entries: {len(result.get('work', []))}")
print(f"Education entries: {len(result.get('education', []))}")
print(f"Skills entries: {len(result.get('skills', []))}")
print(f"Basics: {result.get('basics', {})}")
print(f"Complete sections: {list(result.keys())}")
