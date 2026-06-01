import sys
import os
from pathlib import Path
import numpy as np
from PIL import Image

# Add directories to system path so we can import modules
sys.path.append(str(Path(__file__).resolve().parent / "ai-service"))
sys.path.append(str(Path(__file__).resolve().parent / "backend"))

from parsers.confidence_scorer import ConfidenceScorer
from matching.matching_engine import MatchingEngine
from app.services.parser.extract_text import _is_text_quality_good, _preprocess_image_for_ocr, _increase_dpi

def test_quality_score():
    print("\n--- 1. Testing Quality & Completeness Scoring ---")
    scorer = ConfidenceScorer()
    
    complete_data = {
        'name': 'Alice Smith',
        'email': 'alice@example.com',
        'phone': '123-456-7890',
        'summary': 'Senior software engineer with 10 years of experience building web applications.',
        'skills': ['Python', 'JavaScript', 'React', 'AWS', 'Docker'],
        'work_experience': [
            {'title': 'Senior Engineer', 'company': 'Tech Inc'},
            {'title': 'Software Developer', 'company': 'Startup Co'}
        ],
        'education': [{'degree': 'BS Computer Science', 'institution': 'State Univ'}],
        'certifications': ['AWS Solutions Architect']
    }
    
    incomplete_data = {
        'name': 'Bob',
        'skills': ['Python']
    }
    
    complete_res = scorer.score_parsed_resume(complete_data)
    incomplete_res = scorer.score_parsed_resume(incomplete_data)
    
    print(f"Complete Candidate Quality Score: {complete_res['quality_score']}")
    print(f"Incomplete Candidate Quality Score: {incomplete_res['quality_score']}")
    
    assert complete_res['quality_score'] > incomplete_res['quality_score']
    print("[OK] Quality score test passed!")

def test_batch_matching():
    print("\n--- 2. Testing Batch Matching & Semantic Alignment ---")
    engine = MatchingEngine()
    
    candidates = [
        {
            'id': 'cand-1',
            'name': 'Alice (Strong Python/React/Cloud)',
            'skills': ['Python', 'JS', 'ReactJS', 'AWS', 'Docker'],
            'years_of_experience': 5,
            'work_experience': [{'job_title': 'Senior Dev', 'duration_months': 60}],
            'education': [{'degree': 'Bachelor'}]
        },
        {
            'id': 'cand-2',
            'name': 'Bob (Only junior Java)',
            'skills': ['Java', 'SQL'],
            'years_of_experience': 1,
            'work_experience': [{'job_title': 'Junior Dev', 'duration_months': 12}],
            'education': [{'degree': 'Associate'}]
        }
    ]
    
    job = {
        'required_skills': ['Python', 'React', 'Amazon Web Services'],
        'preferred_skills': ['Docker'],
        'min_experience_years': 4,
        'max_experience_years': 8,
        'education_requirement': 'Bachelor'
    }
    
    results = engine.calculate_match_score_batch(candidates, job)
    
    for r in results:
        print(f"Candidate: {r.get('candidate_id')} - Score: {r['overall_score']} - Recommendation: {r['recommendation']}")
        print(f"  Reason: {r['reason']}")
        
    assert results[0]['overall_score'] > results[1]['overall_score']
    assert results[0]['recommendation'] == 'Strong Match' or results[0]['recommendation'] == 'Good Match'
    print("[OK] Batch matching test passed!")

def test_ocr_quality_checker():
    print("\n--- 3. Testing OCR Text Quality Validation ---")
    good_text = (
        "Experienced software developer. Specialized in Java, C++, and Python. "
        "Graduated from MIT with a degree in Computer Science. Over 10 years of experience "
        "working in the tech industry, building enterprise web applications, scaling services, "
        "and managing databases. Proficient in cloud platforms like AWS, GCP, and Azure."
    )
    bad_text = "lkjlkasjd laksjdlkasjd ;alksjd;laksjd qiwuoieurpoiquwpoeirupqoieu 123019823091283"
    
    good_ok = _is_text_quality_good(good_text)
    bad_ok = _is_text_quality_good(bad_text)
    
    print(f"Good text quality ok: {good_ok}")
    print(f"Garbage text quality ok: {bad_ok}")
    
    assert good_ok is True
    assert bad_ok is False
    print("[OK] OCR text quality checker test passed!")

def test_image_preprocessing():
    print("\n--- 4. Testing OpenCV/NumPy Preprocessing ---")
    # Create a simple tilted black text line on white background
    img = Image.new("RGB", (200, 100), color=(255, 255, 255))
    
    # Run through preprocessing
    processed = _preprocess_image_for_ocr(img)
    print("Image preprocessed successfully.")
    assert processed is not None
    
    # Test DPI increase
    higher_dpi = _increase_dpi(img, target=400)
    print(f"Original size: {img.size}, Resized size: {higher_dpi.size}")
    assert higher_dpi.size[0] > img.size[0]
    print("[OK] Image preprocessing and DPI resize tests passed!")

def main():
    print("=== STARTING SYSTEM FEATURE VERIFICATION ===")
    test_quality_score()
    test_batch_matching()
    test_ocr_quality_checker()
    test_image_preprocessing()
    print("\n*** ALL TESTS COMPLETED SUCCESSFULLY! ***")

if __name__ == "__main__":
    main()
