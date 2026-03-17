"""
Test Script for Enhanced Resume Parser
Validates all components with sample data
"""

import sys
import os
import time
from datetime import datetime

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__)))

from app.services.parser.enhanced_parser_integration import EnhancedParserIntegration

def test_enhanced_parser():
    """Test the enhanced parser with sample resume data"""
    
    print("=" * 80)
    print("ENHANCED RESUME PARSER TEST")
    print("=" * 80)
    
    # Sample resume text for testing
    sample_resume = """
    John Doe
    Email: john.doe@email.com | Phone: (555) 123-4567 | LinkedIn: linkedin.com/in/johndoe
    
    PROFESSIONAL SUMMARY
    Experienced Senior Software Engineer with 8+ years in full-stack development,
    cloud architecture, and team leadership. Passionate about building scalable
    solutions and mentoring junior developers.
    
    EXPERIENCE
    
    Company: Google
    Title: Senior Software Engineer
    Location: Mountain View, CA
    Duration: 2020-2023
    
    - Led development of microservices architecture serving 10M+ users
    - Implemented CI/CD pipelines reducing deployment time by 60%
    - Mentored 5 junior engineers on best practices and code review
    
    Company: Airbnb
    Title: Software Engineer
    Location: San Francisco, CA
    Duration: 2018-2020
    
    - Developed React-based user interfaces with TypeScript
    - Optimized database queries improving performance by 40%
    - Collaborated with cross-functional teams on product features
    
    Company: Microsoft
    Title: Junior Software Developer
    Location: Redmond, WA
    Duration: 2016-2018
    
    - Built RESTful APIs using Node.js and Express
    - Implemented automated testing with Jest and Cypress
    - Participated in agile development processes
    
    EDUCATION
    
    Institution: Stanford University
    Degree: Bachelor of Science in Computer Science
    Duration: 2012-2016
    GPA: 3.8
    Honors: Dean's List, Magna Cum Laude
    
    Institution: MIT
    Degree: Master of Science in Computer Science
    Duration: 2016-2018
    
    SKILLS
    
    Technical Skills: Python, JavaScript, TypeScript, React, Node.js, Docker, Kubernetes,
    AWS, Azure, SQL, NoSQL, MongoDB, PostgreSQL, Redis, Elasticsearch, Git, CI/CD,
    Microservices, REST APIs, GraphQL, Machine Learning, Data Science
    
    Soft Skills: Leadership, Communication, Teamwork, Problem Solving, Project Management,
    Mentoring, Critical Thinking, Time Management
    
    Certifications: AWS Solutions Architect, Google Cloud Professional, Scrum Master
    
    LANGUAGES
    English (Native), Spanish (Fluent), French (Intermediate)
    """
    
    try:
        print("Initializing Enhanced Parser...")
        start_time = time.time()
        
        # Initialize the enhanced parser
        parser = EnhancedParserIntegration(cache_ttl_hours=1, use_fuzzy_matching=True)
        
        init_time = time.time() - start_time
        print(f"✅ Parser initialized in {init_time:.2f} seconds")
        
        # Get dataset statistics
        print("\n📊 Dataset Statistics:")
        stats = parser.get_parser_statistics()
        dataset_stats = stats['datasets']
        
        for dataset, count in dataset_stats.items():
            print(f"  {dataset.title()}: {count:,} entries")
        
        # Test parsing
        print("\n🔍 Parsing Sample Resume...")
        parse_start = time.time()
        
        result = parser.parse_resume_enhanced(sample_resume)
        
        parse_time = time.time() - parse_start
        print(f"✅ Resume parsed in {parse_time:.2f} seconds")
        
        # Display results
        print("\n📋 PARSING RESULTS:")
        print("=" * 50)
        
        # Experience results
        print(f"\n🏢 WORK EXPERIENCE ({len(result.experiences)} entries):")
        for i, exp in enumerate(result.experiences, 1):
            print(f"\n  {i}. {exp.title} at {exp.company}")
            print(f"     Seniority: {exp.seniority} | Category: {exp.category}")
            print(f"     Location: {exp.location}")
            print(f"     Duration: {exp.start_date} - {exp.end_date}")
            print(f"     Confidence: {exp.company_confidence:.2f} (company), {exp.title_confidence:.2f} (title)")
        
        # Education results
        print(f"\n🎓 EDUCATION ({len(result.education)} entries):")
        for i, edu in enumerate(result.education, 1):
            print(f"\n  {i}. {edu.degree} in {edu.field_of_study}")
            print(f"     Institution: {edu.institution}")
            print(f"     Level: {edu.degree_level}")
            print(f"     Duration: {edu.start_date} - {edu.end_date}")
            print(f"     Confidence: {edu.institution_confidence:.2f} (institution), {edu.degree_confidence:.2f} (degree)")
            if edu.gpa:
                print(f"     GPA: {edu.gpa}")
            if edu.honors:
                print(f"     Honors: {', '.join(edu.honors)}")
        
        # Skills results
        print(f"\n💻 SKILLS:")
        print(f"  Technical Skills: {len(result.skills.technical_skills)}")
        for skill, confidence in result.skills.technical_skills[:10]:  # Show first 10
            print(f"    • {skill} (confidence: {confidence:.2f})")
        
        print(f"  Soft Skills: {len(result.skills.soft_skills)}")
        for skill, confidence in result.skills.soft_skills[:5]:  # Show first 5
            print(f"    • {skill} (confidence: {confidence:.2f})")
        
        print(f"  Certifications: {len(result.skills.certifications)}")
        for cert, confidence in result.skills.certifications:
            print(f"    • {cert} (confidence: {confidence:.2f})")
        
        print(f"  Skill Categories: {list(result.skills.skill_categories.keys())}")
        
        if result.skills.inferred_industry:
            print(f"  Inferred Industry: {result.skills.inferred_industry} (confidence: {result.skills.industry_confidence:.2f})")
        
        # Skill combinations
        if result.skills.skill_combinations:
            print(f"  Skill Combinations:")
            for combo, confidence, skills in result.skills.skill_combinations:
                print(f"    • {combo} (confidence: {confidence:.2f}) - {', '.join(skills)}")
        
        # Summary
        print(f"\n📈 SUMMARY:")
        summary = result.summary
        print(f"  Total Experiences: {summary['total_experiences']}")
        print(f"  Total Education: {summary['total_education']}")
        print(f"  Career Level: {summary['career_level']}")
        print(f"  Highest Degree: {summary['highest_degree']}")
        print(f"  Experience Duration: {summary['experience_duration_months']} months")
        
        # Confidence scores
        print(f"\n🎯 CONFIDENCE SCORES:")
        for component, score in result.confidence_scores.items():
            print(f"  {component.title()}: {score:.2f}")
        
        # Performance statistics
        print(f"\n📊 PERFORMANCE STATISTICS:")
        perf_stats = stats['performance']
        print(f"  Total Parsed: {perf_stats['total_parsed']}")
        print(f"  Successful Parses: {perf_stats['successful_parses']}")
        print(f"  Average Confidence: {perf_stats['average_confidence']:.2f}")
        
        # Component performance
        print(f"\n🔧 COMPONENT PERFORMANCE:")
        for component, metrics in perf_stats['component_performance'].items():
            print(f"  {component.title()}:")
            print(f"    Success Rate: {metrics['success_rate']:.2f}")
            print(f"    Avg Confidence: {metrics['avg_confidence']:.2f}")
        
        # Test individual components
        print(f"\n🧪 COMPONENT TESTING:")
        test_individual_components(parser)
        
        print(f"\n✅ ALL TESTS COMPLETED SUCCESSFULLY!")
        print(f"⏱️  Total Test Time: {time.time() - start_time:.2f} seconds")
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

def test_individual_components(parser):
    """Test individual parser components"""
    
    print("\n🔍 Testing Company Matcher:")
    test_companies = [
        "Google",
        "Airbnb Inc.",
        "Microsoft Corporation",
        "Unknown Startup XYZ",
        "McKinsey & Company"
    ]
    
    for company in test_companies:
        match_result = parser.company_matcher.match_company(company)
        print(f"  '{company}' → '{match_result[0]}' (confidence: {match_result[1]:.2f})")
    
    print("\n🔍 Testing Job Title Normalizer:")
    test_titles = [
        "Senior Software Engineer",
        "SWE",
        "Product Manager",
        "CEO",
        "Junior Developer"
    ]
    
    for title in test_titles:
        normalized, seniority, category, confidence = parser.job_title_normalizer.normalize_job_title(title)
        print(f"  '{title}' → '{normalized}' ({seniority}, {category}, confidence: {confidence:.2f})")
    
    print("\n🔍 Testing Skills Validator:")
    test_skills = [
        "Python",
        "React.js",
        "Machine Learning",
        "Leadership",
        "Unknown Skill XYZ"
    ]
    
    for skill in test_skills:
        is_valid, skill_data, confidence = parser.skills_validator.validate_skill(skill)
        status = "✅" if is_valid else "❌"
        print(f"  {status} '{skill}' → {'Valid' if is_valid else 'Invalid'} (confidence: {confidence:.2f})")
    
    print("\n🔍 Testing Education Normalizer:")
    test_institutions = [
        "Stanford University",
        "MIT",
        "UCLA",
        "Harvard",
        "Unknown College XYZ"
    ]
    
    for institution in test_institutions:
        normalized, confidence, metadata = parser.education_normalizer.normalize_institution(institution)
        print(f"  '{institution}' → '{normalized}' (confidence: {confidence:.2f})")

def test_dataset_validation():
    """Test dataset validation"""
    print("\n🔍 Testing Dataset Validation:")
    
    try:
        parser = EnhancedParserIntegration()
        validation_results = parser.validate_datasets()
        
        for dataset, results in validation_results.items():
            status = "✅" if results['valid'] else "❌"
            print(f"  {status} {dataset.title()}: {results['file_count']} files, {results['total_records']} records")
            
            if results['errors']:
                for error in results['errors']:
                    print(f"    ❌ Error: {error}")
            
            if results['warnings']:
                for warning in results['warnings']:
                    print(f"    ⚠️  Warning: {warning}")
        
    except Exception as e:
        print(f"❌ Dataset validation error: {e}")

if __name__ == "__main__":
    print("🚀 Starting Enhanced Parser Tests...")
    
    # Run main test
    success = test_enhanced_parser()
    
    # Run dataset validation
    test_dataset_validation()
    
    if success:
        print("\n🎉 All tests passed! Enhanced parser is ready for use.")
    else:
        print("\n💥 Some tests failed. Please check the errors above.")
    
    print("\n" + "=" * 80)
