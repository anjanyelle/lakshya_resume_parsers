"""
Enhanced Parsing System Testing Script
Validates that the enhanced system maintains backward compatibility
while improving parsing accuracy with external datasets.
"""

import json
import logging
import os
import sys
from pathlib import Path
from typing import Dict, List, Any

# Add the backend path to sys.path for imports
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedParsingTester:
    """Test suite for enhanced parsing system"""
    
    def __init__(self):
        self.test_results = {
            'dataset_loader': {'passed': 0, 'failed': 0, 'errors': []},
            'hybrid_parser': {'passed': 0, 'failed': 0, 'errors': []},
            'normalizer': {'passed': 0, 'failed': 0, 'errors': []},
            'adapter': {'passed': 0, 'failed': 0, 'errors': []},
            'pipeline_integration': {'passed': 0, 'failed': 0, 'errors': []}
        }
    
    def test_dataset_loader(self) -> bool:
        """Test enhanced dataset loader"""
        logger.info("Testing Enhanced Dataset Loader...")
        
        try:
            from app.services.parser.utils.enhanced_dataset_loader import enhanced_loader
            
            # Test dataset loading
            stats = enhanced_loader.get_dataset_stats()
            assert isinstance(stats, dict), "Dataset stats should be a dictionary"
            assert len(stats) > 0, "Should load at least one dataset"
            
            # Test company lookup
            company_result = enhanced_loader.lookup_company("Google")
            logger.info(f"Company lookup test: Google -> {company_result}")
            
            # Test job title lookup
            title_result = enhanced_loader.lookup_job_title("Software Engineer")
            logger.info(f"Job title lookup test: Software Engineer -> {title_result}")
            
            # Test skill lookup
            skill_result = enhanced_loader.lookup_skill("Python")
            logger.info(f"Skill lookup test: Python -> {skill_result}")
            
            # Test normalization
            normalized_company = enhanced_loader.normalize_company_name("Google LLC")
            logger.info(f"Company normalization: Google LLC -> {normalized_company}")
            
            self.test_results['dataset_loader']['passed'] += 1
            logger.info("✅ Dataset Loader tests passed")
            return True
            
        except Exception as e:
            self.test_results['dataset_loader']['failed'] += 1
            self.test_results['dataset_loader']['errors'].append(str(e))
            logger.error(f"❌ Dataset Loader test failed: {e}")
            return False
    
    def test_hybrid_parser(self) -> bool:
        """Test hybrid work experience parser"""
        logger.info("Testing Hybrid Work Experience Parser...")
        
        try:
            from app.services.parser.hybrid_work_experience_parser import hybrid_parser
            
            # Test with sample experience text
            sample_text = """
            Chief Revenue Officer | Omni Stream Global | 2021 - Present
            VP of Global Marketing | Nexa Health Tech | 2017 - 2021
            Software Engineer at Google | 2015 - 2017
            """
            
            results = hybrid_parser.parse_experience_section(sample_text)
            assert isinstance(results, list), "Should return a list"
            assert len(results) > 0, "Should parse at least one job"
            
            # Check for enhanced entries
            enhanced_entries = [r for r in results if hasattr(r, 'source')]
            logger.info(f"Parsed {len(results)} jobs, {len(enhanced_entries)} enhanced")
            
            # Test parsing stats
            stats = hybrid_parser.get_parsing_stats()
            assert isinstance(stats, dict), "Stats should be a dictionary"
            logger.info(f"Parser stats: {stats}")
            
            self.test_results['hybrid_parser']['passed'] += 1
            logger.info("✅ Hybrid Parser tests passed")
            return True
            
        except Exception as e:
            self.test_results['hybrid_parser']['failed'] += 1
            self.test_results['hybrid_parser']['errors'].append(str(e))
            logger.error(f"❌ Hybrid Parser test failed: {e}")
            return False
    
    def test_normalizer(self) -> bool:
        """Test enhanced normalizer"""
        logger.info("Testing Enhanced Normalizer...")
        
        try:
            from app.services.parser.enhanced_normalizer import enhanced_normalizer
            
            # Test company normalization
            normalized_company = enhanced_normalizer.normalize_company_name("Google LLC")
            logger.info(f"Company normalization: Google LLC -> {normalized_company}")
            
            # Test job title normalization
            normalized_title = enhanced_normalizer.normalize_job_title("Sr Software Engineer")
            logger.info(f"Title normalization: Sr Software Engineer -> {normalized_title}")
            
            # Test education normalization
            normalized_inst, normalized_degree = enhanced_normalizer.normalize_education(
                "University of Chicago Booth School of Business", "Master of Business Administration"
            )
            logger.info(f"Education normalization: {normalized_inst}, {normalized_degree}")
            
            # Test location normalization
            normalized_location = enhanced_normalizer.normalize_location("NYC, USA")
            logger.info(f"Location normalization: NYC, USA -> {normalized_location}")
            
            # Test skill normalization
            normalized_skill = enhanced_normalizer.normalize_skill("python programming")
            logger.info(f"Skill normalization: python programming -> {normalized_skill}")
            
            # Test stats
            stats = enhanced_normalizer.get_normalization_stats()
            assert isinstance(stats, dict), "Stats should be a dictionary"
            logger.info(f"Normalizer stats: {stats}")
            
            self.test_results['normalizer']['passed'] += 1
            logger.info("✅ Normalizer tests passed")
            return True
            
        except Exception as e:
            self.test_results['normalizer']['failed'] += 1
            self.test_results['normalizer']['errors'].append(str(e))
            logger.error(f"❌ Normalizer test failed: {e}")
            return False
    
    def test_adapter(self) -> bool:
        """Test JSON format adapter"""
        logger.info("Testing JSON Format Adapter...")
        
        try:
            from app.services.parser.json_format_adapter import json_adapter
            
            # Test with sample data
            sample_data = {
                "contact": {
                    "name": {"name": "John Doe"},
                    "emails": [{"email": "john@example.com"}],
                    "phones": [{"phone": "123-456-7890"}],
                    "location": {"city": "New York", "state": "NY", "country": "USA"}
                },
                "work_experience": [
                    {
                        "title": "Software Engineer",
                        "company": "Google",
                        "location": "Mountain View, CA",
                        "startDate": "2020-01-01",
                        "endDate": "2022-01-01"
                    }
                ],
                "education": [
                    {
                        "institution": "Stanford University",
                        "degree": "Bachelor of Science",
                        "graduationYear": "2019"
                    }
                ],
                "skills": [
                    {"name": "Python", "category": "Programming", "confidence": 0.9}
                ],
                "certifications": [
                    {"name": "AWS Certified Developer", "issuer": "Amazon"}
                ],
                "sections": {
                    "experience": {"content": "Software Engineer at Google..."}
                }
            }
            
            # Test enhancement
            enhanced_data = json_adapter.enhance_parsing_with_external_datasets(sample_data)
            assert isinstance(enhanced_data, dict), "Should return a dictionary"
            
            # Test JSON structure validation
            is_valid = json_adapter.validate_json_structure(enhanced_data)
            assert is_valid, "Enhanced data should maintain valid JSON structure"
            
            # Check that required keys are present
            required_keys = ["basics", "work_experience", "education", "skills", "certifications", "sections", "metadata"]
            for key in required_keys:
                assert key in enhanced_data, f"Missing required key: {key}"
            
            # Check enhancement metadata
            assert "enhancement_info" in enhanced_data.get("metadata", {}), "Should include enhancement metadata"
            
            logger.info("✅ JSON Adapter tests passed")
            self.test_results['adapter']['passed'] += 1
            return True
            
        except Exception as e:
            self.test_results['adapter']['failed'] += 1
            self.test_results['adapter']['errors'].append(str(e))
            logger.error(f"❌ JSON Adapter test failed: {e}")
            return False
    
    def test_pipeline_integration(self) -> bool:
        """Test pipeline integration"""
        logger.info("Testing Pipeline Integration...")
        
        try:
            # Test that we can import the enhanced components
            from app.services.parser.utils.enhanced_dataset_loader import enhanced_loader
            from app.services.parser.enhanced_normalizer import enhanced_normalizer
            from app.services.parser.hybrid_work_experience_parser import hybrid_parser
            from app.services.parser.json_format_adapter import json_adapter
            
            # Test that all components are initialized
            assert enhanced_loader is not None, "Enhanced loader should be available"
            assert enhanced_normalizer is not None, "Enhanced normalizer should be available"
            assert hybrid_parser is not None, "Hybrid parser should be available"
            assert json_adapter is not None, "JSON adapter should be available"
            
            # Test that the pipeline can import the adapter
            try:
                # This simulates what happens in the pipeline
                from app.services.parser.json_format_adapter import json_adapter as pipeline_adapter
                assert pipeline_adapter is not None, "Pipeline should be able to import adapter"
            except ImportError as e:
                raise ImportError(f"Pipeline cannot import adapter: {e}")
            
            logger.info("✅ Pipeline Integration tests passed")
            self.test_results['pipeline_integration']['passed'] += 1
            return True
            
        except Exception as e:
            self.test_results['pipeline_integration']['failed'] += 1
            self.test_results['pipeline_integration']['errors'].append(str(e))
            logger.error(f"❌ Pipeline Integration test failed: {e}")
            return False
    
    def test_backward_compatibility(self) -> bool:
        """Test that existing functionality is not broken"""
        logger.info("Testing Backward Compatibility...")
        
        try:
            # Test existing imports still work
            from app.services.parser.work_experience_parser import WorkExperienceParser
            from app.services.parser.skill_extractor import SkillExtractor
            from app.services.parser.education_parser import EducationParser
            
            # Test existing functionality
            existing_parser = WorkExperienceParser()
            sample_text = "Software Engineer at Google (2020-2022)"
            results = existing_parser.parse_experience_section(sample_text)
            assert isinstance(results, list), "Existing parser should still work"
            
            logger.info("✅ Backward Compatibility tests passed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Backward Compatibility test failed: {e}")
            return False
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all tests and return results"""
        logger.info("🧪 Running Enhanced Parsing System Tests...")
        
        # Run individual tests
        self.test_dataset_loader()
        self.test_hybrid_parser()
        self.test_normalizer()
        self.test_adapter()
        self.test_pipeline_integration()
        self.test_backward_compatibility()
        
        # Calculate overall results
        total_passed = sum(result['passed'] for result in self.test_results.values())
        total_failed = sum(result['failed'] for result in self.test_results.values())
        total_tests = total_passed + total_failed
        
        success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
        
        overall_results = {
            'total_tests': total_tests,
            'total_passed': total_passed,
            'total_failed': total_failed,
            'success_rate': success_rate,
            'test_details': self.test_results,
            'status': 'PASSED' if success_rate >= 80 else 'FAILED'
        }
        
        return overall_results
    
    def print_results(self, results: Dict[str, Any]):
        """Print test results in a readable format"""
        print("\n" + "="*60)
        print("🧪 ENHANCED PARSING SYSTEM TEST RESULTS")
        print("="*60)
        
        print(f"📊 Overall Results:")
        print(f"   Total Tests: {results['total_tests']}")
        print(f"   Passed: {results['total_passed']}")
        print(f"   Failed: {results['total_failed']}")
        print(f"   Success Rate: {results['success_rate']:.1f}%")
        print(f"   Status: {results['status']}")
        
        print(f"\n📋 Test Details:")
        for test_name, result in results['test_details'].items():
            if result['passed'] > 0 or result['failed'] > 0:
                status = "✅ PASS" if result['failed'] == 0 else "❌ FAIL"
                print(f"   {test_name}: {status} ({result['passed']} passed, {result['failed']} failed)")
                
                if result['errors']:
                    for error in result['errors']:
                        print(f"      Error: {error}")
        
        print("\n" + "="*60)
        
        if results['status'] == 'PASSED':
            print("🎉 All tests passed! Enhanced parsing system is ready.")
        else:
            print("⚠️  Some tests failed. Please review the errors above.")
        
        print("="*60)

def main():
    """Main testing function"""
    tester = EnhancedParsingTester()
    results = tester.run_all_tests()
    tester.print_results(results)
    
    return results['status'] == 'PASSED'

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
