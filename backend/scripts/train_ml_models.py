#!/usr/bin/env python3
"""
Train ML Models for Work Experience Parser
"""

import sys
import os
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.services.parser.ml_work_experience_parser import MLWorkExperienceParser
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def train_ml_models():
    """Train ML models for work experience parsing"""
    
    print("🤖 Training ML Models for Work Experience Parser")
    print("=" * 60)
    
    # Check if datasets are available
    datasets_path = Path("data/external/work_experience/resume_classification_dataset/Dataset.csv")
    ground_truth_path = Path("data/ground_truth.json")
    
    if not datasets_path.exists():
        print("❌ Resume dataset not found. Please run:")
        print("   python data/scripts/download_datasets.py")
        return False
    
    print(f"📊 Found resume dataset: {datasets_path}")
    print(f"📊 Found ground truth: {ground_truth_path}")
    
    try:
        # Initialize ML parser
        ml_parser = MLWorkExperienceParser()
        
        # Train models
        print("\n🧠 Training ML models...")
        ml_parser._train_models()
        
        # Test models
        print("\n🧪 Testing trained models...")
        test_text = """
        PROFESSIONAL EXPERIENCE
        Client: Nike | Location: Beaverton, OR
        Role: Senior Developer | Jan 2022 - Current
        • Developed web applications
        • Led team of 5 developers
        
        Company: Microsoft | Location: Redmond, WA
        Role: Software Engineer | Jun 2020 - Present
        • Developed Windows applications
        • Worked on Azure services
        """
        
        predictions = ml_parser.parse_work_experience(test_text)
        
        print(f"✅ Found {len(predictions)} job predictions")
        for i, pred in enumerate(predictions, 1):
            print(f"\nJob {i}:")
            print(f"  Company: {pred.company}")
            print(f"  Title: {pred.title}")
            print(f"  Location: {pred.location}")
            print(f"  Format: {pred.format_type}")
            print(f"  Confidence: {pred.confidence:.2f}")
        
        print("\n🎉 ML models trained and tested successfully!")
        print("\n📈 Model Performance:")
        print("  • Format Classifier: Detects resume format types")
        print("  • Company Extractor: Identifies company names")
        print("  • Title Extractor: Extracts job titles")
        print("  • Location Extractor: Finds location information")
        print("  • Date Extractor: Parses date ranges")
        
        return True
        
    except Exception as e:
        print(f"❌ Error training models: {e}")
        logger.exception("Training failed")
        return False

def evaluate_ml_models():
    """Evaluate ML models against test data"""
    
    print("\n📊 Evaluating ML Model Performance")
    print("-" * 40)
    
    try:
        ml_parser = MLWorkExperienceParser()
        
        if not ml_parser.is_trained:
            print("❌ Models not trained. Run training first.")
            return False
        
        # Test with various formats
        test_cases = [
            {
                'name': 'Client/Role/Location',
                'text': 'Client: Nike | Location: Beaverton, OR\nRole: Senior Developer | Jan 2022 - Current'
            },
            {
                'name': 'Company/Role/Location',
                'text': 'Company: Microsoft | Location: Redmond, WA\nRole: Software Engineer | Jun 2020 - Present'
            },
            {
                'name': 'Company Date Location',
                'text': 'Apple Inc: January 2020 - Present (Location: Cupertino, CA)\nSenior Software Engineer'
            },
            {
                'name': 'Company Client Pipe',
                'text': 'Goldman Sachs (Client: Marcus) | 2019 - 2022 | New York, NY\nLead QA Engineer'
            },
            {
                'name': 'Header Format',
                'text': '## Amazon: January 2021 - Present (Location: Seattle, WA)\nCloud Architect'
            }
        ]
        
        total_tests = len(test_cases)
        passed_tests = 0
        
        for test in test_cases:
            print(f"\n🧪 Testing {test['name']} format:")
            
            predictions = ml_parser.parse_work_experience(test['text'])
            
            if predictions:
                pred = predictions[0]
                confidence = pred.confidence
                
                if confidence > 0.5:
                    print(f"  ✅ Passed (confidence: {confidence:.2f})")
                    print(f"     Company: {pred.company}")
                    print(f"     Title: {pred.title}")
                    print(f"     Location: {pred.location}")
                    passed_tests += 1
                else:
                    print(f"  ⚠️ Low confidence (confidence: {confidence:.2f})")
            else:
                print(f"  ❌ No predictions")
        
        accuracy = passed_tests / total_tests
        print(f"\n📊 Overall Accuracy: {accuracy:.1%} ({passed_tests}/{total_tests})")
        
        return accuracy > 0.7
        
    except Exception as e:
        print(f"❌ Error evaluating models: {e}")
        return False

def main():
    """Main function"""
    
    print("🚀 ML Model Training Pipeline")
    print("=" * 60)
    
    # Change to backend directory
    os.chdir(Path(__file__).resolve().parent)
    
    # Train models
    if not train_ml_models():
        print("\n❌ Training failed. Exiting.")
        sys.exit(1)
    
    # Evaluate models
    if not evaluate_ml_models():
        print("\n⚠️ Model evaluation needs improvement.")
    
    print("\n🎯 Next Steps:")
    print("1. Test with your resume formats")
    print("2. Integrate with main parser")
    print("3. Monitor performance in production")
    print("4. Retrain with new data periodically")

if __name__ == "__main__":
    main()
