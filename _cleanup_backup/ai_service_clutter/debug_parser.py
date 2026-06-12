#!/usr/bin/env python3
"""
Debug script to analyze why AI parsing has low accuracy.
Tests each step of the pipeline individually.
"""

import json
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from parsers.text_extractor import TextExtractor
from parsers.rule_parser import RuleBasedParser
from parsers.ai_ner_parser import AINamedEntityParser
from parsers.section_splitter import SectionSplitter
from parsers.experience_extractor import ExperienceExtractor
from parsers.education_extractor import EducationExtractor
from parsers.hybrid_merger import HybridMerger
from parsers.confidence_scorer import ConfidenceScorer

def debug_parsing(file_path: str):
    """Debug the parsing pipeline step by step."""
    
    print(f"\n🔍 DEBUGGING PARSING FOR: {file_path}")
    print("=" * 80)
    
    # Initialize all parsers
    print("\n1️⃣ Initializing parsers...")
    try:
        text_extractor = TextExtractor()
        print("✅ TextExtractor initialized")
    except Exception as e:
        print(f"❌ TextExtractor failed: {e}")
        return
    
    try:
        rule_parser = RuleBasedParser()
        print("✅ RuleBasedParser initialized")
    except Exception as e:
        print(f"❌ RuleBasedParser failed: {e}")
        return
    
    try:
        ai_parser = AINamedEntityParser()
        print("✅ AINamedEntityParser initialized")
    except Exception as e:
        print(f"❌ AINamedEntityParser failed: {e}")
        return
    
    try:
        section_splitter = SectionSplitter()
        print("✅ SectionSplitter initialized")
    except Exception as e:
        print(f"❌ SectionSplitter failed: {e}")
        return
    
    try:
        experience_extractor = ExperienceExtractor()
        print("✅ ExperienceExtractor initialized")
    except Exception as e:
        print(f"❌ ExperienceExtractor failed: {e}")
        return
    
    try:
        education_extractor = EducationExtractor()
        print("✅ EducationExtractor initialized")
    except Exception as e:
        print(f"❌ EducationExtractor failed: {e}")
        return
    
    try:
        hybrid_merger = HybridMerger()
        print("✅ HybridMerger initialized")
    except Exception as e:
        print(f"❌ HybridMerger failed: {e}")
        return
    
    try:
        confidence_scorer = ConfidenceScorer()
        print("✅ ConfidenceScorer initialized")
    except Exception as e:
        print(f"❌ ConfidenceScorer failed: {e}")
        return
    
    # Step 1: Text extraction
    print("\n2️⃣ Extracting text from file...")
    try:
        text_result = text_extractor.extract(file_path)
        text = text_result.get('text', '')
        print(f"✅ Text extracted: {len(text)} characters")
        print(f"   Method: {text_result.get('method', 'unknown')}")
        print(f"   Quality score: {text_result.get('quality_score', 0):.2f}")
        
        # Show first 200 characters
        print(f"\n   Text preview (first 200 chars):")
        print(f"   {text[:200]}...")
        
        # Count lines and words
        lines = text.split('\n')
        words = text.split()
        print(f"   Lines: {len(lines)}, Words: {len(words)}")
        
    except Exception as e:
        print(f"❌ Text extraction failed: {e}")
        return
    
    # Step 2: Rule-based parsing
    print("\n3️⃣ Rule-based parsing...")
    try:
        rule_result = {
            'email': rule_parser.extract_email(text),
            'phone': rule_parser.extract_phone(text),
            'linkedin': rule_parser.extract_linkedin(text),
            'github': rule_parser.extract_github(text),
            'websites': rule_parser.extract_websites(text),
            'dates': rule_parser.extract_dates(text),
            'years_of_experience': rule_parser.extract_years_of_experience(text)
        }
        print("✅ Rule-based parsing completed")
        for field, value in rule_result.items():
            if value:
                print(f"   {field}: {value}")
            else:
                print(f"   {field}: ❌ NOT FOUND")
    except Exception as e:
        print(f"❌ Rule-based parsing failed: {e}")
        rule_result = {}
    
    # Step 3: AI NER parsing
    print("\n4️⃣ AI NER parsing...")
    try:
        ai_entities = ai_parser.extract_entities(text)
        print("✅ AI NER parsing completed")
        
        ai_result = {
            'name': ai_parser.get_top_person(ai_entities),
            'companies': ai_parser.get_organizations(ai_entities),
            'locations': ai_parser.get_locations(ai_entities),
            'skills': ai_parser.get_skills(ai_entities),
            'misc': ai_parser.get_misc_entities(ai_entities),
            'ai_entities': ai_entities  # Include raw entities for debugging
        }
        
        for field, value in ai_result.items():
            if field == 'ai_entities':
                continue
            if value:
                if isinstance(value, list):
                    print(f"   {field}: {len(value)} items")
                    for item in value[:5]:  # Show first 5
                        print(f"     - {item}")
                else:
                    print(f"   {field}: {value}")
            else:
                print(f"   {field}: ❌ NOT FOUND")
    except Exception as e:
        print(f"❌ AI NER parsing failed: {e}")
        ai_result = {}
    
    # Step 4: Section splitting
    print("\n5️⃣ Section splitting...")
    try:
        sections = section_splitter.split_sections(text)
        print("✅ Section splitting completed")
        for section, content in sections.items():
            if content:
                print(f"   {section}: {len(content)} chars")
    except Exception as e:
        print(f"❌ Section splitting failed: {e}")
        sections = {}
    
    # Step 5: Experience extraction
    print("\n6️⃣ Experience extraction...")
    try:
        work_experience = experience_extractor.extract_work_experience(text, sections)
        print(f"✅ Experience extraction completed: {len(work_experience)} positions")
        for i, exp in enumerate(work_experience[:3]):  # Show first 3
            print(f"   Position {i+1}:")
            print(f"     Title: {exp.get('title', 'N/A')}")
            print(f"     Company: {exp.get('company', 'N/A')}")
            print(f"     Duration: {exp.get('duration', 'N/A')}")
    except Exception as e:
        print(f"❌ Experience extraction failed: {e}")
        work_experience = []
    
    # Step 6: Education extraction
    print("\n7️⃣ Education extraction...")
    try:
        education = education_extractor.extract_education(text, sections)
        print(f"✅ Education extraction completed: {len(education)} entries")
        for i, edu in enumerate(education[:3]):  # Show first 3
            print(f"   Education {i+1}:")
            print(f"     Degree: {edu.get('degree', 'N/A')}")
            print(f"     Institution: {edu.get('institution', 'N/A')}")
            print(f"     Year: {edu.get('year', 'N/A')}")
    except Exception as e:
        print(f"❌ Education extraction failed: {e}")
        education = []
    
    # Step 7: Combine AI results
    ai_result['work_experience'] = work_experience
    ai_result['education'] = education
    
    # Step 8: Hybrid merging
    print("\n8️⃣ Hybrid merging...")
    try:
        merged_result = hybrid_merger.merge_results(rule_result, ai_result)
        print("✅ Hybrid merging completed")
        
        # Show key merged fields
        key_fields = ['name', 'email', 'phone', 'skills', 'work_experience', 'education']
        for field in key_fields:
            value = merged_result.get(field)
            if value:
                if isinstance(value, list):
                    print(f"   {field}: {len(value)} items")
                else:
                    print(f"   {field}: {value}")
            else:
                print(f"   {field}: ❌ NOT FOUND")
    except Exception as e:
        print(f"❌ Hybrid merging failed: {e}")
        merged_result = {}
    
    # Step 9: Confidence scoring
    print("\n9️⃣ Confidence scoring...")
    try:
        confidence = confidence_scorer.score_parsed_resume(merged_result)
        print("✅ Confidence scoring completed")
        print(f"   Overall score: {confidence['overall']:.3f} ({confidence['quality_level']})")
        print(f"   Needs review: {confidence['needs_review']}")
        print(f"   Missing critical: {confidence['missing_critical']}")
        
        print("\n   Field scores:")
        for field, score in confidence['fields'].items():
            print(f"     {field}: {score:.3f}")
        
        if confidence['recommendations']:
            print("\n   Recommendations:")
            for rec in confidence['recommendations']:
                print(f"     - {rec}")
    except Exception as e:
        print(f"❌ Confidence scoring failed: {e}")
        confidence = {}
    
    # Save detailed results to file
    debug_output = {
        'file_path': file_path,
        'text_extraction': {
            'text_length': len(text),
            'method': text_result.get('method'),
            'quality_score': text_result.get('quality_score'),
            'text_preview': text[:500]
        },
        'rule_result': rule_result,
        'ai_entities': ai_entities,
        'ai_result': {k: v for k, v in ai_result.items() if k != 'ai_entities'},
        'sections': {k: len(v) for k, v in sections.items()},
        'merged_result': merged_result,
        'confidence': confidence
    }
    
    output_file = file_path.replace('.', '_debug_output.') + '.json'
    with open(output_file, 'w') as f:
        json.dump(debug_output, f, indent=2, default=str)
    
    print(f"\n💾 Detailed debug output saved to: {output_file}")
    print("\n🎯 SUMMARY:")
    print(f"   Text extracted: {len(text)} chars")
    print(f"   Rule-based fields found: {sum(1 for v in rule_result.values() if v)}")
    print(f"   AI entities found: {sum(len(v) for v in ai_entities.values())}")
    print(f"   Work experience: {len(work_experience)} positions")
    print(f"   Education: {len(education)} entries")
    print(f"   Overall confidence: {confidence.get('overall', 0):.3f}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python debug_parser.py <resume_file_path>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        sys.exit(1)
    
    debug_parsing(file_path)
