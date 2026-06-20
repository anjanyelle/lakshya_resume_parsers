"""
Accuracy Testing Framework for Resume Parser
Systematic testing against ground truth data with comprehensive metrics
"""

import json
import logging
import os
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from pathlib import Path
import difflib
from statistics import mean
import hashlib

logger = logging.getLogger(__name__)


class AccuracyMetrics:
    """Comprehensive accuracy metrics for resume parsing evaluation."""
    
    def __init__(self):
        """Initialize accuracy metrics calculator."""
        self.metrics = {}
        
    def calculate_text_extraction_accuracy(
        self, 
        extracted_text: str, 
        ground_truth_text: str
    ) -> Dict[str, float]:
        """
        Calculate text extraction accuracy using character and word level metrics.
        
        Args:
            extracted_text: Text extracted by parser
            ground_truth_text: Ground truth text
            
        Returns:
            Dictionary with accuracy metrics
        """
        if not extracted_text or not ground_truth_text:
            return {
                'character_accuracy': 0.0,
                'word_accuracy': 0.0,
                'levenshtein_similarity': 0.0,
                'length_ratio': 0.0
            }
            
        # Character-level accuracy
        char_diff = difflib.SequenceMatcher(None, ground_truth_text, extracted_text)
        char_accuracy = char_diff.ratio()
        
        # Word-level accuracy
        ground_truth_words = ground_truth_text.split()
        extracted_words = extracted_text.split()
        
        word_diff = difflib.SequenceMatcher(None, ground_truth_words, extracted_words)
        word_accuracy = word_diff.ratio()
        
        # Length ratio
        length_ratio = min(len(extracted_text), len(ground_truth_text)) / max(len(extracted_text), len(ground_truth_text))
        
        return {
            'character_accuracy': char_accuracy,
            'word_accuracy': word_accuracy,
            'levenshtein_similarity': char_accuracy,  # Using ratio as similarity
            'length_ratio': length_ratio
        }
        
    def calculate_section_detection_accuracy(
        self, 
        extracted_sections: Dict[str, str], 
        ground_truth_sections: Dict[str, str]
    ) -> Dict[str, float]:
        """
        Calculate section detection accuracy.
        
        Args:
            extracted_sections: Sections detected by parser
            ground_truth_sections: Ground truth sections
            
        Returns:
            Dictionary with section detection metrics
        """
        extracted_section_names = set(name.lower() for name in extracted_sections.keys())
        ground_truth_section_names = set(name.lower() for name in ground_truth_sections.keys())
        
        # Calculate precision, recall, F1
        true_positives = len(extracted_section_names & ground_truth_section_names)
        false_positives = len(extracted_section_names - ground_truth_section_names)
        false_negatives = len(ground_truth_section_names - extracted_section_names)
        
        precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0.0
        recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0.0
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
        
        # Section boundary accuracy
        boundary_accuracy = self._calculate_boundary_accuracy(extracted_sections, ground_truth_sections)
        
        return {
            'precision': precision,
            'recall': recall,
            'f1_score': f1_score,
            'boundary_accuracy': boundary_accuracy,
            'true_positives': true_positives,
            'false_positives': false_positives,
            'false_negatives': false_negatives
        }
        
    def _calculate_boundary_accuracy(
        self, 
        extracted_sections: Dict[str, str], 
        ground_truth_sections: Dict[str, str]
    ) -> float:
        """Calculate how accurately section boundaries were detected."""
        # Simplified boundary accuracy based on section content overlap
        total_overlap = 0
        total_sections = 0
        
        for section_name in ground_truth_sections.keys():
            total_sections += 1
            gt_content = ground_truth_sections[section_name].lower()
            
            # Find best matching extracted section
            best_overlap = 0.0
            for extracted_name, extracted_content in extracted_sections.items():
                extracted_content_lower = extracted_content.lower()
                
                # Calculate content overlap
                overlap = difflib.SequenceMatcher(None, gt_content, extracted_content_lower).ratio()
                best_overlap = max(best_overlap, overlap)
                
            total_overlap += best_overlap
            
        return total_overlap / total_sections if total_sections > 0 else 0.0
        
    def calculate_entity_extraction_accuracy(
        self, 
        extracted_entities: Dict[str, Any], 
        ground_truth_entities: Dict[str, Any]
    ) -> Dict[str, float]:
        """
        Calculate entity extraction accuracy using F1 scores for each field.
        
        Args:
            extracted_entities: Entities extracted by parser
            ground_truth_entities: Ground truth entities
            
        Returns:
            Dictionary with entity extraction metrics
        """
        field_metrics = {}
        
        # Get all unique field names from both extracted and ground truth
        all_fields = set(extracted_entities.keys()) | set(ground_truth_entities.keys())
        
        for field in all_fields:
            extracted_value = extracted_entities.get(field)
            ground_truth_value = ground_truth_entities.get(field)
            
            if isinstance(extracted_value, list) and isinstance(ground_truth_value, list):
                # For arrays, calculate F1 score
                field_metrics[field] = self._calculate_array_f1(extracted_value, ground_truth_value)
            elif isinstance(extracted_value, dict) and isinstance(ground_truth_value, dict):
                # For nested dicts, calculate average of sub-fields
                sub_metrics = self.calculate_entity_extraction_accuracy(extracted_value, ground_truth_value)
                field_metrics[field] = mean(sub_metrics.values()) if sub_metrics else 0.0
            else:
                # For simple values, use exact match
                field_metrics[field] = 1.0 if str(extracted_value) == str(ground_truth_value) else 0.0
                
        # Calculate overall metrics
        overall_accuracy = mean(field_metrics.values()) if field_metrics else 0.0
        
        return {
            'overall_accuracy': overall_accuracy,
            'field_metrics': field_metrics,
            'total_fields': len(field_metrics),
            'perfect_fields': sum(1 for v in field_metrics.values() if v == 1.0)
        }
        
    def _calculate_array_f1(self, extracted_list: List[Any], ground_truth_list: List[Any]) -> float:
        """Calculate F1 score for array fields."""
        if not extracted_list and not ground_truth_list:
            return 1.0  # Both empty is perfect match
            
        if not extracted_list or not ground_truth_list:
            return 0.0  # One empty is no match
            
        # Convert to strings for comparison
        extracted_str = [str(item).lower().strip() for item in extracted_list]
        ground_truth_str = [str(item).lower().strip() for item in ground_truth_list]
        
        # Calculate true positives, false positives, false negatives
        true_positives = sum(1 for item in extracted_str if item in ground_truth_str)
        false_positives = len(extracted_str) - true_positives
        false_negatives = len(ground_truth_str) - true_positives
        
        precision = true_positives / len(extracted_str) if extracted_str else 0.0
        recall = true_positives / len(ground_truth_str) if ground_truth_str else 0.0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
        
        return f1
        
    def calculate_overall_pipeline_accuracy(
        self, 
        text_accuracy: Dict[str, float],
        section_accuracy: Dict[str, float],
        entity_accuracy: Dict[str, float]
    ) -> Dict[str, float]:
        """
        Calculate overall pipeline accuracy with weighted components.
        
        Args:
            text_accuracy: Text extraction metrics
            section_accuracy: Section detection metrics
            entity_accuracy: Entity extraction metrics
            
        Returns:
            Overall accuracy metrics
        """
        # Weight different components
        weights = {
            'text_extraction': 0.2,
            'section_detection': 0.3,
            'entity_extraction': 0.5
        }
        
        overall_accuracy = (
            text_accuracy.get('character_accuracy', 0.0) * weights['text_extraction'] +
            section_accuracy.get('f1_score', 0.0) * weights['section_detection'] +
            entity_accuracy.get('overall_accuracy', 0.0) * weights['entity_extraction']
        )
        
        return {
            'overall_accuracy': overall_accuracy,
            'component_weights': weights,
            'weighted_scores': {
                'text_extraction': text_accuracy.get('character_accuracy', 0.0) * weights['text_extraction'],
                'section_detection': section_accuracy.get('f1_score', 0.0) * weights['section_detection'],
                'entity_extraction': entity_accuracy.get('overall_accuracy', 0.0) * weights['entity_extraction']
            }
        }


class AccuracyTester:
    """
    Main accuracy testing framework that runs systematic tests against ground truth data.
    """
    
    def __init__(self, parser_instance):
        """
        Initialize accuracy tester.
        
        Args:
            parser_instance: Instance of MasterParser or similar
        """
        self.parser = parser_instance
        self.metrics_calculator = AccuracyMetrics()
        self.test_results = []
        
    def run_single_test(
        self, 
        resume_path: str, 
        ground_truth: Dict[str, Any],
        test_name: str = None
    ) -> Dict[str, Any]:
        """
        Run accuracy test for a single resume.
        
        Args:
            resume_path: Path to resume file
            ground_truth: Ground truth data
            test_name: Name of the test case
            
        Returns:
            Test results dictionary
        """
        test_name = test_name or Path(resume_path).stem
        start_time = datetime.now()
        
        try:
            # Parse the resume
            parsing_result = self.parser.parse_file(resume_path, f"test_{test_name}")
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Calculate accuracy metrics
            text_accuracy = self.metrics_calculator.calculate_text_extraction_accuracy(
                parsing_result.get('raw_text', ''),
                ground_truth.get('raw_text', '')
            )
            
            section_accuracy = self.metrics_calculator.calculate_section_detection_accuracy(
                parsing_result.get('sections', {}),
                ground_truth.get('sections', {})
            )
            
            entity_accuracy = self.metrics_calculator.calculate_entity_extraction_accuracy(
                parsing_result,
                ground_truth
            )
            
            overall_accuracy = self.metrics_calculator.calculate_overall_pipeline_accuracy(
                text_accuracy, section_accuracy, entity_accuracy
            )
            
            test_result = {
                'test_name': test_name,
                'resume_path': resume_path,
                'status': 'success',
                'processing_time_seconds': processing_time,
                'text_accuracy': text_accuracy,
                'section_accuracy': section_accuracy,
                'entity_accuracy': entity_accuracy,
                'overall_accuracy': overall_accuracy,
                'parsed_data': parsing_result,
                'ground_truth': ground_truth,
                'timestamp': datetime.now().isoformat()
            }
            
            self.test_results.append(test_result)
            logger.info(f"✅ Test '{test_name}' completed with accuracy: {overall_accuracy['overall_accuracy']:.2%}")
            
            return test_result
            
        except Exception as e:
            logger.error(f"❌ Test '{test_name}' failed: {e}")
            return {
                'test_name': test_name,
                'resume_path': resume_path,
                'status': 'failed',
                'error': str(e),
                'processing_time_seconds': (datetime.now() - start_time).total_seconds(),
                'timestamp': datetime.now().isoformat()
            }
            
    def run_test_suite(
        self, 
        test_suite_path: str, 
        ground_truth_path: str
    ) -> Dict[str, Any]:
        """
        Run complete test suite against multiple resumes.
        
        Args:
            test_suite_path: Path to directory containing test resumes
            ground_truth_path: Path to ground truth JSON file
            
        Returns:
            Test suite results
        """
        # Load ground truth data
        with open(ground_truth_path, 'r') as f:
            ground_truth_data = json.load(f)
            
        # Get all resume files
        resume_files = list(Path(test_suite_path).glob('*.pdf')) + \
                      list(Path(test_suite_path).glob('*.docx')) + \
                      list(Path(test_suite_path).glob('*.txt'))
                      
        logger.info(f"🚀 Starting test suite with {len(resume_files)} resumes")
        
        suite_results = {
            'test_suite_name': Path(test_suite_path).name,
            'total_tests': len(resume_files),
            'successful_tests': 0,
            'failed_tests': 0,
            'test_results': [],
            'aggregate_metrics': {},
            'timestamp': datetime.now().isoformat()
        }
        
        # Run each test
        for resume_file in resume_files:
            # Find corresponding ground truth
            file_hash = self._calculate_file_hash(resume_file)
            ground_truth = ground_truth_data.get(file_hash)
            
            if not ground_truth:
                # Try to match by filename (without extension)
                filename_key = resume_file.stem
                ground_truth = ground_truth_data.get(filename_key)
                
            if not ground_truth:
                # Try to match by full filename (with extension)
                full_filename = resume_file.name
                ground_truth = ground_truth_data.get(full_filename)
                
            if not ground_truth:
                logger.warning(f"⚠️  No ground truth found for {resume_file.name}, skipping")
                continue
                
            # Run single test
            test_result = self.run_single_test(str(resume_file), ground_truth, resume_file.stem)
            suite_results['test_results'].append(test_result)
            
            if test_result['status'] == 'success':
                suite_results['successful_tests'] += 1
            else:
                suite_results['failed_tests'] += 1
                
        # Calculate aggregate metrics
        suite_results['aggregate_metrics'] = self._calculate_aggregate_metrics(suite_results['test_results'])
        
        logger.info(f"🎉 Test suite completed: {suite_results['successful_tests']}/{suite_results['total_tests']} tests passed")
        
        return suite_results
        
    def _calculate_aggregate_metrics(self, test_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate aggregate metrics across all test results."""
        successful_results = [r for r in test_results if r['status'] == 'success']
        
        if not successful_results:
            return {
                'success_rate': 0.0,
                'average_processing_time': 0.0,
                'average_overall_accuracy': 0.0
            }
            
        # Calculate averages
        overall_accuracies = [r['overall_accuracy']['overall_accuracy'] for r in successful_results]
        processing_times = [r['processing_time_seconds'] for r in successful_results]
        
        return {
            'success_rate': len(successful_results) / len(test_results),
            'average_processing_time': mean(processing_times),
            'average_overall_accuracy': mean(overall_accuracies),
            'min_accuracy': min(overall_accuracies),
            'max_accuracy': max(overall_accuracies),
            'accuracy_std_dev': self._calculate_std_dev(overall_accuracies),
            'total_tests': len(test_results),
            'successful_tests': len(successful_results),
            'failed_tests': len(test_results) - len(successful_results)
        }
        
    def _calculate_std_dev(self, values: List[float]) -> float:
        """Calculate standard deviation."""
        if len(values) < 2:
            return 0.0
            
        mean_val = mean(values)
        variance = sum((x - mean_val) ** 2 for x in values) / len(values)
        return variance ** 0.5
        
    def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate hash of file for matching with ground truth."""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
        
    def generate_report(self, output_path: str = None) -> str:
        """
        Generate comprehensive test report.
        
        Args:
            output_path: Path to save report
            
        Returns:
            Path to generated report
        """
        if not self.test_results:
            return None
            
        report = {
            'report_metadata': {
                'generated_at': datetime.now().isoformat(),
                'total_tests': len(self.test_results),
                'successful_tests': sum(1 for r in self.test_results if r['status'] == 'success'),
                'failed_tests': sum(1 for r in self.test_results if r['status'] == 'failed')
            },
            'aggregate_metrics': self._calculate_aggregate_metrics(self.test_results),
            'detailed_results': self.test_results,
            'recommendations': self._generate_recommendations()
        }
        
        if output_path is None:
            output_path = f"accuracy_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
            
        logger.info(f"📄 Accuracy report generated: {output_path}")
        return output_path
        
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on test results."""
        recommendations = []
        
        if not self.test_results:
            return ["No test results available for recommendations"]
            
        successful_results = [r for r in self.test_results if r['status'] == 'success']
        
        if not successful_results:
            return ["All tests failed - review parser initialization and error handling"]
            
        # Analyze accuracy patterns
        overall_accuracies = [r['overall_accuracy']['overall_accuracy'] for r in successful_results]
        avg_accuracy = mean(overall_accuracies)
        
        if avg_accuracy < 0.7:
            recommendations.append("Overall accuracy is below 70% - consider model retraining or prompt optimization")
        elif avg_accuracy < 0.85:
            recommendations.append("Overall accuracy is moderate - focus on improving entity extraction")
        else:
            recommendations.append("Overall accuracy is good - maintain current configuration")
            
        # Analyze component performance
        avg_text_accuracy = mean([r['text_accuracy']['character_accuracy'] for r in successful_results])
        avg_section_accuracy = mean([r['section_accuracy']['f1_score'] for r in successful_results])
        avg_entity_accuracy = mean([r['entity_accuracy']['overall_accuracy'] for r in successful_results])
        
        if avg_text_accuracy < 0.9:
            recommendations.append("Text extraction accuracy needs improvement - check OCR and text extraction methods")
            
        if avg_section_accuracy < 0.8:
            recommendations.append("Section detection accuracy needs improvement - enhance section splitter")
            
        if avg_entity_accuracy < 0.8:
            recommendations.append("Entity extraction accuracy needs improvement - refine model or prompts")
            
        return recommendations