# Resume Quality Classifier - Simple Implementation

import re
from typing import Dict, Any, List
from dataclasses import dataclass

@dataclass
class QualityMetrics:
    """Quality metrics for resume assessment"""
    completeness_score: float
    structure_score: float
    content_score: float
    overall_score: float
    issues: List[str]
    recommendations: List[str]

class ResumeQualityClassifier:
    """
    Simple resume quality classifier
    Assesses resume completeness, structure, and content quality
    """
    
    def __init__(self):
        self.required_sections = ['work', 'education', 'skills']
        self.important_sections = ['summary', 'projects', 'certifications']
        
    def classify_quality(self, resume_text: str, parsed_data: Dict[str, Any]) -> QualityMetrics:
        """
        Classify resume quality
        
        Args:
            resume_text: Raw resume text
            parsed_data: Parsed resume data
            
        Returns:
            QualityMetrics object with scores and recommendations
        """
        
        # Calculate completeness score
        completeness_score = self._calculate_completeness(parsed_data)
        
        # Calculate structure score
        structure_score = self._calculate_structure(resume_text)
        
        # Calculate content score
        content_score = self._calculate_content(resume_text, parsed_data)
        
        # Calculate overall score
        overall_score = (completeness_score + structure_score + content_score) / 3
        
        # Generate issues and recommendations
        issues, recommendations = self._generate_feedback(parsed_data, overall_score)
        
        return QualityMetrics(
            completeness_score=completeness_score,
            structure_score=structure_score,
            content_score=content_score,
            overall_score=overall_score,
            issues=issues,
            recommendations=recommendations
        )
    
    def _calculate_completeness(self, parsed_data: Dict[str, Any]) -> float:
        """Calculate completeness score based on required sections"""
        score = 0.0
        total_sections = len(self.required_sections) + len(self.important_sections)
        
        # Check required sections
        for section in self.required_sections:
            if section in parsed_data and parsed_data[section]:
                score += 1.0
        
        # Check important sections
        for section in self.important_sections:
            if section in parsed_data and parsed_data[section]:
                score += 0.5
        
        return min(score / total_sections * 100, 100)
    
    def _calculate_structure(self, resume_text: str) -> float:
        """Calculate structure score based on formatting and organization"""
        score = 50.0  # Base score
        
        lines = resume_text.split('\n')
        
        # Check for proper section headers
        header_pattern = r'^#+\s+\w+'
        headers = [line for line in lines if re.match(header_pattern, line.strip())]
        if len(headers) >= 3:
            score += 20
        elif len(headers) >= 1:
            score += 10
        
        # Check for consistent formatting
        bullet_lines = [line for line in lines if line.strip().startswith(('-', '•', '*', '·'))]
        if len(bullet_lines) >= 5:
            score += 15
        elif len(bullet_lines) >= 2:
            score += 8
        
        # Check for proper spacing
        empty_lines = [line for line in lines if not line.strip()]
        if 0.1 <= len(empty_lines) / len(lines) <= 0.3:
            score += 15
        
        return min(score, 100)
    
    def _calculate_content(self, resume_text: str, parsed_data: Dict[str, Any]) -> float:
        """Calculate content score based on quality and detail"""
        score = 50.0  # Base score
        
        # Check text length (should be substantial but not too long)
        if 500 <= len(resume_text) <= 2000:
            score += 20
        elif 2000 < len(resume_text) <= 4000:
            score += 15
        elif len(resume_text) < 500:
            score -= 20
        
        # Check for contact information
        if self._has_contact_info(resume_text):
            score += 15
        
        # Check for detailed work experience
        work_exp = parsed_data.get('work', [])
        if work_exp:
            detailed_jobs = [job for job in work_exp if len(str(job.get('description', ''))) > 100]
            if len(detailed_jobs) >= 2:
                score += 15
            elif len(detailed_jobs) >= 1:
                score += 8
        
        return min(score, 100)
    
    def _has_contact_info(self, text: str) -> bool:
        """Check if resume contains contact information"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
        
        has_email = bool(re.search(email_pattern, text))
        has_phone = bool(re.search(phone_pattern, text))
        
        return has_email or has_phone
    
    def _generate_feedback(self, parsed_data: Dict[str, Any], overall_score: float) -> tuple[List[str], List[str]]:
        """Generate feedback based on quality assessment"""
        issues = []
        recommendations = []
        
        # Check for missing required sections
        for section in self.required_sections:
            if section not in parsed_data or not parsed_data[section]:
                issues.append(f"Missing {section} section")
                recommendations.append(f"Add a {section} section to improve completeness")
        
        # Check for missing important sections
        for section in self.important_sections:
            if section not in parsed_data or not parsed_data[section]:
                recommendations.append(f"Consider adding a {section} section")
        
        # Specific recommendations based on score
        if overall_score < 60:
            issues.append("Overall resume quality needs improvement")
            recommendations.append("Review and enhance all sections for better impact")
        elif overall_score < 80:
            recommendations.append("Good foundation, consider adding more details")
        
        return issues, recommendations

# Global instance
quality_classifier = ResumeQualityClassifier()
