#!/usr/bin/env python3
"""
Demo script showing how the production pipeline processes a full resume:
1. Section Extraction (EXPERIENCE & EDUCATION only)
2. Model Inference (only on extracted sections)
3. Results Display
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from resume_parser_pipeline import SectionExtractor, ModelInference, PostProcessor
import json


def print_box(title, content="", width=80):
    """Print content in a box"""
    print("╔" + "═" * (width - 2) + "╗")
    print(f"║ {title:<{width-4}} ║")
    print("╠" + "═" * (width - 2) + "╣")
    if content:
        for line in content.split('\n'):
            if line:
                print(f"║ {line:<{width-4}} ║")
    print("╚" + "═" * (width - 2) + "╝")


def print_step(step_num, title):
    """Print step header"""
    print(f"\n{'='*80}")
    print(f"STEP {step_num}: {title}")
    print(f"{'='*80}\n")


def demo_pipeline(resume_text):
    """Demonstrate the full pipeline process"""
    
    print("\n" + "="*80)
    print("🚀 PRODUCTION PIPELINE DEMONSTRATION")
    print("="*80)
    print(f"\n📄 Full Resume Length: {len(resume_text)} characters")
    print(f"📝 Word Count: {len(resume_text.split())} words")
    
    # STEP 1: Section Extraction
    print_step(1, "SMART SECTION EXTRACTION")
    print("🔍 Detecting EXPERIENCE and EDUCATION sections...")
    print("⚠️  Ignoring: Skills, Summary, Projects, Certifications\n")
    
    sections = SectionExtractor.extract_sections(resume_text)
    
    exp_text = sections.get('experience', '')
    edu_text = sections.get('education', '')
    
    print(f"✅ EXPERIENCE Section: {len(exp_text)} characters")
    if exp_text:
        print("─" * 80)
        print(exp_text[:500] + ("..." if len(exp_text) > 500 else ""))
        print("─" * 80)
    else:
        print("❌ No EXPERIENCE section found")
    
    print(f"\n✅ EDUCATION Section: {len(edu_text)} characters")
    if edu_text:
        print("─" * 80)
        print(edu_text[:300] + ("..." if len(edu_text) > 300 else ""))
        print("─" * 80)
    else:
        print("❌ No EDUCATION section found")
    
    # STEP 2: Check if sections found
    if not exp_text and not edu_text:
        print_step(2, "FALLBACK TO CHUNKING")
        print("⚠️  No sections detected - would use chunking fallback")
        print("📦 Chunking strategy: 400-450 tokens with 50 token overlap")
        print("🔍 Filter: Only chunks with experience/education keywords")
        return
    
    # STEP 3: Model Inference
    print_step(2, "MODEL INFERENCE (DeBERTa)")
    print("🤖 Loading DeBERTa model...")
    
    model_path = "./models/resume-ner-deberta"
    model = ModelInference(model_path)
    
    print(f"✅ Model loaded: {model_path}")
    print(f"🎯 Token Limit: 512 tokens per section\n")
    
    all_entities = []
    
    # Process EXPERIENCE section
    if exp_text:
        print("─" * 80)
        print("📊 Processing EXPERIENCE section...")
        print("─" * 80)
        exp_entities = model.extract_entities(exp_text)
        all_entities.extend(exp_entities)
        
        print(f"\n🔍 Extracted {len(exp_entities)} entities from EXPERIENCE:")
        for entity in exp_entities[:10]:  # Show first 10
            print(f"   • {entity['label']:<15} → {entity['text']}")
        if len(exp_entities) > 10:
            print(f"   ... and {len(exp_entities) - 10} more")
    
    # Process EDUCATION section
    if edu_text:
        print("\n" + "─" * 80)
        print("🎓 Processing EDUCATION section...")
        print("─" * 80)
        edu_entities = model.extract_entities(edu_text)
        all_entities.extend(edu_entities)
        
        print(f"\n🔍 Extracted {len(edu_entities)} entities from EDUCATION:")
        for entity in edu_entities[:10]:
            print(f"   • {entity['label']:<15} → {entity['text']}")
        if len(edu_entities) > 10:
            print(f"   ... and {len(edu_entities) - 10} more")
    
    # STEP 4: Post-Processing
    print_step(3, "POST-PROCESSING")
    print("🧹 Cleaning entities...")
    print("   • Removing person names from COMPANY")
    print("   • Removing skills from DEGREE\n")
    
    cleaned_entities = PostProcessor.clean_entities(all_entities)
    
    removed_count = len(all_entities) - len(cleaned_entities)
    print(f"✅ Removed {removed_count} invalid entities")
    print(f"✅ Final entity count: {len(cleaned_entities)}\n")
    
    # STEP 5: Structured Output
    print_step(4, "STRUCTURED OUTPUT")
    
    # Group entities by type
    companies = [e['text'] for e in cleaned_entities if e['label'] == 'COMPANY']
    roles = [e['text'] for e in cleaned_entities if e['label'] == 'ROLE']
    locations = [e['text'] for e in cleaned_entities if e['label'] == 'LOCATION']
    start_dates = [e['text'] for e in cleaned_entities if e['label'] == 'START_DATE']
    end_dates = [e['text'] for e in cleaned_entities if e['label'] == 'END_DATE']
    degrees = [e['text'] for e in cleaned_entities if e['label'] == 'DEGREE']
    institutions = [e['text'] for e in cleaned_entities if e['label'] == 'EDUCATION']
    
    # Build experience entries
    print("🏢 WORK EXPERIENCE:")
    print("─" * 80)
    
    max_exp = max(len(companies), len(roles)) if companies or roles else 0
    
    if max_exp == 0:
        print("❌ No work experience found\n")
    else:
        for i in range(max_exp):
            print(f"\n📌 Experience #{i+1}:")
            print(f"   Company:      {companies[i] if i < len(companies) else 'N/A'}")
            print(f"   Role:         {roles[i] if i < len(roles) else 'N/A'}")
            print(f"   Location:     {locations[i] if i < len(locations) else 'N/A'}")
            print(f"   Start Date:   {start_dates[i] if i < len(start_dates) else 'N/A'}")
            print(f"   End Date:     {end_dates[i] if i < len(end_dates) else 'N/A'}")
    
    # Build education entries
    print("\n" + "─" * 80)
    print("🎓 EDUCATION:")
    print("─" * 80)
    
    max_edu = max(len(degrees), len(institutions)) if degrees or institutions else 0
    
    if max_edu == 0:
        print("❌ No education found\n")
    else:
        for i in range(max_edu):
            print(f"\n📌 Education #{i+1}:")
            print(f"   Degree:       {degrees[i] if i < len(degrees) else 'N/A'}")
            print(f"   Institution:  {institutions[i] if i < len(institutions) else 'N/A'}")
    
    # Summary
    print("\n" + "="*80)
    print("📊 PIPELINE SUMMARY")
    print("="*80)
    print(f"✅ Full Resume: {len(resume_text)} chars → Sections: {len(exp_text) + len(edu_text)} chars")
    print(f"✅ Token Savings: {((len(resume_text) - (len(exp_text) + len(edu_text))) / len(resume_text) * 100):.1f}% reduction")
    print(f"✅ Entities Extracted: {len(all_entities)} → Cleaned: {len(cleaned_entities)}")
    print(f"✅ Work Experience: {max_exp} entries")
    print(f"✅ Education: {max_edu} entries")
    print("="*80 + "\n")


if __name__ == "__main__":
    print("\n" * 2)
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 20 + "🚀 PRODUCTION PIPELINE DEMO" + " " * 30 + "║")
    print("╚" + "═" * 78 + "╝")
    print("\n📝 Paste your FULL RESUME text below.")
    print("When done, press Enter, then type 'END' and press Enter again.\n")
    print("─" * 80)
    
    lines = []
    while True:
        try:
            line = input()
            if line.strip().upper() == 'END':
                break
            lines.append(line)
        except EOFError:
            break
    
    resume_text = '\n'.join(lines)
    
    if resume_text.strip():
        demo_pipeline(resume_text)
    else:
        print("\n❌ No resume text provided!")
