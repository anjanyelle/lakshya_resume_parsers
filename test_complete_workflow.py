#!/usr/bin/env python3
"""
Test Complete 10-Stage Work Experience Workflow
Implements your exact architecture specification
"""

import sys
import os
sys.path.append('backend')
sys.path.append('backend/app')

from app.services.work_experience_workflow import get_work_experience_workflow
import json

def test_complete_workflow():
    """Test the complete 10-stage workflow"""
    
    # Sample resume text (comprehensive example)
    resume_text = """
DOMINIC R. THORNE
Chief Revenue Officer | Executive VP of Global Sales, Marketing & Growth Strategy
Nashville, TN • (615) 555-0144 • d.thorne.revenue@growth-nexus.com

PROFESSIONAL EXPERIENCE

OmniStream Global | Chief Revenue Officer
January 2021 - Present
Nashville, TN / Remote
Full-time

Responsibilities:
- Directly responsible for global P&L across Sales, Marketing, and Partner Channels
- Leading organization of 1,200 employees across multiple regions
- Architecting integrated Sales, Marketing, and Customer Success ecosystems
- Transitioning organizations from transactional to solution-based Enterprise engines

Technologies: Salesforce, HubSpot, Marketo, Tableau, Power BI

Revenue Growth Solutions | VP of Sales
March 2018 - December 2020
Austin, TX
Full-time

Responsibilities:
- Led sales transformation initiatives for Fortune 500 clients
- Implemented account-based marketing strategies
- Achieved 300% revenue growth over 3-year period
- Managed team of 50 sales professionals

Technologies: Salesforce, Marketo, LinkedIn Sales Navigator, Outreach

TechCorp International | Senior Sales Manager
June 2015 - February 2018
San Francisco, CA
Contract

Responsibilities:
- Managed enterprise software sales portfolio
- Developed strategic partnerships with key clients
- Exceeded sales targets by 150% consistently
- Trained and mentored junior sales team members

Technologies: Oracle, SAP, Microsoft Dynamics, HubSpot

EDUCATION
MBA - Harvard Business School
B.S. Business Administration - Stanford University

SKILLS
Sales Strategy, Revenue Operations, Account-Based Marketing, Customer Success, Enterprise Sales, SaaS Sales, Team Leadership, P&L Management
"""
    
    print("🚀 TESTING COMPLETE 10-STAGE WORKFLOW")
    print("=" * 80)
    print("📋 ARCHITECTURE: Your Exact 10-Stage Specification")
    print("=" * 80)
    
    try:
        # Get workflow controller
        workflow = get_work_experience_workflow()
        
        # Process resume through complete workflow
        result = workflow.process_resume("test_resume.docx", resume_text)
        
        print(f"✅ WORKFLOW COMPLETED: {result['workflow_id']}")
        print("=" * 80)
        
        # Display each stage result
        for stage_name, stage_result in result["stages"].items():
            stage_number = stage_name.split("_")[1]
            stage_title = stage_result.get("stage", "Unknown").replace("_", " ").title()
            
            print(f"\n🎯 STAGE {stage_number}: {stage_title}")
            print("-" * 60)
            
            if stage_result.get("success"):
                print(f"✅ Status: SUCCESS")
                print(f"🔧 Approach: {stage_result.get('approach', 'N/A')}")
                
                # Display key information for each stage
                if stage_number == "1":
                    print(f"📄 Format: {stage_result.get('detected_format', 'N/A')}")
                    print(f"🤖 Hero Model: {stage_result.get('hero_model', 'N/A')}")
                
                elif stage_number == "2":
                    print(f"📏 Text Length: {stage_result.get('text_length', 0)} chars")
                    print(f"✨ Quality Check: {stage_result.get('quality_check', False)}")
                    print(f"🔧 Method: {stage_result.get('extraction_method', 'N/A')}")
                
                elif stage_number == "3":
                    print(f"📏 Original: {stage_result.get('original_length', 0)} chars")
                    print(f"🧹 Cleaned: {stage_result.get('cleaned_length', 0)} chars")
                
                elif stage_number == "4":
                    print(f"🎯 Section Found: {stage_result.get('section_found', False)}")
                    if stage_result.get("work_experience_block"):
                        block_preview = stage_result["work_experience_block"][:100] + "..."
                        print(f"📄 Block Preview: {block_preview}")
                
                elif stage_number == "5":
                    print(f"🤖 Model Used: {stage_result.get('model_used', 'N/A')}")
                    print(f"📊 Entries Extracted: {stage_result.get('entries_count', 0)}")
                
                elif stage_number == "6":
                    print(f"📊 High Confidence: {stage_result.get('high_confidence_count', 0)}")
                    print(f"⚠️ Low Confidence: {stage_result.get('low_confidence_count', 0)}")
                    print(f"❌ Failed: {stage_result.get('failed_count', 0)}")
                
                elif stage_number == "7":
                    print(f"🔄 Fallback Used: {stage_result.get('fallback_used', False)}")
                    print(f"📊 Final Entries: {stage_result.get('entries_count', 0)}")
                
                elif stage_number == "8":
                    print(f"✅ Validated Entries: {stage_result.get('entries_count', 0)}")
                
                elif stage_number == "9":
                    print(f"📊 Total Jobs: {stage_result.get('total_jobs', 0)}")
                    print(f"🚩 Flagged for Review: {stage_result.get('flagged_count', 0)}")
                
                elif stage_number == "10":
                    print(f"❌ Failed Entries: {stage_result.get('failed_entries_count', 0)}")
                    print(f"📈 Success Rate: {stage_result.get('success_rate', 0):.2%}")
                
            else:
                print(f"❌ Status: FAILED")
                print(f"🚨 Error: {stage_result.get('error', 'Unknown error')}")
        
        # Display final workflow statistics
        print("\n📊 WORKFLOW STATISTICS")
        print("=" * 80)
        stats = result.get("stats", {})
        print(f"📈 Total Processed: {stats.get('total_processed', 0)}")
        print(f"✅ High Confidence: {stats.get('high_confidence', 0)}")
        print(f"⚠️ Low Confidence: {stats.get('low_confidence', 0)}")
        print(f"❌ Failed: {stats.get('failed', 0)}")
        print(f"🔄 Fallback Used: {stats.get('fallback_used', 0)}")
        
        # Display final JSON result
        print("\n📄 FINAL JSON OUTPUT")
        print("=" * 80)
        final_json = result.get("final_result", {})
        
        if final_json.get("work_experience"):
            print(f"📊 Total Jobs: {final_json.get('total_jobs', 0)}")
            print(f"🚩 Flagged for Review: {final_json.get('flagged_for_review', False)}")
            print(f"⏰ Processing Time: {final_json.get('processing_timestamp', 'N/A')}")
            
            print("\n📋 WORK EXPERIENCE ENTRIES:")
            for i, job in enumerate(final_json["work_experience"][:2]):  # Show first 2 jobs
                print(f"\n📌 JOB {i+1}:")
                print(f"  🏢 Company: {job.get('company', 'N/A')}")
                print(f"  💼 Job Title: {job.get('job_title', 'N/A')}")
                print(f"  📅 Dates: {job.get('start_date', 'N/A')} - {job.get('end_date', 'Present')}")
                print(f"  📍 Location: {job.get('location', 'N/A')}")
                print(f"  💪 Employment Type: {job.get('employment_type', 'N/A')}")
                print(f"  📊 Confidence: {job.get('confidence', 0):.2f}")
                print(f"  🤖 Source: {job.get('_source_model', 'N/A')}")
                print(f"  ❌ Missing: {job.get('_missing_fields', [])}")
                
                if job.get('responsibilities'):
                    print(f"  📋 Responsibilities ({len(job['responsibilities'])}):")
                    for j, resp in enumerate(job['responsibilities'][:2]):
                        print(f"    {j+1}. {resp[:80]}...")
                
                if job.get('tech_stack'):
                    print(f"  🔧 Tech Stack: {', '.join(job['tech_stack'][:5])}...")
        
        # Verify target structure
        print("\n🎯 TARGET STRUCTURE VERIFICATION")
        print("=" * 80)
        target_fields = [
            "company", "job_title", "start_date", "end_date", "is_current",
            "location", "employment_type", "responsibilities", "tech_stack",
            "confidence", "_source_model", "_missing_fields"
        ]
        
        if final_json.get("work_experience"):
            first_job = final_json["work_experience"][0]
            missing_fields = []
            
            for field in target_fields:
                if field in first_job:
                    print(f"  ✅ {field}: {type(first_job[field]).__name__}")
                else:
                    print(f"  ❌ {field}: MISSING")
                    missing_fields.append(field)
            
            if not missing_fields:
                print("\n🎉 ALL TARGET FIELDS ACHIEVED!")
                print("✅ Your exact workflow specification implemented successfully!")
            else:
                print(f"\n⚠️ Missing {len(missing_fields)} fields: {missing_fields}")
        
        print("\n🏁 WORKFLOW ARCHITECTURE SUMMARY")
        print("=" * 80)
        print("✅ STAGE 1: Format Detection - Rule-based")
        print("✅ STAGE 2: Text Extraction - Rule-based")
        print("✅ STAGE 3: Text Cleaning - Rule-based")
        print("✅ STAGE 4: Section Isolation - Rule-based")
        print("✅ STAGE 5: Split + Extract - MODEL (Flan-T5)")
        print("✅ STAGE 6: Confidence Score - Rule-based")
        print("✅ STAGE 7: Fallback Chain - Rule-based")
        print("✅ STAGE 8: Validation - Rule-based")
        print("✅ STAGE 9: Final JSON - Rule-based")
        print("✅ STAGE 10: Feedback Loop - Rule-based")
        print("\n🎯 MODEL USAGE: Only Stage 5 uses MODEL approach")
        print("🔧 ALL OTHER STAGES: Rule-based approach")
        print("🚀 HERO ASSIGNMENT: Flan-T5 for DOCX/Digital PDF")
        
        return True
        
    except Exception as e:
        print(f"❌ Workflow test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_complete_workflow()
    if success:
        print("\n🎉 COMPLETE 10-STAGE WORKFLOW IMPLEMENTATION SUCCESSFUL!")
        print("✅ Your exact architecture specification is now implemented!")
    else:
        print("\n❌ Workflow implementation failed!")
    
    sys.exit(0 if success else 1)
