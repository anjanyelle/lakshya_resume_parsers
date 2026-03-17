#!/usr/bin/env python3
"""
Integration of Enhanced Work Experience & Certification Parser with LLM Service
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional
from enhanced_work_cert_parser import WorkExperienceParser, CertificationParser

class EnhancedResumeParser:
    """Enhanced resume parser with specialized work experience and certification extraction"""
    
    def __init__(self):
        self.work_parser = WorkExperienceParser()
        self.cert_parser = CertificationParser()
    
    def parse_resume_sections(self, resume_text: str) -> Dict:
        """Parse resume with enhanced work experience and certification extraction"""
        
        # Split resume into sections
        sections = self._split_into_sections(resume_text)
        
        result = {
            "work_experience": [],
            "certifications": [],
            "other_sections": {}
        }
        
        # Parse work experience section
        if "work" in sections:
            result["work_experience"] = self.work_parser.parse_work_experience(sections["work"])
        
        # Parse certification section
        if "certification" in sections:
            result["certifications"] = self.cert_parser.parse_certifications(sections["certification"])
        
        # Store other sections for LLM processing
        for section_name, section_text in sections.items():
            if section_name not in ["work", "certification"]:
                result["other_sections"][section_name] = section_text
        
        return result
    
    def _split_into_sections(self, text: str) -> Dict[str, str]:
        """Split resume text into logical sections"""
        sections = {}
        
        # Common section headers
        section_patterns = {
            "work": r"(?i)(work\s+experience|employment|experience|career|professional\s+experience)",
            "certification": r"(?i)(certifications|certificates|credentials|licenses)",
            "education": r"(?i)(education|academic|qualification|degree)",
            "skills": r"(?i)(skills|technical\s+skills|competencies)",
            "projects": r"(?i)(projects|portfolio|work\s+samples)",
            "summary": r"(?i)(summary|objective|profile|about)"
        }
        
        # Split text by major section breaks
        lines = text.split('\n')
        current_section = "other"
        current_content = []
        
        for line in lines:
            line_stripped = line.strip()
            
            # Check if this line is a section header
            section_found = None
            for section_name, pattern in section_patterns.items():
                if re.match(pattern, line_stripped):
                    section_found = section_name
                    break
            
            if section_found:
                # Save previous section
                if current_content:
                    sections[current_section] = '\n'.join(current_content).strip()
                
                # Start new section
                current_section = section_found
                current_content = [line_stripped]
            else:
                current_content.append(line_stripped)
        
        # Save last section
        if current_content:
            sections[current_section] = '\n'.join(current_content).strip()
        
        return sections
    
    def enhance_with_llm(self, parsed_data: Dict, llm_service) -> Dict:
        """Enhance parsed data with LLM service for missing information"""
        
        # Process work experience with LLM
        enhanced_work = []
        for exp in parsed_data["work_experience"]:
            if not exp["job_title"] or not exp["company"]:
                # Use LLM to extract missing information
                llm_result = llm_service.extract_structured_resume(exp["raw_text"])
                if llm_result:
                    exp.update(llm_result.get("work", [{}])[0])
            enhanced_work.append(exp)
        
        # Process certifications with LLM
        enhanced_certs = []
        for cert in parsed_data["certifications"]:
            if not cert["name"] or not cert["issuer"]:
                # Use LLM to extract missing information
                llm_result = llm_service.extract_structured_resume(cert["raw_text"])
                if llm_result:
                    cert.update(llm_result.get("certifications", [{}])[0])
            enhanced_certs.append(cert)
        
        return {
            "work_experience": enhanced_work,
            "certifications": enhanced_certs,
            "other_sections": parsed_data["other_sections"]
        }
    
    def generate_training_data(self, raw_resumes: List[str], ground_truth: List[Dict]) -> List[Dict]:
        """Generate training data for model improvement"""
        
        training_data = []
        
        for raw_resume, truth_data in zip(raw_resumes, ground_truth):
            # Parse with our enhanced parser
            parsed = self.parse_resume_sections(raw_resume)
            
            # Compare with ground truth
            training_entry = {
                "input": raw_resume,
                "parsed": parsed,
                "ground_truth": truth_data,
                "corrections": self._identify_corrections(parsed, truth_data)
            }
            
            training_data.append(training_entry)
        
        return training_data
    
    def _identify_corrections(self, parsed: Dict, truth: Dict) -> Dict:
        """Identify corrections needed between parsed and ground truth"""
        corrections = {
            "work_experience": [],
            "certifications": []
        }
        
        # Compare work experience
        for i, (parsed_exp, truth_exp) in enumerate(zip(parsed["work_experience"], truth.get("work", []))):
            exp_corrections = {}
            
            if parsed_exp.get("job_title") != truth_exp.get("job_title"):
                exp_corrections["job_title"] = {
                    "parsed": parsed_exp.get("job_title"),
                    "correct": truth_exp.get("job_title")
                }
            
            if parsed_exp.get("company") != truth_exp.get("company"):
                exp_corrections["company"] = {
                    "parsed": parsed_exp.get("company"),
                    "correct": truth_exp.get("company")
                }
            
            if exp_corrections:
                corrections["work_experience"].append({
                    "index": i,
                    "corrections": exp_corrections
                })
        
        # Compare certifications
        for i, (parsed_cert, truth_cert) in enumerate(zip(parsed["certifications"], truth.get("certifications", []))):
            cert_corrections = {}
            
            if parsed_cert.get("name") != truth_cert.get("name"):
                cert_corrections["name"] = {
                    "parsed": parsed_cert.get("name"),
                    "correct": truth_cert.get("name")
                }
            
            if parsed_cert.get("issuer") != truth_cert.get("issuer"):
                cert_corrections["issuer"] = {
                    "parsed": parsed_cert.get("issuer"),
                    "correct": truth_cert.get("issuer")
                }
            
            if cert_corrections:
                corrections["certifications"].append({
                    "index": i,
                    "corrections": cert_corrections
                })
        
        return corrections


def main():
    """Test the enhanced parser integration"""
    
    # Sample resume text
    resume_text = """
    JOHN DOE
    Senior Software Engineer
    
    WORK EXPERIENCE
    Senior Software Engineer
    Google
    Jan 2020 - Dec 2021
    
    • Developed scalable web applications using React and Node.js
    • Led team of 5 engineers on cloud migration project
    • Implemented CI/CD pipelines with Jenkins and Docker
    • Worked with AWS and Kubernetes for deployment
    
    CERTIFICATIONS
    AWS Certified Solutions Architect
    Amazon Web Services
    Issued: June 2023 Expires: June 2026
    ID: AWS-123456
    
    EDUCATION
    Bachelor of Science in Computer Science
    Stanford University
    2016-2020
    """
    
    # Initialize enhanced parser
    parser = EnhancedResumeParser()
    
    # Parse resume
    result = parser.parse_resume_sections(resume_text)
    
    # Output results
    print("Enhanced Resume Parser Results:")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
