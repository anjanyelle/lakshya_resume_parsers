#!/usr/bin/env python3

import sys
import os
sys.path.append('backend')
sys.path.append('backend/app')

from app.services.enhanced_pipeline_final import EnhancedResumePipelineFinal

pipeline = EnhancedResumePipelineFinal()

resume_text = """DOMINIC R. THORNE
Chief Revenue Officer | Executive VP of Global Sales, Marketing & Growth Strategy
Nashville, TN • (615) 555-0144 • d.thorne.revenue@growth-nexus.com linkedin.com/in/dominic-thorne-growth • US Citizen"""

print("🚀 TESTING FIXED ENHANCED PIPELINE...")
result = pipeline.parse_resume_complete(resume_text)

print("✅ ENHANCED PIPELINE SUCCESS!")
print("📊 FINAL RESULTS:")
print(f"  Work entries: {len(result.get('work', []))}")
print(f"  Skills entries: {len(result.get('skills', []))}")
print(f"  Education entries: {len(result.get('education', []))}")
print(f"  Certifications: {len(result.get('certifications', []))}")

print("\n📋 WORK EXPERIENCE:")
for i, work in enumerate(result.get('work', [])[:4]):
    company = work.get('company', '')
    title = work.get('title', '')
    start = work.get('start_date', '')
    end = work.get('end_date', '')
    is_current = work.get('is_current', False)
    location = work.get('location', '')
    print(f"  {i+1}. {title} at {company}")
    print(f"      Dates: {start} - {end if end else 'Current'}")
    print(f"      Location: {location}")

print("\n🎯 SKILLS (first 10):")
for i, skill in enumerate(result.get('skills', [])[:10]):
    skill_name = skill.get('name', '') if isinstance(skill, dict) else skill
    print(f"  {i+1}. {skill_name}")

print("\n🏆 CERTIFICATIONS (first 5):")
for i, cert in enumerate(result.get('certifications', [])[:5]):
    cert_name = cert.get('name', '')
    issuer = cert.get('issuer', '')
    print(f"  {i+1}. {cert_name} from {issuer}")
