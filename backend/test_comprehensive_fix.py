"""
Comprehensive Test Suite - Validates All Fixes
Tests the complete enhanced parsing system for accuracy and compliance
"""

import json
import logging
import sys
from pathlib import Path
from typing import Dict, List, Any

# Add the backend path to sys.path for imports
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ComprehensiveTestSuite:
    """Comprehensive test suite for all parsing fixes"""
    
    def __init__(self):
        self.test_results = {
            'work_experience': {'passed': 0, 'failed': 0, 'errors': []},
            'skills': {'passed': 0, 'failed': 0, 'errors': []},
            'education': {'passed': 0, 'failed': 0, 'errors': []},
            'certifications': {'passed': 0, 'failed': 0, 'errors': []},
            'comprehensive_fix': {'passed': 0, 'failed': 0, 'errors': []},
            'json_structure': {'passed': 0, 'failed': 0, 'errors': []}
        }
    
    def test_work_experience_fix(self) -> bool:
        """Test work experience parsing fixes"""
        logger.info("Testing Work Experience Fix")
        
        try:
            from app.services.parser.enhanced_work_experience_parser import enhanced_work_parser
            
            # Test multiple job formats
            test_cases = [
                # Pipe-separated format
                """Senior Software Engineer | Google | 2020 - Present
                Led development of cloud infrastructure
                Managed team of 5 engineers
                
                Software Engineer | Microsoft | 2018 - 2020
                Developed enterprise applications
                Worked with Azure cloud services""",
                
                # Title at Company format
                """Product Manager at Amazon (2017 - 2019)
                Launched new product lines
                Increased revenue by 30%
                
                Business Analyst at Oracle (2015 - 2017)
                Analyzed business requirements
                Created detailed specifications""",
                
                # Company - Title format
                """Netflix - Data Scientist - 2019 - Present
                Built machine learning models
                Improved recommendation accuracy
                
                Uber - Software Engineer - 2018 - 2019
                Developed mobile applications
                Implemented real-time features"""
            ]
            
            for i, test_text in enumerate(test_cases):
                jobs = enhanced_work_parser.parse_experience_section(test_text)
                standard_jobs = enhanced_work_parser.convert_to_standard_format(jobs)
                
                # Validate each job
                for job in standard_jobs:
                    assert job.get('jobTitle'), f"Job {i+1}: Missing jobTitle"
                    assert job.get('company'), f"Job {i+1}: Missing company"
                    assert not job.get('jobTitle') or job.get('jobTitle') != "", f"Job {i+1}: Empty jobTitle"
                    assert not job.get('company') or job.get('company') != "", f"Job {i+1}: Empty company"
                
                logger.info(f"Test case {i+1}: Parsed {len(standard_jobs)} jobs successfully")
            
            self.test_results['work_experience']['passed'] += 1
            logger.info("✅ Work Experience Fix tests passed")
            return True
            
        except Exception as e:
            self.test_results['work_experience']['failed'] += 1
            self.test_results['work_experience']['errors'].append(str(e))
            logger.error(f"❌ Work Experience Fix test failed: {e}")
            return False
    
    def test_skills_fix(self) -> bool:
        """Test skills parsing fixes"""
        logger.info("Testing Skills Fix")
        
        try:
            from app.services.parser.enhanced_skills_parser import enhanced_skills_parser
            
            # Test with noise and valid skills
            test_cases = [
                # Mixed valid skills and noise
                "Python, Java, JavaScript, TECHNOLOGIES REFERENCE, React, Angular, CONFERENCES",
                
                # Only valid skills
                "Machine Learning, Data Science, AWS, Docker, Kubernetes, SQL, NoSQL",
                
                # Mostly noise with some valid skills
                "PROJECTS, Python, RESPONSIBILITIES, React, ACHIEVEMENTS, Node.js, ENVIRONMENT"
            ]
            
            for i, test_text in enumerate(test_cases):
                skills = enhanced_skills_parser.parse_skills_section(test_text)
                standard_skills = enhanced_skills_parser.convert_to_standard_format(skills)
                
                # Validate skills
                for skill in standard_skills:
                    assert skill.get('name'), f"Test case {i+1}: Missing skill name"
                    assert len(skill.get('name', '')) >= 3, f"Test case {i+1}: Skill name too short"
                    assert not self._is_noise_skill(skill.get('name', '')), f"Test case {i+1}: Contains noise skill: {skill.get('name')}"
                
                logger.info(f"Test case {i+1}: Extracted {len(standard_skills)} valid skills")
            
            self.test_results['skills']['passed'] += 1
            logger.info("✅ Skills Fix tests passed")
            return True
            
        except Exception as e:
            self.test_results['skills']['failed'] += 1
            self.test_results['skills']['errors'].append(str(e))
            logger.error(f"❌ Skills Fix test failed: {e}")
            return False
    
    def _is_noise_skill(self, skill_name: str) -> bool:
        """Check if skill name is noise"""
        noise_phrases = [
            'technologies reference', 'conferences', 'projects', 'responsibilities',
            'achievements', 'environment', 'tools', 'frameworks', 'languages'
        ]
        skill_lower = skill_name.lower()
        return any(phrase in skill_lower for phrase in noise_phrases)
    
    def test_education_fix(self) -> bool:
        """Test education parsing fixes"""
        logger.info("Testing Education Fix")
        
        try:
            from app.services.parser.enhanced_education_parser import enhanced_education_parser
            
            # Test various education formats
            test_cases = [
                # Degree in Field at Institution (Year)
                """Bachelor of Science in Computer Science at Stanford University (2020)
                GPA: 3.8
                
                Master of Business Administration at Harvard Business School (2022)
                GPA: 3.9""",
                
                # Institution - Degree format
                """MIT - Master of Science in Data Science (2021)
                GPA: 3.7
                
                Stanford - Bachelor of Science in Engineering (2019)
                GPA: 3.6""",
                
                # Mixed format
                """University of California, Berkeley
                Bachelor of Arts in Economics
                Graduated: 2018
                GPA: 3.5"""
            ]
            
            for i, test_text in enumerate(test_cases):
                education = enhanced_education_parser.parse_education_section(test_text)
                standard_education = enhanced_education_parser.convert_to_standard_format(education)
                
                # Validate education entries
                for edu in standard_education:
                    assert edu.get('institution') or edu.get('degree'), f"Test case {i+1}: Missing institution or degree"
                
                logger.info(f"Test case {i+1}: Parsed {len(standard_education)} education entries")
            
            self.test_results['education']['passed'] += 1
            logger.info("✅ Education Fix tests passed")
            return True
            
        except Exception as e:
            self.test_results['education']['failed'] += 1
            self.test_results['education']['errors'].append(str(e))
            logger.error(f"❌ Education Fix test failed: {e}")
            return False
    
    def test_certifications_fix(self) -> bool:
        """Test certifications parsing fixes"""
        logger.info("Testing Certifications Fix")
        
        try:
            from app.services.parser.enhanced_certifications_parser import enhanced_certifications_parser
            
            # Test with valid and invalid certifications
            test_cases = [
                # Valid certifications
                "AWS Certified Solutions Architect, Microsoft Azure Certified, PMP",
                
                # Mixed valid and invalid
                "AWS Certified Developer, This is a long sentence that should be filtered, Google Cloud Certified",
                
                # Only invalid
                "This is not a certification, Another invalid entry, PROJECT WORK"
            ]
            
            for i, test_text in enumerate(test_cases):
                certs = enhanced_certifications_parser.parse_certifications_section(test_text)
                standard_certs = enhanced_certifications_parser.convert_to_standard_format(certs)
                
                # Validate certifications
                for cert in standard_certs:
                    assert cert.get('name'), f"Test case {i+1}: Missing certification name"
                    assert len(cert.get('name', '')) <= 50, f"Test case {i+1}: Certification name too long: {cert.get('name')}"
                    assert not self._is_invalid_certification(cert.get('name', '')), f"Test case {i+1}: Contains invalid certification: {cert.get('name')}"
                
                logger.info(f"Test case {i+1}: Extracted {len(standard_certs)} valid certifications")
            
            self.test_results['certifications']['passed'] += 1
            logger.info("✅ Certifications Fix tests passed")
            return True
            
        except Exception as e:
            self.test_results['certifications']['failed'] += 1
            self.test_results['certifications']['errors'].append(str(e))
            logger.error(f"❌ Certifications Fix test failed: {e}")
            return False
    
    def _is_invalid_certification(self, cert_name: str) -> bool:
        """Check if certification name is invalid"""
        cert_lower = cert_name.lower()
        return any(phrase in cert_lower for phrase in [
            'this is', 'another', 'project', 'work', 'sentence', 'entry', 'invalid'
        ])
    
    def test_comprehensive_fix(self) -> bool:
        """Test comprehensive pipeline fix"""
        logger.info("Testing Comprehensive Fix")
        
        try:
            from app.services.parser.comprehensive_pipeline_fix import comprehensive_fix
            
            # Test with sample parsed data
            sample_data = {
                'work_experience': [
                    {
                        'jobTitle': '',
                        'company': '',
                        'description': 'Some description'
                    }
                ],
                'skills': [
                    {'name': 'TECHNOLOGIES REFERENCE'},
                    {'name': 'Python'}
                ],
                'education': [
                    {'degree': '', 'institution': ''}
                ],
                'certifications': [
                    {'name': 'This is a long sentence that should be filtered'},
                    {'name': 'AWS Certified'}
                ],
                'contact': {
                    'name': {'name': 'John Doe'},
                    'emails': ['john@example.com']
                }
            }
            
            # Apply comprehensive fix
            fixed_data = comprehensive_fix.apply_comprehensive_fix(sample_data)
            
            # Validate fixes
            assert fixed_data.get('work_experience'), "Missing work_experience after fix"
            assert fixed_data.get('skills'), "Missing skills after fix"
            assert fixed_data.get('education'), "Missing education after fix"
            assert fixed_data.get('certifications'), "Missing certifications after fix"
            assert fixed_data.get('basics'), "Missing basics after fix"
            
            # Validate no null/empty values in work experience
            for job in fixed_data.get('work_experience', []):
                assert job.get('jobTitle'), "Missing jobTitle in fixed work experience"
                assert job.get('company'), "Missing company in fixed work experience"
            
            # Validate skills filtering
            skill_names = [skill.get('name', '') for skill in fixed_data.get('skills', [])]
            assert not any('TECHNOLOGIES REFERENCE' in name.upper() for name in skill_names), "Noise skill not filtered"
            
            # Validate comprehensive fix validation
            is_valid = comprehensive_fix.validate_fixed_data(fixed_data)
            assert is_valid, "Fixed data validation failed"
            
            self.test_results['comprehensive_fix']['passed'] += 1
            logger.info("✅ Comprehensive Fix tests passed")
            return True
            
        except Exception as e:
            self.test_results['comprehensive_fix']['failed'] += 1
            self.test_results['comprehensive_fix']['errors'].append(str(e))
            logger.error(f"❌ Comprehensive Fix test failed: {e}")
            return False
    
    def test_json_structure_compliance(self) -> bool:
        """Test JSON structure compliance"""
        logger.info("Testing JSON Structure Compliance")
        
        try:
            from app.services.parser.json_format_adapter import unified_json_adapter
            
            # Test with sample data
            sample_data = {
                'basics': {
                    'firstName': 'John',
                    'lastName': 'Doe',
                    'emails': ['john@example.com']
                },
                'work_experience': [
                    {
                        'jobTitle': 'Software Engineer',
                        'company': 'Google',
                        'startDate': '2020-01-01',
                        'endDate': 'Present'
                    }
                ],
                'skills': [
                    {'name': 'Python', 'category': 'Programming'}
                ],
                'education': [
                    {
                        'institution': 'Stanford University',
                        'degree': 'Bachelor of Science',
                        'graduationYear': '2020'
                    }
                ],
                'certifications': [
                    {'name': 'AWS Certified Solutions Architect'}
                ],
                'sections': {
                    'summary': {'content': 'Experienced software engineer'}
                },
                'metadata': {}
            }
            
            # Validate structure
            is_valid = unified_json_adapter.validate_json_structure(sample_data)
            assert is_valid, "JSON structure validation failed"
            
            self.test_results['json_structure']['passed'] += 1
            logger.info("✅ JSON Structure Compliance tests passed")
            return True
            
        except Exception as e:
            self.test_results['json_structure']['failed'] += 1
            self.test_results['json_structure']['errors'].append(str(e))
            logger.error(f"❌ JSON Structure Compliance test failed: {e}")
            return False
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all comprehensive tests"""
        logger.info("🧪 Running Comprehensive Test Suite")
        
        # Run individual tests
        self.test_work_experience_fix()
        self.test_skills_fix()
        self.test_education_fix()
        self.test_certifications_fix()
        self.test_comprehensive_fix()
        self.test_json_structure_compliance()
        
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
            'status': 'PASSED' if success_rate >= 85 else 'FAILED',  # High accuracy requirement
            'accuracy_achieved': f"{success_rate:.1f}%"
        }
        
        return overall_results
    
    def print_results(self, results: Dict[str, Any]):
        """Print comprehensive test results"""
        print("\n" + "="*70)
        print("🧪 COMPREHENSIVE PARSING SYSTEM TEST RESULTS")
        print("="*70)
        
        print(f"📊 Overall Results:")
        print(f"   Total Tests: {results['total_tests']}")
        print(f"   Passed: {results['total_passed']}")
        print(f"   Failed: {results['total_failed']}")
        print(f"   Success Rate: {results['accuracy_achieved']}")
        print(f"   Status: {results['status']}")
        print(f"   Target Accuracy: 85-95%")
        
        print(f"\n📋 Test Details:")
        for test_name, result in results['test_details'].items():
            if result['passed'] > 0 or result['failed'] > 0:
                status = "✅ PASS" if result['failed'] == 0 else "❌ FAIL"
                print(f"   {test_name}: {status} ({result['passed']} passed, {result['failed']} failed)")
                
                if result['errors']:
                    for error in result['errors']:
                        print(f"      Error: {error}")
        
        print("\n" + "="*70)
        
        if results['status'] == 'PASSED':
            print("🎉 All tests passed! Enhanced parsing system meets accuracy requirements.")
            print("✅ Key-value mismatches resolved")
            print("✅ Structured extraction working correctly")
            print("✅ JSON schema compliance maintained")
        else:
            print("⚠️  Some tests failed. Review errors above.")
        
        print("="*70)

def main():
    """Main testing function"""
    tester = ComprehensiveTestSuite()
    results = tester.run_all_tests()
    tester.print_results(results)
    
    return results['status'] == 'PASSED'

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
