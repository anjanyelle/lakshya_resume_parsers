#!/usr/bin/env python3
"""
Test Suite for NER Post-Processor

Tests all 13 phases of the production-grade NER post-processing pipeline.

Run tests:
    python -m pytest tests/test_ner_postprocessor.py -v
    
Or:
    python tests/test_ner_postprocessor.py

Author: AI Engineering Team
Version: 1.0.0
"""

import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import unittest
import logging
from parsers.ner_postprocessor import NERPostProcessor


class TestPhase1PreProcessing(unittest.TestCase):
    """Test Phase 1: Pre-processing"""
    
    def test_email_removal(self):
        """Test email address removal"""
        text = "Contact: john.doe@company.com for more info"
        result = NERPostProcessor.preprocess_text(text)
        self.assertNotIn("john.doe@company.com", result)
        self.assertIn("[EMAIL]", result)
    
    def test_phone_removal(self):
        """Test phone number removal"""
        text = "Call me at +1-555-123-4567 or 9876543210"
        result = NERPostProcessor.preprocess_text(text)
        self.assertNotIn("+1-555-123-4567", result)
        self.assertNotIn("9876543210", result)
        self.assertIn("[PHONE]", result)
    
    def test_url_removal(self):
        """Test URL removal"""
        text = "Visit linkedin.com/in/johndoe or https://github.com/johndoe"
        result = NERPostProcessor.preprocess_text(text)
        self.assertNotIn("linkedin.com", result)
        self.assertNotIn("github.com", result)
        self.assertIn("[URL]", result)
    
    def test_whitespace_normalization(self):
        """Test whitespace normalization"""
        text = "Too    many     spaces\n\n\nand\n\n\nnewlines"
        result = NERPostProcessor.preprocess_text(text)
        self.assertNotIn("    ", result)
        self.assertNotIn("\n\n\n", result)
    
    def test_duplicate_line_removal(self):
        """Test duplicate line removal"""
        text = "Line 1\nLine 2\nLine 1\nLine 3"
        result = NERPostProcessor.preprocess_text(text)
        lines = result.split('\n')
        # First occurrence of "Line 1" should be kept, duplicate removed
        self.assertEqual(lines.count("Line 1"), 1)


class TestPhase3ConfidenceFiltering(unittest.TestCase):
    """Test Phase 3: Confidence Filtering"""
    
    def setUp(self):
        self.processor = NERPostProcessor()
    
    def test_high_confidence_accepted(self):
        """Test that high confidence entities are accepted"""
        entities = [
            {"entity_group": "ROLE", "word": "Senior Developer", "score": 0.98}
        ]
        result = self.processor.filter_by_confidence(entities)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['word'], "Senior Developer")
    
    def test_low_confidence_rejected(self):
        """Test that low confidence entities are rejected"""
        entities = [
            {"entity_group": "ROLE", "word": "Uncertain Role", "score": 0.75}
        ]
        result = self.processor.filter_by_confidence(entities)
        self.assertEqual(len(result), 0)
    
    def test_threshold_boundary(self):
        """Test entities at threshold boundary"""
        entities = [
            {"entity_group": "ROLE", "word": "Exactly at threshold", "score": 0.92},
            {"entity_group": "ROLE", "word": "Just below threshold", "score": 0.91}
        ]
        result = self.processor.filter_by_confidence(entities)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['word'], "Exactly at threshold")
    
    def test_custom_thresholds(self):
        """Test custom confidence thresholds"""
        custom_processor = NERPostProcessor(confidence_thresholds={'ROLE': 0.95})
        entities = [
            {"entity_group": "ROLE", "word": "High bar role", "score": 0.93}
        ]
        result = custom_processor.filter_by_confidence(entities)
        self.assertEqual(len(result), 0)  # Should be rejected with 0.95 threshold


class TestPhase4RoleValidation(unittest.TestCase):
    """Test Phase 4: Role Validation"""
    
    def setUp(self):
        self.processor = NERPostProcessor()
    
    def test_valid_roles_accepted(self):
        """Test that valid job titles are accepted"""
        valid_roles = [
            "Senior Full Stack Developer",
            "Software Engineer",
            "Technical Lead",
            "Product Manager",
            "Data Scientist"
        ]
        for role in valid_roles:
            self.assertTrue(
                self.processor.validate_role(role),
                f"Valid role rejected: {role}"
            )
    
    def test_invalid_roles_rejected(self):
        """Test that tasks/skills are rejected as roles"""
        invalid_roles = [
            "integration test cases",
            "unit testing",
            "code reviews",
            "sprint planning",
            "business analysts",  # Plural form
            "REST APIs",
            "microservices"
        ]
        for role in invalid_roles:
            self.assertFalse(
                self.processor.validate_role(role),
                f"Invalid role accepted: {role}"
            )
    
    def test_plural_forms_rejected(self):
        """Test that plural forms are rejected"""
        self.assertFalse(self.processor.validate_role("developers"))
        self.assertFalse(self.processor.validate_role("engineers"))
        self.assertFalse(self.processor.validate_role("managers"))
    
    def test_case_sensitivity(self):
        """Test that all-lowercase or all-uppercase roles are rejected"""
        self.assertFalse(self.processor.validate_role("senior developer"))  # All lowercase
        self.assertFalse(self.processor.validate_role("SENIOR DEVELOPER"))  # All uppercase
        self.assertTrue(self.processor.validate_role("Senior Developer"))  # Proper case


class TestPhase5CompanyValidation(unittest.TestCase):
    """Test Phase 5: Company Validation"""
    
    def setUp(self):
        self.processor = NERPostProcessor()
    
    def test_valid_companies_accepted(self):
        """Test that valid company names are accepted"""
        valid_companies = [
            "Infosys Limited",
            "TechMahindra Pvt Ltd",
            "Accenture",
            "Google Inc",
            "Microsoft Corporation"
        ]
        for company in valid_companies:
            self.assertTrue(
                self.processor.validate_company(company),
                f"Valid company rejected: {company}"
            )
    
    def test_tech_keywords_rejected(self):
        """Test that technology keywords are rejected as companies"""
        tech_keywords = [
            "React",
            "Node.js",
            "Python",
            "AWS",
            "Docker",
            "Kubernetes"
        ]
        for keyword in tech_keywords:
            self.assertFalse(
                self.processor.validate_company(keyword),
                f"Tech keyword accepted as company: {keyword}"
            )
    
    def test_company_indicators(self):
        """Test that company indicators boost acceptance"""
        self.assertTrue(self.processor.validate_company("XYZ Technologies"))
        self.assertTrue(self.processor.validate_company("ABC Solutions"))
        self.assertTrue(self.processor.validate_company("DEF Consulting"))


class TestPhase7LocationValidation(unittest.TestCase):
    """Test Phase 7: Location Validation"""
    
    def setUp(self):
        self.processor = NERPostProcessor()
    
    def test_known_locations_accepted(self):
        """Test that known locations are accepted"""
        locations = [
            "Hyderabad",
            "Bangalore",
            "New York",
            "San Francisco",
            "London"
        ]
        for location in locations:
            self.assertTrue(
                self.processor.validate_location(location),
                f"Known location rejected: {location}"
            )
    
    def test_location_patterns(self):
        """Test location pattern recognition"""
        self.assertTrue(self.processor.validate_location("Seattle, WA"))
        self.assertTrue(self.processor.validate_location("New York, USA"))
        self.assertTrue(self.processor.validate_location("Hyderabad, Telangana"))
    
    def test_short_locations_rejected(self):
        """Test that very short strings are rejected"""
        self.assertFalse(self.processor.validate_location("NY"))
        self.assertFalse(self.processor.validate_location("CA"))


class TestPhase8EducationValidation(unittest.TestCase):
    """Test Phase 8: Education Validation"""
    
    def setUp(self):
        self.processor = NERPostProcessor()
    
    def test_valid_degrees_accepted(self):
        """Test that valid degrees are accepted"""
        degrees = [
            "Bachelor of Technology",
            "Master of Science",
            "PhD in Computer Science",
            "MBA",
            "B.Tech"
        ]
        for degree in degrees:
            self.assertTrue(
                self.processor.validate_degree(degree),
                f"Valid degree rejected: {degree}"
            )
    
    def test_valid_institutions_accepted(self):
        """Test that valid institutions are accepted"""
        institutions = [
            "JNTU Hyderabad",
            "Stanford University",
            "MIT",
            "IIT Delhi",
            "Anna University"
        ]
        for institution in institutions:
            self.assertTrue(
                self.processor.validate_institution(institution),
                f"Valid institution rejected: {institution}"
            )
    
    def test_valid_fields_accepted(self):
        """Test that valid fields of study are accepted"""
        fields = [
            "Computer Science and Engineering",
            "Information Technology",
            "Electrical Engineering",
            "Business Administration"
        ]
        for field in fields:
            self.assertTrue(
                self.processor.validate_field(field),
                f"Valid field rejected: {field}"
            )


class TestPhase9EntityMerging(unittest.TestCase):
    """Test Phase 9: Entity Merging"""
    
    def setUp(self):
        self.processor = NERPostProcessor()
    
    def test_company_fragments_merged(self):
        """Test that fragmented company names are merged"""
        entities = [
            {"entity_group": "COMPANY", "word": "TechMahindra Pvt", "score": 0.95},
            {"entity_group": "COMPANY", "word": "Ltd", "score": 0.93}
        ]
        result = self.processor.merge_fragmented_entities(entities)
        self.assertEqual(len(result), 1)
        self.assertIn("TechMahindra Pvt Ltd", result[0]['word'])
    
    def test_role_fragments_merged(self):
        """Test that fragmented roles are merged"""
        entities = [
            {"entity_group": "ROLE", "word": "Senior", "score": 0.96},
            {"entity_group": "ROLE", "word": "Full", "score": 0.94},
            {"entity_group": "ROLE", "word": "Stack", "score": 0.95},
            {"entity_group": "ROLE", "word": "Developer", "score": 0.97}
        ]
        result = self.processor.merge_fragmented_entities(entities)
        # Should merge into fewer entities
        self.assertLess(len(result), len(entities))
    
    def test_different_types_not_merged(self):
        """Test that different entity types are not merged"""
        entities = [
            {"entity_group": "COMPANY", "word": "Google", "score": 0.95},
            {"entity_group": "ROLE", "word": "Engineer", "score": 0.94}
        ]
        result = self.processor.merge_fragmented_entities(entities)
        self.assertEqual(len(result), 2)  # Should remain separate


class TestPhase10Deduplication(unittest.TestCase):
    """Test Phase 10: Deduplication"""
    
    def setUp(self):
        self.processor = NERPostProcessor()
    
    def test_exact_duplicates_removed(self):
        """Test that exact duplicates are removed"""
        entities = {
            'COMPANY': ['Google', 'Google', 'Microsoft'],
            'ROLE': ['Developer', 'Developer']
        }
        result = self.processor.deduplicate_entities(entities)
        self.assertEqual(len(result['COMPANY']), 2)
        self.assertEqual(len(result['ROLE']), 1)
    
    def test_location_deduplication(self):
        """Test that location duplicates are handled correctly"""
        entities = {
            'LOCATION': ['Hyderabad', 'Hyderabad, Telangana', 'Bangalore']
        }
        result = self.processor.deduplicate_entities(entities)
        # Should keep the more specific version
        self.assertIn('Hyderabad, Telangana', result['LOCATION'])
        self.assertNotIn('Hyderabad', result['LOCATION'])
    
    def test_case_insensitive_deduplication(self):
        """Test that deduplication is case-insensitive"""
        entities = {
            'COMPANY': ['Google', 'google', 'GOOGLE']
        }
        result = self.processor.deduplicate_entities(entities)
        self.assertEqual(len(result['COMPANY']), 1)


class TestPhase11Normalization(unittest.TestCase):
    """Test Phase 11: Normalization"""
    
    def setUp(self):
        self.processor = NERPostProcessor()
    
    def test_date_normalization(self):
        """Test date normalization"""
        entities = {
            'DATE_START': ['jan 2022', 'Dec 2021'],
            'DATE_END': ['mar 2023']
        }
        result = self.processor.normalize_entities(entities)
        self.assertIn('January 2022', result['DATE_START'])
        self.assertIn('December 2021', result['DATE_START'])
        self.assertIn('March 2023', result['DATE_END'])
    
    def test_proper_noun_normalization(self):
        """Test proper noun normalization (companies, institutions)"""
        entities = {
            'COMPANY': ['infosys limited', 'GOOGLE INC'],
            'INSTITUTION': ['stanford university']
        }
        result = self.processor.normalize_entities(entities)
        self.assertIn('Infosys Limited', result['COMPANY'])
        self.assertIn('Google Inc', result['COMPANY'])
        self.assertIn('Stanford University', result['INSTITUTION'])
    
    def test_location_normalization(self):
        """Test location normalization"""
        entities = {
            'LOCATION': ['new york, usa', 'LONDON, UK']
        }
        result = self.processor.normalize_entities(entities)
        self.assertIn('New York, Usa', result['LOCATION'])
        self.assertIn('London, Uk', result['LOCATION'])


class TestCompleteIntegration(unittest.TestCase):
    """Test complete end-to-end pipeline"""
    
    def setUp(self):
        self.processor = NERPostProcessor()
    
    def test_complete_pipeline(self):
        """Test complete processing pipeline"""
        # Simulate raw NER output with various issues
        raw_entities = [
            # Valid entities
            {"entity_group": "ROLE", "word": "Senior Full Stack Developer", "score": 0.998},
            {"entity_group": "COMPANY", "word": "TechMahindra Pvt", "score": 0.943},
            {"entity_group": "COMPANY", "word": "Ltd", "score": 0.921},
            {"entity_group": "INSTITUTION", "word": "JNTU Hyderabad", "score": 0.941},
            {"entity_group": "LOCATION", "word": "Hyderabad", "score": 0.956},
            {"entity_group": "LOCATION", "word": "Hyderabad, Telangana", "score": 0.948},
            
            # Invalid entities (should be filtered)
            {"entity_group": "ROLE", "word": "business analysts", "score": 0.935},  # Plural
            {"entity_group": "ROLE", "word": "integration test cases", "score": 0.912},  # Task
            {"entity_group": "COMPANY", "word": "React", "score": 0.889},  # Tech keyword
            {"entity_group": "COMPANY", "word": "AWS", "score": 0.850},  # Low confidence + tech
        ]
        
        result = self.processor.process(raw_entities)
        
        # Assertions
        self.assertIn("Senior Full Stack Developer", result['roles'])
        self.assertNotIn("business analysts", result['roles'])
        self.assertNotIn("integration test cases", result['roles'])
        
        # Company should be merged
        self.assertTrue(
            any("TechMahindra Pvt Ltd" in company for company in result['companies']),
            f"Expected merged company, got: {result['companies']}"
        )
        self.assertNotIn("React", result['companies'])
        self.assertNotIn("AWS", result['companies'])
        
        # Location deduplication
        self.assertIn("Hyderabad, Telangana", result['locations'])
        # "Hyderabad" alone should be removed in favor of the more specific version
        
        # Institution
        self.assertIn("JNTU Hyderabad", result['institutions'])
    
    def test_empty_input(self):
        """Test handling of empty input"""
        result = self.processor.process([])
        self.assertEqual(result['companies'], [])
        self.assertEqual(result['roles'], [])
        self.assertEqual(result['locations'], [])
    
    def test_all_filtered_input(self):
        """Test handling when all entities are filtered out"""
        raw_entities = [
            {"entity_group": "ROLE", "word": "invalid", "score": 0.50},
            {"entity_group": "COMPANY", "word": "React", "score": 0.60}
        ]
        result = self.processor.process(raw_entities)
        self.assertEqual(result['companies'], [])
        self.assertEqual(result['roles'], [])


class TestStatistics(unittest.TestCase):
    """Test statistics tracking"""
    
    def test_statistics_tracking(self):
        """Test that statistics are properly tracked"""
        processor = NERPostProcessor()
        
        raw_entities = [
            {"entity_group": "ROLE", "word": "Senior Developer", "score": 0.98},
            {"entity_group": "ROLE", "word": "invalid role", "score": 0.70},
            {"entity_group": "COMPANY", "word": "Google", "score": 0.95},
            {"entity_group": "COMPANY", "word": "Google", "score": 0.94},
        ]
        
        result = processor.process(raw_entities)
        
        # Check statistics
        self.assertEqual(processor.stats['total_entities'], 4)
        self.assertGreater(processor.stats['filtered_by_confidence'], 0)
        self.assertGreaterEqual(processor.stats['deduplicated'], 0)


def run_tests():
    """Run all tests"""
    # Configure logging
    logging.basicConfig(level=logging.WARNING)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestPhase1PreProcessing))
    suite.addTests(loader.loadTestsFromTestCase(TestPhase3ConfidenceFiltering))
    suite.addTests(loader.loadTestsFromTestCase(TestPhase4RoleValidation))
    suite.addTests(loader.loadTestsFromTestCase(TestPhase5CompanyValidation))
    suite.addTests(loader.loadTestsFromTestCase(TestPhase7LocationValidation))
    suite.addTests(loader.loadTestsFromTestCase(TestPhase8EducationValidation))
    suite.addTests(loader.loadTestsFromTestCase(TestPhase9EntityMerging))
    suite.addTests(loader.loadTestsFromTestCase(TestPhase10Deduplication))
    suite.addTests(loader.loadTestsFromTestCase(TestPhase11Normalization))
    suite.addTests(loader.loadTestsFromTestCase(TestCompleteIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestStatistics))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("=" * 80)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
