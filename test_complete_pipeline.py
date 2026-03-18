#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app.services.enhanced_pipeline_final import EnhancedResumePipelineFinal

def test_complete_pipeline():
    """Test the complete pipeline with frontend mapping"""
    
    # Sample resume text
    sample_resume = '''
## PROFESSIONAL SUMMARY

High-impact Revenue Executive with 12+ years of experience engineering hyper-growth for global technology leaders and high-valuation startups. Expert in the orchestration of integrated Sales, Marketing, and Customer Success ecosystems, specializing in transitioning organizations from transactional models to high-velocity, solution-based Enterprise engines.

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
    
    print("🧪 Testing Complete Pipeline with Frontend Mapping...")
    
    # Initialize parser
    parser = EnhancedResumePipelineFinal()
    
    # Parse resume
    result = parser.parse_resume_complete(sample_resume)
    
    print("\n📋 FINAL RESULT FOR FRONTEND:")
    print("=" * 60)
    
    # Pretty print the JSON structure
    import json
    print(json.dumps(result, indent=2))
    
    print("=" * 60)
    
    return result

if __name__ == "__main__":
    test_complete_pipeline()
