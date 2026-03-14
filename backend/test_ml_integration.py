#!/usr/bin/env python3
"""
Test ML Integration with Enhanced Parser
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

def test_enhanced_parser():
    """Test the enhanced parser with ML models"""
    print("🧪 Testing Enhanced Parser with ML Models")
    print("=" * 50)
    
    try:
        from app.services.parser.enhanced_parser_integration import EnhancedParserIntegration
        
        # Initialize parser
        parser = EnhancedParserIntegration()
        print("✅ Enhanced Parser initialized")
        
        # Check ML status
        ml_status = parser.get_ml_model_status()
        print(f"🤖 ML Models Available: {ml_status['available']}")
        print(f"📊 Models Loaded: {ml_status.get('models_loaded', False)}")
        
        # Test resume
        test_resume = """
        John Doe
        Senior Software Engineer
        john.doe@email.com | (555) 123-4567 | LinkedIn: linkedin.com/in/johndoe
        
        PROFESSIONAL EXPERIENCE
        Senior Software Engineer at Google
        Mountain View, CA | 2020-Present
        - Developed microservices using Python and AWS
        - Led team of 5 engineers
        - Improved system performance by 40%
        
        Software Engineer at Microsoft  
        Redmond, WA | 2018-2020
        - Built REST APIs with Node.js and React
        - Worked with Azure cloud services
        - Optimized database queries
        
        EDUCATION
        Bachelor of Science in Computer Science
        Stanford University | 2014-2018
        GPA: 3.8
        
        SKILLS
        Python, JavaScript, AWS, Docker, Kubernetes, React, Node.js, 
        Machine Learning, Data Analysis, SQL, NoSQL
        """
        
        print("\n📄 Parsing Test Resume...")
        
        # Parse with enhanced parser
        result = parser.parse_resume_enhanced(test_resume)
        
        print(f"✅ Parsing completed successfully!")
        print(f"📊 Overall Confidence: {result.confidence_scores.get('overall', 0):.2f}")
        print(f"⏱️  Processing Time: {result.processing_time:.2f}s")
        print(f"💼 Experiences Parsed: {len(result.experiences)}")
        print(f"🎓 Education Parsed: {len(result.education)}")
        print(f"🛠️  Technical Skills: {len(result.skills.technical_skills)}")
        
        # Show sample results
        if result.experiences:
            print("\n💼 Sample Experience:")
            exp = result.experiences[0]
            print(f"   Company: {exp.company}")
            print(f"   Title: {exp.title}")
            print(f"   Location: {exp.location}")
            print(f"   Confidence: {exp.company_confidence:.2f}")
        
        if result.skills.technical_skills:
            print("\n🛠️  Sample Skills:")
            for skill, conf in result.skills.technical_skills[:5]:
                print(f"   {skill} ({conf:.2f})")
        
        # Get parser statistics
        stats = parser.get_parser_statistics()
        print(f"\n📈 Parser Statistics:")
        print(f"   Total Parsed: {stats['performance']['total_parsed']}")
        print(f"   Success Rate: {stats['performance']['successful_parses']}")
        print(f"   Avg Confidence: {stats['performance']['average_confidence']:.2f}")
        
        print("\n🎉 ML Integration Test PASSED!")
        return True
        
    except Exception as e:
        print(f"❌ Test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_enhanced_parser()
    sys.exit(0 if success else 1)
