#!/usr/bin/env python3

from backend.app.services.enhanced_pipeline_final import EnhancedResumePipelineFinal

pipeline = EnhancedResumePipelineFinal()

resume_text = """## Chief Revenue Officer | Omni Stream Global | 2021 - Present
- Nashville, TN / Remote (Enterprise Cloud Solutions | Annual Revenue: $1.5 B)
Strategic Mandate & Executive Oversight: Directly responsible for global P&L across Sales, Marketing, and Partner Channels for an organization of 1,200 employees."""

print("🚀 TESTING ENHANCED PIPELINE...")
result = pipeline.parse_resume_complete(resume_text)

print('✅ ENHANCED PIPELINE SUCCESS!')
print('WORK ENTRIES:', len(result.get('work', [])))

for i, work in enumerate(result.get('work', [])[:2]):
    company = work.get('company', '')
    title = work.get('title', '')
    start = work.get('start_date', '')
    end = work.get('end_date', '')
    print(f'Work {i+1}: Company="{company}" Title="{title}" Start="{start}" End="{end}"')
