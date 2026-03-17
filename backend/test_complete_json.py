# Test Complete Resume JSON Format

import json
import sys
import os

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.enhanced_pipeline import EnhancedResumePipeline
from app.services.ml_complete_parser import MLResumeParser

def test_complete_json_format():
    """
    Test the complete resume JSON format implementation
    """
    
    # Sample resume text (similar to your target format)
    sample_resume = """
    Dominic Thorne
    (615) 555-0144 | d.thorne.revenue@growth-nexus.com | linkedin.com/in/dominic-thorne-growth
    
    PROFESSIONAL SUMMARY
    High-impact Revenue Executive with 12+ years of experience engineering hyper-growth for global technology leaders and high-valuation startups. Expert in the orchestration of integrated Sales, Marketing, and Customer Success ecosystems, specializing in transitioning organizations from transactional models to high-velocity, solution-based Enterprise engines.
    
    WORK EXPERIENCE
    
    Chief Revenue Officer
    OmniStream Global
    Nashville, TN
    2021 - Present
    
    - Strategic Mandate & Executive Oversight: Directly responsible for the global P&L across Sales, Marketing, and Partner Channels for an organization of 1,200 employees.
    - Revenue Transformation: Engineered a strategic pivot to a "Land and Expand" model, increasing Net Revenue Retention (NRR) from 94% to 122% within 24 months.
    
    VP of Global Marketing & Demand Generation
    NexaHealth Tech
    Austin, TX
    2017 - 2021
    
    - Operational Leadership: Directed global marketing function for a high-growth Healthtech firm. Led a team of 95 specialists across brand, demand generation, product marketing, and field operations.
    - Growth Modeling: Developed a proprietary "Predictive Demand Model" that forecasted pipeline within 5% accuracy.
    
    EDUCATION
    
    Master of Business Administration (MBA)
    Strategic Management & Marketing
    The University of Chicago Booth School of Business
    Chicago, IL
    
    Bachelor of Science
    Mathematical Economics & Data Science
    Vanderbilt University
    Nashville, TN
    
    PROJECTS
    
    Project Apex: The "Total Revenue Unification" (TRU) Initiative
    Objective: Consolidate Sales, Marketing, and Success data into a single source of truth to eliminate churn and maximize expansion opportunities.
    Outcome: Reduced churn from 12% to 4% in one fiscal year.
    
    PUBLICATIONS
    
    The Revenue Architect: Building Sustainable Growth in Saturated Markets
    Harvard Business Review (Executive Perspectives)
    2023
    
    CERTIFICATIONS
    
    Salesforce Certified Sales Cloud Consultant
    Marketo Certified Solutions Architect (MCSA)
    HubSpot RevOps Professional Certification
    
    SKILLS
    
    Sales & Revenue Operations (RevOps)
    - CRM Ecosystems: Salesforce (Advanced Architect), HubSpot Enterprise, Microsoft Dynamics 365
    - Sales Enablement: Gong.io, Chorus.ai, Highspot, Outreach, Salesloft
    
    LANGUAGES
    
    English: Native Proficiency
    Spanish: Professional Working Proficiency (C1)
    German: Conversational
    """
    
    print("🔍 Testing Complete Resume JSON Format...")
    print("=" * 60)
    
    # Test ML Parser
    print("1️⃣ Testing ML Parser...")
    ml_parser = MLResumeParser()
    ml_result = ml_parser.parse_complete_resume(sample_resume)
    
    print(f"✅ ML Parser Results:")
    print(f"   - Basics: {len(ml_result.get('basics', {}))} fields")
    print(f"   - Work: {len(ml_result.get('work', []))} entries")
    print(f"   - Education: {len(ml_result.get('education', []))} entries")
    print(f"   - Projects: {len(ml_result.get('projects', []))} entries")
    print(f"   - Publications: {len(ml_result.get('publications', []))} entries")
    print(f"   - Skills: {len(ml_result.get('skills', []))} categories")
    print()
    
    # Test Enhanced Pipeline
    print("2️⃣ Testing Enhanced Pipeline...")
    pipeline = EnhancedResumePipeline()
    pipeline_result = pipeline.parse_resume_complete(sample_resume, use_ml=True)
    
    print(f"✅ Enhanced Pipeline Results:")
    print(f"   - Basics: {pipeline_result.get('basics') is not None}")
    print(f"   - Profile: {pipeline_result.get('profile') is not None}")
    print(f"   - Work: {len(pipeline_result.get('work') or [])} entries")
    print(f"   - Education: {len(pipeline_result.get('education') or [])} entries")
    print(f"   - Projects: {len(pipeline_result.get('projects') or [])} entries")
    print(f"   - Publications: {len(pipeline_result.get('publications') or [])} entries")
    print(f"   - Skills: {len(pipeline_result.get('skills') or [])} categories")
    print()
    
    # Test Target Format Compliance
    print("3️⃣ Testing Target Format Compliance...")
    
    required_sections = [
        'basics', 'profile', 'work', 'education', 'projects',
        'volunteer', 'skills', 'certifications', 'publications',
        'awards', 'achievements', 'hobbies', 'references', 'texts'
    ]
    
    compliance_score = 0
    for section in required_sections:
        if section in pipeline_result:
            compliance_score += 1
            print(f"   ✅ {section}: Present")
        else:
            print(f"   ❌ {section}: Missing")
    
    compliance_percentage = (compliance_score / len(required_sections)) * 100
    print(f"\n📊 Format Compliance: {compliance_percentage:.1f}%")
    
    # Show sample of target format
    print("\n4️⃣ Sample Target JSON Output:")
    print("-" * 40)
    
    # Show basics
    if pipeline_result.get('basics'):
        basics = pipeline_result['basics']
        print("basics:")
        print(f"  firstName: {basics.get('firstName')}")
        print(f"  lastName: {basics.get('lastName')}")
        print(f"  email: {basics.get('email')}")
        print(f"  phone: {basics.get('phone')}")
        print(f"  city: {basics.get('city')}")
        print(f"  country: {basics.get('country')}")
    
    # Show work
    if pipeline_result.get('work'):
        work = pipeline_result['work']
        print(f"\nwork ({len(work)} entries):")
        for i, job in enumerate(work[:2]):  # Show first 2
            print(f"  {i+1}. {job.get('jobTitle')} at {job.get('company')}")
            print(f"     {job.get('startDate')} - {job.get('endDate')}")
            print(f"     {job.get('city')}, {job.get('country')}")
    
    # Show skills
    if pipeline_result.get('skills'):
        skills = pipeline_result['skills']
        print(f"\nskills ({len(skills)} categories):")
        for skill_cat in skills[:3]:  # Show first 3
            print(f"  - {skill_cat.get('name')}: {len(skill_cat.get('skills', []))} skills")
    
    print("\n" + "=" * 60)
    print("🎉 Complete Resume JSON Format Test Completed!")
    
    # Save results to file
    with open('complete_resume_test_output.json', 'w') as f:
        json.dump(pipeline_result, f, indent=2, default=str)
    
    print("💾 Results saved to: complete_resume_test_output.json")
    
    return pipeline_result

if __name__ == "__main__":
    test_complete_json_format()
